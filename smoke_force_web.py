"""Force internet path via ask_internet (satisfaction-gated flow)."""

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
    bot.rag_min_score = 0.99
    before = bot.retriever.count
    q = "How do I screenshot a full page in Playwright?"

    # First ask stays local (no auto-internet)
    first = bot.ask(q)
    print(f"first mode={first['mode']} can_search_web={first.get('can_search_web')}")

    t0 = time.time()
    result = bot.ask_internet(q, prior_best=float(first.get("best_score") or 0.0))
    print(
        f"internet mode={result['mode']} engine={result.get('web_engine')} "
        f"can_save={result.get('can_save_to_kb')} "
        f"secs={time.time()-t0:.1f} before={before} after={result['indexed_chunks']}"
    )
    print(safe(result["answer"])[:700])
    ok = result["mode"] == "internet" or (
        result["mode"] == "none" and not result.get("can_save_to_kb")
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
