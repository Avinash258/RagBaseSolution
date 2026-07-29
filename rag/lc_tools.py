"""LangChain tools wrapping web search and KB helpers."""

from __future__ import annotations

from langchain_core.tools import tool

from rag.web_search import gather_web_answer


@tool("search_playwright_web")
def search_playwright_web(question: str) -> str:
    """Search Playwright docs / web when the local knowledge base misses."""
    web = gather_web_answer(question, max_pages=3)
    if not web.get("ok"):
        return "No web results found."
    parts = [web.get("answer") or ""]
    for s in web.get("sources") or []:
        parts.append(f"- {s.get('title', '')}: {s.get('url', '')}")
    return "\n".join(p for p in parts if p).strip() or "No web results found."


def run_web_fallback(question: str, max_pages: int = 3) -> dict:
    """Direct call used by the cascade (returns structured dict)."""
    return gather_web_answer(question, max_pages=max_pages)


PLAYWRIGHT_TOOLS = [search_playwright_web]
