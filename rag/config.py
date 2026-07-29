"""Central settings for the Playwright RAG chatbot (LangChain + Ollama)."""

from __future__ import annotations

# Retrieval
RAG_MIN_SCORE = 0.68
WEAK_RAG_SCORE = 0.50
TOP_K = 3
RETRIEVE_MIN_SCORE = 0.15

# Generation (tuned for local qwen2.5-coder latency)
LLM_MIN_CHARS = 40
SYNTH_NUM_PREDICT = 280
BARE_NUM_PREDICT = 240
SOURCE_CHAR_LIMIT = 700
MAX_SOURCES_FOR_PROMPT = 3

# High-confidence RAG: skip LLM rewrite for speed (still cited extract)
FAST_EXTRACT_SCORE = 0.85

# Models / Ollama — coding-focused chat model
CHAT_MODEL = "qwen2.5-coder:1.5b"
EMBED_MODEL = "nomic-embed-text"
OLLAMA_BASE_URL = "http://localhost:11434"
KEEP_ALIVE = "30m"
NUM_CTX = 2048
LLM_TEMPERATURE = 0.2

# Query embedding cache
EMBED_CACHE_SIZE = 64

# Framework tag (shown in UI)
FRAMEWORK = "langchain"
