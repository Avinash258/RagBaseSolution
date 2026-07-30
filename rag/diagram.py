"""Mermaid workflow diagram helpers."""

from __future__ import annotations

import re

WORKFLOW_SYSTEM = (
    "You are a requirements-to-workflow specialist.\n"
    "Given application requirements, produce ONE Mermaid flowchart of the "
    "application workflow (user journeys / system steps).\n"
    "Rules:\n"
    "- Use flowchart TD or flowchart LR only (not classDiagram).\n"
    "- No emojis in Mermaid.\n"
    "- Node IDs must be camelCase (e.g. loginPage, submitOrder).\n"
    "- Quote labels that contain spaces or special characters.\n"
    "- Wrap the diagram in a fenced mermaid code block.\n"
    "- After the fence, add at most two short bullets explaining the flow.\n"
    "- Do not invent features not implied by the requirements."
)


def build_workflow_prompt(requirements: str) -> str:
    return (
        "Turn these requirements into an application workflow diagram "
        "(Mermaid flowchart).\n\n"
        f"Requirements:\n{requirements.strip()}\n"
    )


def extract_mermaid(text: str) -> str:
    """Extract Mermaid source from LLM output (fenced or raw flowchart)."""
    text = (text or "").strip()
    if not text:
        return ""
    fence = re.search(
        r"```(?:mermaid)?\s*\n(.*?)```",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if fence:
        return fence.group(1).strip()
    # Raw flowchart starting at first flowchart/graph line
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith(("flowchart ", "graph ")):
            idx = text.find(line)
            return text[idx:].strip()
    return ""


def sanitize_mermaid(source: str) -> str:
    """Light cleanup: strip emojis-ish chars and normalize fences leftovers."""
    source = (source or "").strip()
    if not source:
        return ""
    # Drop accidental fence markers
    source = re.sub(r"^```(?:mermaid)?\s*", "", source, flags=re.I)
    source = re.sub(r"```\s*$", "", source)
    # Remove common emoji ranges (basic BMP symbols often pasted by models)
    source = re.sub(
        "["
        "\U0001F300-\U0001F9FF"
        "\u2600-\u26FF"
        "\u2700-\u27BF"
        "]+",
        "",
        source,
    )
    return source.strip()


def validate_mermaid(source: str) -> tuple[bool, str]:
    """Basic structural checks — not a full Mermaid parser."""
    source = sanitize_mermaid(source)
    if not source:
        return False, "No Mermaid diagram found in the response."
    first = source.splitlines()[0].strip().lower()
    if not (first.startswith("flowchart ") or first.startswith("graph ")):
        return False, "Diagram must start with flowchart TD/LR or graph TD/LR."
    if "-->" not in source and "---" not in source:
        return False, "Diagram has no edges (expected --> or ---)."
    # Unbalanced brackets (rough)
    if source.count("[") != source.count("]"):
        return False, "Unbalanced [] in diagram."
    if source.count("{") != source.count("}"):
        return False, "Unbalanced {} in diagram."
    return True, ""


def process_diagram_answer(raw: str) -> dict:
    """Return mermaid_source, valid, error, and display answer."""
    mermaid = sanitize_mermaid(extract_mermaid(raw))
    ok, err = validate_mermaid(mermaid)
    if ok:
        display = (
            f"```mermaid\n{mermaid}\n```\n\n"
            + _extra_notes(raw, mermaid)
        ).strip()
        return {
            "answer": display,
            "mermaid_source": mermaid,
            "mermaid_valid": True,
            "mermaid_error": "",
        }
    return {
        "answer": (raw or "").strip() or "_No diagram produced._",
        "mermaid_source": mermaid,
        "mermaid_valid": False,
        "mermaid_error": err or "Invalid Mermaid",
    }


def _extra_notes(raw: str, mermaid: str) -> str:
    """Keep short prose outside the mermaid fence."""
    cleaned = re.sub(
        r"```(?:mermaid)?\s*\n.*?```",
        "",
        raw or "",
        flags=re.I | re.DOTALL,
    ).strip()
    if not cleaned:
        return ""
    # Avoid dumping the raw flowchart again
    if cleaned.strip() == mermaid.strip():
        return ""
    return cleaned[:800]
