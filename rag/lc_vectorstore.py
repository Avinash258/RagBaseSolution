"""LangChain-facing vector store helpers over existing ChromaRetriever."""

from __future__ import annotations

from pathlib import Path

from langchain_core.documents import Document

from rag.config import EMBED_MODEL, RETRIEVE_MIN_SCORE, TOP_K
from rag.retriever import Chunk, ChromaRetriever


def build_retriever(
    knowledge_dir: Path,
    *,
    embed_model: str = EMBED_MODEL,
    rebuild: bool = False,
) -> ChromaRetriever:
    """Reuse the project Chroma index (keeps cosine similarity scores)."""
    return ChromaRetriever(
        knowledge_dir=knowledge_dir,
        embed_model=embed_model,
        rebuild=rebuild,
        auto_rebuild=False,
    )


def hits_to_documents(
    hits: list[tuple[Chunk, float]],
) -> list[Document]:
    docs: list[Document] = []
    for chunk, score in hits:
        docs.append(
            Document(
                page_content=chunk.text,
                metadata={
                    "id": chunk.id,
                    "source": chunk.source,
                    "title": chunk.title,
                    "score": float(score),
                },
            )
        )
    return docs


def retrieve_documents(
    retriever: ChromaRetriever,
    question: str,
    *,
    top_k: int = TOP_K,
    min_score: float = RETRIEVE_MIN_SCORE,
) -> list[tuple[Document, float]]:
    hits = retriever.retrieve(question, top_k=top_k, min_score=min_score)
    return [(doc, float(doc.metadata.get("score", 0.0))) for doc in hits_to_documents(hits)]


def chunk_hits_to_sources(hits: list[tuple[Chunk, float]]) -> list[dict]:
    sources = []
    for i, (chunk, score) in enumerate(hits, start=1):
        sources.append(
            {
                "n": i,
                "id": chunk.id,
                "source": chunk.source,
                "url": "",
                "title": chunk.title,
                "score": round(score, 4),
                "preview": chunk.text[:220].replace("\n", " "),
                "text": chunk.text,
            }
        )
    return sources
