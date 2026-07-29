"""LangChain-oriented ingest helpers for Playwright markdown knowledge."""

from __future__ import annotations

from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from rag.retriever import ChromaRetriever, Chunk, MAX_CHUNK_CHARS


def markdown_to_documents(path: Path) -> list[Document]:
    path = Path(path)
    raw = path.read_text(encoding="utf-8")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=MAX_CHUNK_CHARS,
        chunk_overlap=120,
        separators=["\n## ", "\n### ", "\n\n", "\n", " "],
    )
    pieces = splitter.split_text(raw)
    docs: list[Document] = []
    for i, text in enumerate(pieces):
        text = text.strip()
        if len(text) < 40:
            continue
        title = path.stem.replace("_", " ").title()
        first_line = text.splitlines()[0].lstrip("# ").strip()
        if first_line:
            title = first_line[:120]
        docs.append(
            Document(
                page_content=text,
                metadata={
                    "source": path.name,
                    "title": title,
                    "id": f"{path.stem}-lc-{i}",
                },
            )
        )
    return docs


def documents_to_chunks(docs: list[Document]) -> list[Chunk]:
    chunks: list[Chunk] = []
    for doc in docs:
        meta = doc.metadata or {}
        chunks.append(
            Chunk(
                id=str(meta.get("id") or meta.get("source", "doc")),
                source=str(meta.get("source", "")),
                title=str(meta.get("title", "")),
                text=doc.page_content,
            )
        )
    return chunks


def ingest_markdown_file(retriever: ChromaRetriever, path: Path) -> list[Chunk]:
    """Chunk via LangChain splitter and upsert into the existing Chroma index."""
    docs = markdown_to_documents(path)
    chunks = documents_to_chunks(docs)
    # Ensure unique ids if splitter produced duplicates
    fixed: list[Chunk] = []
    for i, c in enumerate(chunks):
        fixed.append(
            Chunk(
                id=f"{Path(path).stem}-lc-{i}",
                source=c.source or Path(path).name,
                title=c.title,
                text=c.text,
            )
        )
    retriever.add_learned_chunks(fixed)
    return fixed
