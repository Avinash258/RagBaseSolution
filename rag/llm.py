"""Ollama LLM client — re-exports LangChain-backed implementation."""

from rag.lc_llm import LangChainLLM as OllamaLLM
from rag.config import CHAT_MODEL, OLLAMA_BASE_URL

__all__ = ["OllamaLLM", "CHAT_MODEL", "OLLAMA_BASE_URL"]
