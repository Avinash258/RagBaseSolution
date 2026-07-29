"""Smoke-test web learn + vector train path."""

from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from rag.pipeline import PlaywrightRAGBot


def safe(text: str) -> str:
    return (text or "").encode("ascii", "ignore").decode()


def main() -> int:
    bot = PlaywrightRAGBot(top_k=3)
    before = bot.retriever.count
    print(f"chunks before: {before}")

    # Vague question that should miss RAG (like the screenshot)
    q = "give me sample code for mocking API with page.route"
    t0 = time.time()
    result = bot.ask(q)
    elapsed = time.time() - t0
    print(f"mode={result['mode']} engine={result.get('web_engine')} trained={result.get('trained')} chunks={result.get('trained_chunks')} secs={elapsed:.1f}")
    print(f"indexed now: {result['indexed_chunks']} (was {before})")
    print(safe(result["answer"])[:500])
    print("sources:", [safe(s["title"]) for s in result["sources"][:3]])

    # Ask again — should hopefully hit RAG now from learned content
    t0 = time.time()
    again = bot.ask(q)
    print(f"\nsecond ask mode={again['mode']} best={again['best_score']} secs={time.time()-t0:.2f}")
    return 0 if result["mode"] in {"google_learn", "rag"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
