"""Offline tests for mode registry and reconcile prompt building."""

from rag.agents.reconcile import _build_prompt
from rag.agents.specialists import AGENT_CLASSES
from rag.modes import MODE_SPECS, list_modes


def test_eight_modes_and_agents_aligned():
    modes = list_modes()
    assert len(modes) == 8
    assert set(MODE_SPECS) == set(AGENT_CLASSES)


def test_reconcile_prompt_includes_drafts():
    prompt = _build_prompt(
        "How to mock APIs?",
        [
            {"label": "A", "content": "Use page.route"},
            {"label": "B", "answer": "Use route.fulfill"},
        ],
    )
    assert "page.route" in prompt
    assert "route.fulfill" in prompt
    assert "How to mock APIs?" in prompt
