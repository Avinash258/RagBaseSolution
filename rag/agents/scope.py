"""Per-agent domain scope — keep each specialist on-topic."""

from __future__ import annotations

# Hard scope rules appended to every specialist system prompt.
SCOPE_RULES: dict[str, str] = {
    "playwright_kb": (
        "SCOPE (strict): You are ONLY the Playwright knowledge agent.\n"
        "- Answer questions about Playwright (@playwright/test), browser automation, "
        "locators, fixtures, hooks, traces, debugging, network mocking (page.route), "
        "auth/storageState, CI for Playwright, and TypeScript/JavaScript test code.\n"
        "- Prefer TypeScript with @playwright/test. Use resilient locators "
        "(getByRole, getByLabel, getByTestId). Do not invent APIs.\n"
        "- If the question is NOT about Playwright (e.g. Agile ceremonies, estimation, "
        "manual test-case writing, defect workflow, synthetic data, general test strategy "
        "without automation), do NOT answer it in depth. Reply briefly that you are the "
        "Playwright KB agent and name the correct sidebar agent to switch to.\n"
        "- Never discuss Selenium/Cypress/WebdriverIO except to contrast briefly with Playwright."
    ),
    "synthetic_data": (
        "SCOPE (strict): Answer ONLY about synthetic / anonymized test data, fixtures, "
        "personas, boundary values, and sample JSON/CSV for tests.\n"
        "If the question is about Playwright code, Agile, estimation, or defect process, "
        "redirect the user to that specialist agent instead of answering in depth."
    ),
    "manual_cases": (
        "SCOPE (strict): Answer ONLY about manual / exploratory test cases "
        "(ID, title, preconditions, steps, expected results).\n"
        "If the question asks for Playwright automation code, redirect to Playwright KB. "
        "If it is about strategy, estimation, or Agile process, redirect to that agent."
    ),
    "test_strategy": (
        "SCOPE (strict): Answer ONLY about test strategy / test plan content "
        "(scope, approach, environments, risks, entry/exit, tooling).\n"
        "Do not write Playwright scripts or full manual case suites — redirect those agents."
    ),
    "estimation": (
        "SCOPE (strict): Answer ONLY about QA effort estimation, sizing, staffing, "
        "and breakdown of hours/days with assumptions.\n"
        "Do not write automation code or full strategy docs — redirect when asked."
    ),
    "agile": (
        "SCOPE (strict): Answer ONLY about Agile/Scrum/Kanban QA practices, "
        "ceremonies, Definition of Done, and shift-left collaboration.\n"
        "Do not write Playwright code or detailed estimation tables unless briefly illustrative."
    ),
    "defect_lifecycle": (
        "SCOPE (strict): Answer ONLY about defect lifecycle, triage, severity/priority, "
        "states, retest, and root-cause notes.\n"
        "Redirect Playwright coding or Agile ceremony questions to those agents."
    ),
    "workflow_diagram": (
        "SCOPE (strict): Produce Mermaid workflow diagrams from requirements only. "
        "Do not write Playwright tests or full test strategies."
    ),
}

# Optional hint when user is clearly in another agent's domain
_OFFTOPIC_HINTS: dict[str, tuple[str, ...]] = {
    "playwright_kb": (
        "sprint ceremony",
        "story points",
        "velocity chart",
        "definition of done checklist",
        "defect severity matrix",
        "bug lifecycle states",
        "estimate hours for testing",
        "generate synthetic personas",
        "write manual test cases only",
    ),
}


def scoped_system(mode_id: str, persona: str) -> str:
    """Combine persona + hard scope rules for a mode (idempotent)."""
    rules = SCOPE_RULES.get(mode_id, "").strip()
    base = (persona or "").strip()
    if not rules:
        return base
    if rules in base:
        return base
    if not base:
        return rules
    return f"{base}\n\n{rules}"


def scope_user_prefix(mode_id: str, label: str) -> str:
    """Remind the model of the active agent on every user turn."""
    return (
        f"[Active agent: {label} ({mode_id}). Stay strictly inside this agent's knowledge.]\n"
    )


def offtopic_redirect(mode_id: str, question: str) -> str | None:
    """
    Cheap heuristic: if Playwright agent gets an obviously non-automation ask,
    return a short redirect message instead of a free-form answer.
    Returns None when the question should go to the LLM as usual.
    """
    if mode_id != "playwright_kb":
        return None
    q = (question or "").lower()
    # Strong Playwright signals → always allow
    pw_signals = (
        "playwright",
        "locator",
        "getbyrole",
        "getbylabel",
        "getbytestid",
        "page.route",
        "storagestate",
        "trace viewer",
        "@playwright",
        "browser context",
        "expect(",
        "test.describe",
        "fixture",
        "chromium",
        "webkit",
        "firefox",
        "automation",
        "e2e",
        "end-to-end",
    )
    if any(s in q for s in pw_signals):
        return None
    hints = _OFFTOPIC_HINTS.get(mode_id, ())
    if any(h in q for h in hints):
        return (
            "I'm the **Playwright KB** agent — I only answer Playwright automation questions "
            "(locators, fixtures, traces, mocking, CI, TypeScript tests).\n\n"
            "Your question looks like another specialty. Please switch agents in the sidebar:\n"
            "- **Manual cases** — structured manual test cases\n"
            "- **Test strategy** — plan / strategy sections\n"
            "- **Estimation** — effort sizing\n"
            "- **Agile** — Scrum/Kanban QA practices\n"
            "- **Defect lifecycle** — bug triage & workflow\n"
            "- **Synthetic data** — fixtures & anonymized data\n"
        )
    return None
