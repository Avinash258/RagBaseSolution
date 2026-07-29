"""Central settings for the Playwright RAG chatbot (LangChain + Ollama)."""

from __future__ import annotations

import os


def _env(name: str, default: str) -> str:
    return (os.getenv(name) or default).strip()


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None or not str(raw).strip():
        return default
    try:
        return float(raw)
    except ValueError:
        return default


# Retrieval
RAG_MIN_SCORE = _env_float("RAG_MIN_SCORE", 0.68)
WEAK_RAG_SCORE = _env_float("WEAK_RAG_SCORE", 0.50)
TOP_K = int(_env_float("TOP_K", 3))
RETRIEVE_MIN_SCORE = _env_float("RETRIEVE_MIN_SCORE", 0.15)

# Generation (tuned for local qwen2.5-coder latency)
LLM_MIN_CHARS = 40
SYNTH_NUM_PREDICT = 280
BARE_NUM_PREDICT = 240
SOURCE_CHAR_LIMIT = 700
MAX_SOURCES_FOR_PROMPT = 3

# High-confidence RAG: skip LLM rewrite for speed (still cited extract)
FAST_EXTRACT_SCORE = _env_float("FAST_EXTRACT_SCORE", 0.85)

# Models / Ollama — coding-focused chat model
CHAT_MODEL = _env("CHAT_MODEL", "qwen2.5-coder:1.5b")
EMBED_MODEL = _env("EMBED_MODEL", "nomic-embed-text")
OLLAMA_BASE_URL = _env("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
KEEP_ALIVE = _env("KEEP_ALIVE", "30m")
NUM_CTX = int(_env_float("NUM_CTX", 2048))
LLM_TEMPERATURE = _env_float("LLM_TEMPERATURE", 0.2)

# Query embedding cache
EMBED_CACHE_SIZE = 64

# Framework tag (shown in UI)
FRAMEWORK = "langchain"

# Modes that may be saved into the knowledge base
TRAINABLE_MODES = frozenset({"llm", "llm_grounded", "internet"})

# Domains preferred when training from web content
TRAINABLE_DOMAINS = frozenset(
    {
        "playwright.dev",
        "github.com",
        "avinash258.github.io",
    }
)
