"""Optional LangChain tool-calling agent for Playwright Q&A."""

from __future__ import annotations

from langchain_core.messages import HumanMessage
from langchain_core.tools import tool

from rag.config import CHAT_MODEL
from rag.lc_llm import build_chat_ollama
from rag.lc_tools import search_playwright_web
from rag.retriever import ChromaRetriever


def build_kb_tool(retriever: ChromaRetriever, top_k: int = 3):
    @tool("search_playwright_kb")
    def search_playwright_kb(question: str) -> str:
        """Search the local Playwright vector knowledge base."""
        hits = retriever.retrieve(question, top_k=top_k, min_score=0.15)
        if not hits:
            return "No knowledge-base hits."
        parts = []
        for chunk, score in hits:
            parts.append(
                f"[{score:.2f}] {chunk.title} ({chunk.source})\n{chunk.text[:800]}"
            )
        return "\n\n".join(parts)

    return search_playwright_kb


def try_create_agent(retriever: ChromaRetriever, model: str = CHAT_MODEL):
    """
    Build a ReAct agent if langgraph is installed.
    Returns None when langgraph is unavailable (cascade remains default).
    """
    try:
        from langgraph.prebuilt import create_react_agent
    except ImportError:
        return None

    llm = build_chat_ollama(model, temperature=0.2, num_predict=320)
    tools = [build_kb_tool(retriever), search_playwright_web]
    return create_react_agent(llm, tools)


def run_agent_once(agent, question: str) -> str:
    if agent is None:
        return ""
    result = agent.invoke(
        {
            "messages": [
                HumanMessage(
                    content=(
                        "Answer this Playwright testing question. "
                        "Use tools when helpful.\n\n" + question
                    )
                )
            ]
        }
    )
    messages = result.get("messages") or []
    if not messages:
        return ""
    last = messages[-1]
    content = getattr(last, "content", "")
    return content.strip() if isinstance(content, str) else str(content)
