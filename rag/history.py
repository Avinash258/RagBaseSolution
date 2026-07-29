"""Q&A history store. Correct answers can be promoted into the vector DB."""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path

DEFAULT_HISTORY_PATH = Path(__file__).resolve().parent / "history" / "qa_history.jsonl"


class AnswerHistory:
    def __init__(self, path: Path | None = None) -> None:
        self.path = Path(path or DEFAULT_HISTORY_PATH)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(
        self,
        *,
        question: str,
        answer: str,
        mode: str,
        best_score: float = 0.0,
        sources: list | None = None,
        learned_markdown: str = "",
        correct: bool | None = None,
    ) -> dict:
        entry = {
            "id": uuid.uuid4().hex[:12],
            "ts": time.time(),
            "question": question,
            "answer": answer,
            "mode": mode,
            "best_score": best_score,
            "sources": sources or [],
            "learned_markdown": learned_markdown or "",
            "correct": correct,
            "saved_to_kb": False,
            "learned_file": "",
        }
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return entry

    def list_entries(self, limit: int = 50) -> list[dict]:
        if not self.path.exists():
            return []
        rows: list[dict] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return rows[-limit:]

    def get(self, entry_id: str) -> dict | None:
        for entry in self.list_entries(limit=10_000):
            if entry.get("id") == entry_id:
                return entry
        return None

    def mark_correct(self, entry_id: str, *, saved_to_kb: bool, learned_file: str = "") -> dict | None:
        if not self.path.exists():
            return None
        updated: dict | None = None
        lines = self.path.read_text(encoding="utf-8").splitlines()
        out: list[str] = []
        for line in lines:
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                out.append(line)
                continue
            if row.get("id") == entry_id:
                row["correct"] = True
                row["saved_to_kb"] = saved_to_kb
                row["learned_file"] = learned_file
                updated = row
            out.append(json.dumps(row, ensure_ascii=False))
        self.path.write_text("\n".join(out) + ("\n" if out else ""), encoding="utf-8")
        return updated

    def pending_correctable(self, limit: int = 20) -> list[dict]:
        """Entries from LLM/web that are not yet saved to the knowledge base."""
        rows = []
        for entry in reversed(self.list_entries(limit=200)):
            if entry.get("saved_to_kb"):
                continue
            if entry.get("mode") in {"rag"}:
                continue
            rows.append(entry)
            if len(rows) >= limit:
                break
        return rows
