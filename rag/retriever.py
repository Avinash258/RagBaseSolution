"""ChromaDB vector retriever over Playwright knowledge chunks."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

import chromadb
from chromadb.config import Settings

from rag.embeddings import OllamaEmbedder

COLLECTION_NAME = "playwright_knowledge"
DEFAULT_PERSIST_DIR = Path(__file__).resolve().parent / "chroma_db"
# Bump when chunking logic changes so stale indexes rebuild automatically
CHUNKER_VERSION = "3-nomic-prefix"


@dataclass
class Chunk:
    id: str
    source: str
    title: str
    text: str


class ChromaRetriever:
    """Persistent vector DB retriever (Chroma + Ollama embeddings)."""

    def __init__(
        self,
        knowledge_dir: Path,
        persist_dir: Path | None = None,
        embed_model: str = "nomic-embed-text",
        rebuild: bool = False,
        auto_rebuild: bool = False,
    ) -> None:
        self.knowledge_dir = Path(knowledge_dir)
        self.persist_dir = Path(persist_dir or DEFAULT_PERSIST_DIR)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.embedder = OllamaEmbedder(model=embed_model)
        self.chunks: list[Chunk] = []

        self._client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=Settings(anonymized_telemetry=False),
        )
        self._collection = self._bind_collection()
        # auto_rebuild=False keeps Streamlit startup fast; use sidebar Rebuild button
        self._ensure_index(rebuild=rebuild, auto_rebuild=auto_rebuild)

    def _bind_collection(self):
        """Attach to the named collection (fresh handle after external rebuilds)."""
        return self._client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    def refresh_collection(self):
        """Re-bind after another process deleted/recreated the collection."""
        self._collection = self._bind_collection()
        return self._collection

    @property
    def count(self) -> int:
        try:
            return self._collection.count()
        except Exception as exc:  # noqa: BLE001
            # Stale UUID after ingest/reindex while Streamlit kept the old handle
            if "does not exist" not in str(exc).lower() and type(exc).__name__ != "NotFoundError":
                raise
            self.refresh_collection()
            return self._collection.count()

    def _ensure_index(self, rebuild: bool = False, auto_rebuild: bool = False) -> None:
        """
        Attach to the existing Chroma collection.

        Full re-embed only when:
        - rebuild=True (explicit), or
        - collection is empty, or
        - auto_rebuild=True and knowledge fingerprint/count drifted

        Default auto_rebuild=False so Streamlit `get_bot()` never hangs for minutes.
        """
        try:
            current_count = self._collection.count()
        except Exception as exc:  # noqa: BLE001
            if "does not exist" in str(exc).lower() or type(exc).__name__ == "NotFoundError":
                self.refresh_collection()
                current_count = self._collection.count()
            else:
                raise

        if rebuild or current_count == 0:
            self.rebuild()
            return

        if not auto_rebuild:
            # Fast path: use whatever is already indexed
            self.chunks = []
            return

        self.chunks = load_chunks(self.knowledge_dir)
        if not self.chunks:
            raise FileNotFoundError(
                f"No knowledge files found in {self.knowledge_dir}"
            )

        fingerprint = knowledge_fingerprint(self.knowledge_dir, self.embedder.model)
        meta_path = self.persist_dir / "index_meta.json"
        previous = {}
        if meta_path.exists():
            previous = json.loads(meta_path.read_text(encoding="utf-8"))

        needs_rebuild = (
            current_count != len(self.chunks)
            or previous.get("fingerprint") != fingerprint
        )
        if needs_rebuild:
            self.rebuild()

    def _write_meta(self) -> None:
        fingerprint = knowledge_fingerprint(self.knowledge_dir, self.embedder.model)
        meta = {
            "fingerprint": fingerprint,
            "chunk_count": self.count,
            "embed_model": self.embedder.model,
            "collection": COLLECTION_NAME,
        }
        (self.persist_dir / "index_meta.json").write_text(
            json.dumps(meta, indent=2),
            encoding="utf-8",
        )

    def rebuild(self) -> int:
        """Re-embed all knowledge chunks into ChromaDB."""
        if not self.embedder.is_available():
            raise RuntimeError(
                f"Embedding model '{self.embedder.model}' is not available in Ollama. "
                f"Run: ollama pull {self.embedder.model}"
            )

        # Drop and recreate for a clean rebuild
        try:
            self._client.delete_collection(COLLECTION_NAME)
        except Exception:  # noqa: BLE001
            pass
        self._collection = self._bind_collection()

        self.chunks = load_chunks(self.knowledge_dir)
        ids = [c.id for c in self.chunks]
        documents = [c.text for c in self.chunks]
        metadatas = [
            {"source": c.source, "title": c.title}
            for c in self.chunks
        ]
        embeddings = self.embedder.embed_many(documents, kind="document")

        self._collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
        )
        self._write_meta()
        return len(self.chunks)

    def retrieve(
        self,
        query: str,
        top_k: int = 4,
        min_score: float = 0.2,
    ) -> list[tuple[Chunk, float]]:
        try:
            n = self._collection.count()
        except Exception as exc:  # noqa: BLE001
            if "does not exist" in str(exc).lower() or type(exc).__name__ == "NotFoundError":
                self.refresh_collection()
                n = self._collection.count()
            else:
                raise
        if n == 0:
            return []

        query_embedding = self.embedder.embed(query, kind="query")
        result = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, n),
            include=["documents", "metadatas", "distances"],
        )

        ids = (result.get("ids") or [[]])[0]
        documents = (result.get("documents") or [[]])[0]
        metadatas = (result.get("metadatas") or [[]])[0]
        distances = (result.get("distances") or [[]])[0]

        hits: list[tuple[Chunk, float]] = []
        for doc_id, document, metadata, distance in zip(
            ids, documents, metadatas, distances, strict=False
        ):
            # cosine distance -> similarity
            score = 1.0 - float(distance)
            if score < min_score:
                continue
            meta = metadata or {}
            hits.append(
                (
                    Chunk(
                        id=doc_id,
                        source=str(meta.get("source", "")),
                        title=str(meta.get("title", "")),
                        text=document or "",
                    ),
                    score,
                )
            )
        return hits

    def add_learned_chunks(self, chunks: list[Chunk]) -> int:
        """Incrementally embed and upsert newly learned web knowledge."""
        if not chunks:
            return 0
        self.refresh_collection()
        ids = [c.id for c in chunks]
        documents = [c.text for c in chunks]
        metadatas = [{"source": c.source, "title": c.title} for c in chunks]
        embeddings = self.embedder.embed_many(documents, kind="document")

        # Upsert so re-learning the same question replaces old vectors
        try:
            self._collection.delete(ids=ids)
        except Exception:  # noqa: BLE001
            pass
        self._collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
        )
        self.chunks.extend(chunks)
        self._write_meta()
        return len(chunks)

    def learn_from_markdown(self, path: Path) -> list[Chunk]:
        """Chunk a markdown file and add it to Chroma without full rebuild."""
        path = Path(path)
        raw = path.read_text(encoding="utf-8")
        sections = split_markdown_sections(raw, path.stem)
        new_chunks: list[Chunk] = []
        idx = 0
        for title, body in sections:
            for piece in split_long_text(body, MAX_CHUNK_CHARS):
                text = f"{title}\n{piece}".strip()
                if len(text) < 40:
                    continue
                new_chunks.append(
                    Chunk(
                        id=f"{path.stem}-{idx}",
                        source=path.name,
                        title=title,
                        text=text,
                    )
                )
                idx += 1
        self.add_learned_chunks(new_chunks)
        return new_chunks


MAX_CHUNK_CHARS = 1400


def load_chunks(knowledge_dir: Path) -> list[Chunk]:
    chunks: list[Chunk] = []
    if not knowledge_dir.exists():
        return chunks

    for path in sorted(knowledge_dir.glob("*.md")):
        raw = path.read_text(encoding="utf-8")
        sections = split_markdown_sections(raw, path.stem)
        idx = 0
        for title, body in sections:
            for piece in split_long_text(body, MAX_CHUNK_CHARS):
                text = f"{title}\n{piece}".strip()
                if len(text) < 40:
                    continue
                chunks.append(
                    Chunk(
                        id=f"{path.stem}-{idx}",
                        source=path.name,
                        title=title,
                        text=text,
                    )
                )
                idx += 1
    return chunks


def split_long_text(text: str, max_chars: int) -> list[str]:
    text = text.strip()
    if len(text) <= max_chars:
        return [text] if text else []
    parts: list[str] = []
    paragraphs = text.split("\n\n")
    buf: list[str] = []
    size = 0
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        extra = len(para) + (2 if buf else 0)
        if buf and size + extra > max_chars:
            parts.append("\n\n".join(buf))
            buf = [para]
            size = len(para)
        else:
            buf.append(para)
            size += extra
    if buf:
        parts.append("\n\n".join(buf))
    # Hard-split any oversized leftover paragraph
    final: list[str] = []
    for part in parts:
        if len(part) <= max_chars:
            final.append(part)
            continue
        for i in range(0, len(part), max_chars):
            final.append(part[i : i + max_chars])
    return final


HEADING_RE = re.compile(r"^#{1,6}\s+(?P<title>.+?)\s*#*\s*$")


def clean_text(text: str) -> str:
    """Strip zero-width and non-breaking characters that pollute titles."""
    for ch in ("\u200b", "\u200c", "\u200d", "\ufeff"):
        text = text.replace(ch, "")
    return text.replace("\u00a0", " ").strip()


def split_markdown_sections(raw: str, fallback_title: str) -> list[tuple[str, str]]:
    raw = clean_text(raw)
    lines = raw.splitlines()
    sections: list[tuple[str, str]] = []
    current_title = fallback_title.replace("_", " ").title()
    current_body: list[str] = []
    in_code_block = False

    def flush() -> None:
        nonlocal current_body
        body = "\n".join(current_body).strip()
        if body:
            sections.append((current_title, body))
        current_body = []

    for line in lines:
        if line.lstrip().startswith("```"):
            in_code_block = not in_code_block
            current_body.append(line)
            continue

        match = None if in_code_block else HEADING_RE.match(line)
        if match:
            flush()
            current_title = clean_text(match.group("title")) or current_title
        else:
            current_body.append(line)
    flush()
    return sections


def knowledge_fingerprint(knowledge_dir: Path, embed_model: str) -> str:
    hasher = hashlib.sha256()
    hasher.update(CHUNKER_VERSION.encode("utf-8"))
    hasher.update(embed_model.encode("utf-8"))
    for path in sorted(Path(knowledge_dir).glob("*.md")):
        hasher.update(path.name.encode("utf-8"))
        hasher.update(path.read_bytes())
    return hasher.hexdigest()
