"""Central settings for the Playwright RAG chatbot."""

from __future__ import annotations

# Retrieval
RAG_MIN_SCORE = 0.68
WEAK_RAG_SCORE = 0.50
TOP_K = 3
RETRIEVE_MIN_SCORE = 0.15

# Generation (keep small for local gemma4:e2b latency)
LLM_MIN_CHARS = 40
SYNTH_NUM_PREDICT = 280
BARE_NUM_PREDICT = 240
SOURCE_CHAR_LIMIT = 700
MAX_SOURCES_FOR_PROMPT = 3

# High-confidence RAG: skip LLM rewrite for speed (still cited extract)
FAST_EXTRACT_SCORE = 0.85

# Models / Ollama
CHAT_MODEL = "gemma4:e2b"
EMBED_MODEL = "nomic-embed-text"
OLLAMA_BASE_URL = "http://localhost:11434"
KEEP_ALIVE = "30m"
NUM_CTX = 2048

# Query embedding cache
EMBED_CACHE_SIZE = 64
