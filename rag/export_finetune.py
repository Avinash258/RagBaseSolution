"""Export Correct / saved history into a fine-tuning JSONL dataset."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rag.history import AnswerHistory, DEFAULT_HISTORY_PATH


def export_finetune_jsonl(
    history_path: Path,
    out_path: Path,
    *,
    only_correct: bool = True,
    include_saved: bool = True,
    min_answer_chars: int = 40,
) -> int:
    """
    Write Alpaca-style JSONL rows:
      {"instruction": "...", "input": "", "output": "...", "id": "..."}
    """
    history = AnswerHistory(path=history_path)
    rows = history.list_entries(limit=50_000)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with out_path.open("w", encoding="utf-8") as fh:
        for entry in rows:
            if only_correct:
                ok = entry.get("correct") is True or (
                    include_saved and entry.get("saved_to_kb")
                )
                if not ok:
                    continue
            question = (entry.get("question") or "").strip()
            answer = (entry.get("answer") or "").strip()
            if len(question) < 5 or len(answer) < min_answer_chars:
                continue
            # Strip UI footnotes that should not be trained
            if "_Saved to history" in answer:
                answer = answer.split("_Saved to history")[0].strip()
            record = {
                "id": entry.get("id"),
                "instruction": (
                    "You are a Playwright testing assistant. "
                    "Answer with practical TypeScript/@playwright/test guidance."
                ),
                "input": question,
                "output": answer,
                "mode": entry.get("mode"),
            }
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
            written += 1
    return written


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export chatbot history for LoRA fine-tuning"
    )
    parser.add_argument(
        "--history",
        type=Path,
        default=DEFAULT_HISTORY_PATH,
        help="Path to qa_history.jsonl",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("rag/finetune/playwright_sft.jsonl"),
        help="Output JSONL path",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Export all history (not only Correct/saved)",
    )
    args = parser.parse_args()
    n = export_finetune_jsonl(
        args.history,
        args.out,
        only_correct=not args.all,
    )
    print(f"Wrote {n} examples → {args.out}")
    if n < 100:
        print(
            "Tip: fine-tuning works better with 100+ high-quality Correct answers."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
