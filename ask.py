"""CLI for quick RAG → LLM queries without the UI."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rag.config import CHAT_MODEL, EMBED_MODEL
from rag.pipeline import PlaywrightRAGBot


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Playwright RAG chatbot (CLI, LangChain)"
    )
    parser.add_argument("question", nargs="+", help="Question about Playwright testing")
    parser.add_argument("--model", default=CHAT_MODEL)
    parser.add_argument("--embed-model", default=EMBED_MODEL)
    parser.add_argument("--top-k", type=int, default=4)
    parser.add_argument("--rebuild-index", action="store_true")
    parser.add_argument("--json", action="store_true", help="Print full JSON result")
    args = parser.parse_args()

    question = " ".join(args.question)
    bot = PlaywrightRAGBot(
        model=args.model,
        embed_model=args.embed_model,
        top_k=args.top_k,
        rebuild_index=args.rebuild_index,
    )

    if not bot.llm.is_available():
        print(
            "Ollama is not reachable or model is missing. "
            f"Start Ollama and run: ollama pull {args.model}",
            file=sys.stderr,
        )
        return 1

    result = bot.ask(question)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(
            f"=== mode={result.get('mode')} "
            f"framework={result.get('framework')} "
            f"best={result.get('best_score')} "
            f"db={result.get('vector_db')} "
            f"chunks={result.get('indexed_chunks')} ==="
        )
        if not result["sources"]:
            print("(no sources)")
        for s in result["sources"]:
            print(f"- {s['title']} [{s['source']}] score={s['score']}")
        print("\n=== Answer ===")
        print(result["answer"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
