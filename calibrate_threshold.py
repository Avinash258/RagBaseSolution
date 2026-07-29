"""Measure vector scores for on-topic vs off-topic questions.

Used to pick the RAG-vs-LLM fallback threshold.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rag.retriever import ChromaRetriever

ON_TOPIC = [
    "How do I install Playwright with npm?",
    "How to mock API responses with page.route?",
    "What is the Page Object Model?",
    "How do I use getByRole locators?",
    "How do soft assertions work?",
    "How do I reuse login state between tests?",
    "How do I run tests in CI with GitHub Actions?",
    "What does trace viewer show?",
    "How do I handle iframes?",
    "How to upload a file in a test?",
]
OFF_TOPIC = [
    "Explain how to bake sourdough bread on Mars",
    "What is the capital of France?",
    "Write a poem about autumn rain",
    "How do I change the oil in my car?",
    "What are good stretches for lower back pain?",
    "Summarize the plot of Hamlet",
]


def main() -> int:
    retriever = ChromaRetriever(ROOT / "rag" / "knowledge")
    print(f"indexed chunks: {retriever.count}\n")

    def best_score(question: str) -> float:
        hits = retriever.retrieve(question, top_k=3, min_score=0.0)
        return hits[0][1] if hits else 0.0

    on_scores = []
    print("ON-TOPIC")
    for q in ON_TOPIC:
        score = best_score(q)
        on_scores.append(score)
        print(f"  {score:.3f}  {q}")

    off_scores = []
    print("\nOFF-TOPIC")
    for q in OFF_TOPIC:
        score = best_score(q)
        off_scores.append(score)
        print(f"  {score:.3f}  {q}")

    lo_on = min(on_scores)
    hi_off = max(off_scores)
    print(f"\nlowest on-topic : {lo_on:.3f}")
    print(f"highest off-topic: {hi_off:.3f}")
    if lo_on > hi_off:
        print(f"suggested threshold: {(lo_on + hi_off) / 2:.2f}")
    else:
        print("scores overlap — a lexical guard is needed alongside the threshold")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
