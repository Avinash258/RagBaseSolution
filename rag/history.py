"""Q&A history store. Correct answers can be promoted into the vector DB."""

from __future__ import annotations

import json
import time
import uuid
from pathlib import Path

from rag.config import TRAINABLE_MODES

DEFAULT_HISTORY_PATH = Path(__file__).resolve().parent / "history" / "qa_history.jsonl"


class AnswerHistory:
    def __init__(self, path: Path | None = None) -> None:
        self.path = Path(path or DEFAULT_HISTORY_PATH)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._count_cache: int | None = None

    def count(self) -> int:
        """Lightweight entry count (cached until writes)."""
        if self._count_cache is not None:
            return self._count_cache
        if not self.path.exists():
            self._count_cache = 0
            return 0
        n = 0
        with self.path.open("r", encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    n += 1
        self._count_cache = n
        return n

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
        if self._count_cache is not None:
            self._count_cache += 1
        else:
            self._count_cache = None
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

    def _rewrite(self, mutator) -> dict | None:
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
            changed = mutator(row)
            if changed is not None:
                row = changed
                updated = row
            out.append(json.dumps(row, ensure_ascii=False))
        self.path.write_text("\n".join(out) + ("\n" if out else ""), encoding="utf-8")
        return updated

    def mark_correct(
        self, entry_id: str, *, saved_to_kb: bool, learned_file: str = ""
    ) -> dict | None:
        def mut(row: dict):
            if row.get("id") != entry_id:
                return None
            row["correct"] = True
            row["saved_to_kb"] = saved_to_kb
            row["learned_file"] = learned_file
            return row

        return self._rewrite(mut)

    def set_feedback(
        self,
        entry_id: str,
        *,
        rating: str,
        comment: str = "",
    ) -> dict | None:
        """Persist user feedback on an answer (helpful / not_helpful)."""
        rating = (rating or "").strip().lower()
        if rating not in {"helpful", "not_helpful"}:
            return None

        def mut(row: dict):
            if row.get("id") != entry_id:
                return None
            row["feedback"] = {
                "rating": rating,
                "comment": (comment or "").strip()[:1000],
                "ts": time.time(),
            }
            return row

        return self._rewrite(mut)

    def pending_correctable(self, limit: int = 20) -> list[dict]:
        """Trainable LLM/web entries not yet saved to the knowledge base."""
        rows = []
        for entry in reversed(self.list_entries(limit=200)):
            if entry.get("saved_to_kb"):
                continue
            if entry.get("mode") not in TRAINABLE_MODES:
                continue
            if not (entry.get("learned_markdown") or "").strip():
                continue
            rows.append(entry)
            if len(rows) >= limit:
                break
        return rows
