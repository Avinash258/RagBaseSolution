"""Force google_learn path with an off-catalog phrasing."""

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
    # Force miss by temporarily raising threshold
    bot.rag_min_score = 0.99
    before = bot.retriever.count
    q = "How do I screenshot a full page in Playwright?"
    t0 = time.time()
    result = bot.ask(q)
    print(
        f"mode={result['mode']} engine={result.get('web_engine')} "
        f"trained={result.get('trained')} n={result.get('trained_chunks')} "
        f"secs={time.time()-t0:.1f} before={before} after={result['indexed_chunks']}"
    )
    print(safe(result["answer"])[:700])
    print("file", result.get("learned_file"))
    return 0 if result["mode"] == "google_learn" and result.get("trained") else 1


if __name__ == "__main__":
    raise SystemExit(main())
