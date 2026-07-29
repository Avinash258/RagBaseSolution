"""Smoke-test satisfaction-gated web learn + optional KB train."""

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

    q = "give me sample code for mocking API with page.route"
    t0 = time.time()
    first = bot.ask(q)
    print(
        f"first mode={first['mode']} can_search_web={first.get('can_search_web')} "
        f"secs={time.time()-t0:.1f}"
    )

    t0 = time.time()
    result = bot.ask_internet(q, prior_best=float(first.get("best_score") or 0.0))
    elapsed = time.time() - t0
    print(
        f"internet mode={result['mode']} engine={result.get('web_engine')} "
        f"can_save={result.get('can_save_to_kb')} secs={elapsed:.1f}"
    )
    print(f"indexed now: {result['indexed_chunks']} (was {before})")
    print(safe(result["answer"])[:500])
    print("sources:", [safe(s["title"]) for s in result["sources"][:3]])

    again = bot.ask(q)
    print(f"\nsecond ask mode={again['mode']} best={again['best_score']}")
    return 0 if result["mode"] in {"internet", "none"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
