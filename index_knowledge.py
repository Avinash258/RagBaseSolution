"""Build / rebuild the ChromaDB vector index for Playwright knowledge."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rag.retriever import ChromaRetriever


def main() -> int:
    parser = argparse.ArgumentParser(description="Index Playwright docs into ChromaDB")
    parser.add_argument(
        "--knowledge-dir",
        type=Path,
        default=ROOT / "rag" / "knowledge",
    )
    parser.add_argument("--embed-model", default="nomic-embed-text")
    parser.add_argument(
        "--persist-dir",
        type=Path,
        default=ROOT / "rag" / "chroma_db",
    )
    args = parser.parse_args()

    print(f"Knowledge dir : {args.knowledge_dir}")
    print(f"Persist dir   : {args.persist_dir}")
    print(f"Embed model   : {args.embed_model}")
    print("Building vector index...")

    retriever = ChromaRetriever(
        knowledge_dir=args.knowledge_dir,
        persist_dir=args.persist_dir,
        embed_model=args.embed_model,
        rebuild=True,
    )
    print(f"Indexed {retriever.count} chunks into ChromaDB collection 'playwright_knowledge'.")

    sample = "How do I use getByRole locators?"
    hits = retriever.retrieve(sample, top_k=3)
    print(f"\nSample query: {sample}")
    for chunk, score in hits:
        print(f"  - {chunk.title} [{chunk.source}] score={score:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
