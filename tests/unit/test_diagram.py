"""Offline tests for Mermaid diagram helpers."""

from rag.diagram import extract_mermaid, process_diagram_answer, validate_mermaid


def test_extract_fenced_mermaid():
    raw = """Here is the flow:

```mermaid
flowchart TD
  a[Start] --> b[End]
```

Done.
"""
    src = extract_mermaid(raw)
    assert src.startswith("flowchart TD")
    ok, err = validate_mermaid(src)
    assert ok, err


def test_process_diagram_answer_valid():
    raw = "```mermaid\nflowchart LR\n  loginPage[Login] --> homePage[Home]\n```\n"
    out = process_diagram_answer(raw)
    assert out["mermaid_valid"] is True
    assert "loginPage" in out["mermaid_source"]


def test_process_diagram_answer_invalid():
    out = process_diagram_answer("Sorry, no diagram.")
    assert out["mermaid_valid"] is False
    assert out["mermaid_error"]
