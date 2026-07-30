"""Mode registry for the Multi-mode Testing Hub."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

KNOWLEDGE_ROOT = Path(__file__).resolve().parent / "knowledge"
MODES_ROOT = KNOWLEDGE_ROOT / "modes"


@dataclass(frozen=True)
class ModeSpec:
    id: str
    label: str
    description: str
    knowledge_subdir: str  # relative to knowledge root; "" = playwright root
    allow_web: bool = False
    supports_rag: bool = True
    suggestions: tuple[str, ...] = field(default_factory=tuple)
    related_modes: tuple[str, ...] = field(default_factory=tuple)


MODE_SPECS: dict[str, ModeSpec] = {
    "playwright_kb": ModeSpec(
        id="playwright_kb",
        label="AI KB for Playwright testing",
        description="Vector DB + coding LLM for Playwright automation Q&A.",
        knowledge_subdir="",
        allow_web=True,
        supports_rag=True,
        suggestions=(
            "How do I use getByRole locators?",
            "Mock an API with page.route",
            "Reuse login with storageState",
            "Debug flaky tests with Trace Viewer",
        ),
        related_modes=("manual_cases", "test_strategy"),
    ),
    "synthetic_data": ModeSpec(
        id="synthetic_data",
        label="Synthetic test data agent",
        description="Generate realistic fixtures and anonymized test data.",
        knowledge_subdir="modes/synthetic_data",
        suggestions=(
            "Generate 10 user personas for an e-commerce checkout",
            "Create boundary values for a date-of-birth field",
            "Suggest fixture JSON for login API tests",
        ),
        related_modes=("manual_cases", "estimation"),
    ),
    "manual_cases": ModeSpec(
        id="manual_cases",
        label="Manual test case generation",
        description="Turn requirements into structured manual test cases.",
        knowledge_subdir="modes/manual_cases",
        suggestions=(
            "Write manual cases for password reset",
            "Generate negative cases for checkout payment",
            "Create smoke suite for admin user management",
        ),
        related_modes=("test_strategy", "defect_lifecycle"),
    ),
    "test_strategy": ModeSpec(
        id="test_strategy",
        label="KB Test Strategy template",
        description="Draft test strategy / plan sections from context.",
        knowledge_subdir="modes/test_strategy",
        suggestions=(
            "Outline a test strategy for a banking web app",
            "What risks should a regression strategy cover?",
            "Template entry/exit criteria for UAT",
        ),
        related_modes=("estimation", "agile"),
    ),
    "estimation": ModeSpec(
        id="estimation",
        label="Estimation",
        description="Estimate testing effort, sizing, and staffing hints.",
        knowledge_subdir="modes/estimation",
        suggestions=(
            "Estimate effort for 40 API endpoints automation",
            "How to size exploratory testing for a release?",
            "Break down hours for accessibility testing",
        ),
        related_modes=("test_strategy", "agile"),
    ),
    "agile": ModeSpec(
        id="agile",
        label="Agile",
        description="Scrum/Kanban testing practices and ceremonies.",
        knowledge_subdir="modes/agile",
        suggestions=(
            "How should QA work in a 2-week sprint?",
            "Definition of Done checklist for stories",
            "Shift-left ideas for daily stand-ups",
        ),
        related_modes=("test_strategy", "defect_lifecycle"),
    ),
    "defect_lifecycle": ModeSpec(
        id="defect_lifecycle",
        label="Defect life cycle",
        description="Bug triage, severity, and lifecycle guidance.",
        knowledge_subdir="modes/defect_lifecycle",
        suggestions=(
            "Suggest severity for a payment double-charge bug",
            "Defect lifecycle states for Jira",
            "Triage checklist for production incidents",
        ),
        related_modes=("manual_cases", "agile"),
    ),
    "workflow_diagram": ModeSpec(
        id="workflow_diagram",
        label="Workflow diagram from requirements",
        description="Paste requirements → Mermaid application workflow.",
        knowledge_subdir="modes/workflow_diagram",
        supports_rag=True,
        suggestions=(
            "User registers, verifies email, then logs in to dashboard",
            "Checkout: cart → address → payment → confirmation",
            "Admin approves seller listing then publishes to storefront",
        ),
        related_modes=("manual_cases", "test_strategy"),
    ),
}


def list_modes() -> list[ModeSpec]:
    return list(MODE_SPECS.values())


def get_mode(mode_id: str) -> ModeSpec:
    if mode_id not in MODE_SPECS:
        raise KeyError(f"Unknown mode: {mode_id}")
    return MODE_SPECS[mode_id]


def mode_knowledge_dir(mode_id: str) -> Path:
    spec = get_mode(mode_id)
    if not spec.knowledge_subdir:
        return KNOWLEDGE_ROOT
    return KNOWLEDGE_ROOT / spec.knowledge_subdir


def ensure_mode_folders() -> None:
    MODES_ROOT.mkdir(parents=True, exist_ok=True)
    for spec in MODE_SPECS.values():
        if spec.knowledge_subdir:
            (KNOWLEDGE_ROOT / spec.knowledge_subdir).mkdir(
                parents=True, exist_ok=True
            )
