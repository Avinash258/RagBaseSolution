"""Smoke test: RAG fast path and local-LLM fallback (no auto-internet)."""

from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rag.pipeline import PlaywrightRAGBot

RAG_QUESTIONS = [
    "How do I install Playwright with npm?",
    "How to mock API responses with page.route?",
    "What is the Page Object Model?",
    "How do I use getByRole locators?",
]
FALLBACK_QUESTION = "Explain how to bake sourdough bread on Mars"


def safe(text: str) -> str:
    return text.encode("ascii", "ignore").decode()


def main() -> int:
    bot = PlaywrightRAGBot(top_k=3)
    print(f"indexed chunks: {bot.retriever.count}")
    print(f"rag threshold : {bot.rag_min_score}\n")

    failures = 0
    for question in RAG_QUESTIONS:
        started = time.time()
        result = bot.ask(question)
        elapsed = time.time() - started
        titles = [safe(s["title"])[:32] for s in result["sources"][:2]]
        print(
            f"[{result['mode']:12s}] best={result['best_score']:.3f} "
            f"{elapsed:5.2f}s  {safe(question)}"
        )
        print(f"    sources: {titles}")
        if result["mode"] != "rag":
            failures += 1
            print("    WARNING: expected RAG fast path")

    print(f"\nFallback check: {FALLBACK_QUESTION}")
    started = time.time()
    result = bot.ask(FALLBACK_QUESTION)
    elapsed = time.time() - started
    print(
        f"[{result['mode']:12s}] best={result['best_score']:.3f} {elapsed:5.2f}s"
    )
    print(f"    answer: {safe(result['answer'])[:160]}")
    if result["mode"] not in {"llm", "llm_grounded", "none"}:
        failures += 1
        print("    WARNING: expected local LLM / none (internet is satisfaction-gated)")
    if result.get("can_search_web") is not True and result["mode"] != "rag":
        # none/llm should offer web search
        if result["mode"] in {"llm", "llm_grounded", "none"} and not result.get(
            "can_search_web"
        ):
            failures += 1
            print("    WARNING: expected can_search_web=True")

    print("\nRESULT:", "PASS" if failures == 0 else f"FAIL ({failures})")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
