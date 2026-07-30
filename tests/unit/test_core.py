from __future__ import annotations

from pathlib import Path

from rag.history import AnswerHistory
from rag.security import (
    escape_html,
    has_trainable_body,
    is_trainable_url,
    redact_secrets,
)
from rag.web_search import learned_filename
from rag.retriever import split_long_text, split_markdown_sections
from rag.lc_pipeline import _is_proper_llm_answer


def test_learned_filename_slug():
    name = learned_filename("How do I use getByRole?")
    assert name.startswith("web_learned_")
    assert name.endswith(".md")


def test_split_markdown_sections():
    raw = "# Title\n\nHello\n\n## Next\n\nBody"
    parts = split_markdown_sections(raw, "fallback")
    assert len(parts) >= 2
    assert parts[0][0]


def test_split_long_text():
    text = ("para one.\n\n" * 40) + "end"
    pieces = split_long_text(text, 80)
    assert len(pieces) > 1
    assert all(len(p) <= 80 or "\n\n" not in p for p in pieces[:3])


def test_history_append_feedback_and_pending(tmp_path: Path):
    path = tmp_path / "qa.jsonl"
    hist = AnswerHistory(path=path)
    entry = hist.append(
        question="Q?",
        answer="A" * 50,
        mode="llm",
        learned_markdown="# Learned\n\n" + ("x" * 100),
    )
    assert hist.count() == 1
    assert hist.get(entry["id"])["question"] == "Q?"

    saved = hist.set_feedback(entry["id"], rating="helpful", comment="nice")
    assert saved and saved["feedback"]["rating"] == "helpful"

    hist.append(
        question="none",
        answer="no answer",
        mode="none",
        learned_markdown="",
    )
    pending = hist.pending_correctable(limit=10)
    assert all(
        p["mode"]
        in {"llm", "llm_grounded", "internet", "agent", "reconciled"}
        for p in pending
    )
    assert all((p.get("learned_markdown") or "").strip() for p in pending)


def test_mark_correct(tmp_path: Path):
    path = tmp_path / "qa.jsonl"
    hist = AnswerHistory(path=path)
    entry = hist.append(question="Q", answer="A", mode="internet")
    updated = hist.mark_correct(entry["id"], saved_to_kb=True, learned_file="x.md")
    assert updated["saved_to_kb"] is True
    assert updated["learned_file"] == "x.md"


def test_escape_and_redact():
    assert "&lt;script&gt;" in escape_html("<script>")
    assert "[REDACTED]" in redact_secrets("Authorization: Bearer abc.def-ghi")
    assert not has_trainable_body("short")
    assert has_trainable_body("# Title\n\n" + ("Playwright locator guidance. " * 10))
    assert is_trainable_url(
        "https://playwright.dev/docs/mock", {"playwright.dev"}
    )


def test_is_proper_llm_answer():
    assert not _is_proper_llm_answer("no")
    assert not _is_proper_llm_answer("I do not know how to help with that")
    assert _is_proper_llm_answer(
        "Use page.getByRole('button', { name: 'Submit' }) in Playwright."
    )
