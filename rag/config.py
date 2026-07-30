"""Central settings for the Multi-mode Testing Hub (LangChain + providers)."""

from __future__ import annotations

import os
from pathlib import Path


def _load_dotenv() -> None:
    """Load repo-root .env if present (no override of existing env vars)."""
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        return
    try:
        from dotenv import load_dotenv

        load_dotenv(env_path, override=False)
    except ImportError:
        # Minimal fallback without python-dotenv
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = val


_load_dotenv()


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
RECONCILE_NUM_PREDICT = int(_env_float("RECONCILE_NUM_PREDICT", 400))
DIAGRAM_NUM_PREDICT = int(_env_float("DIAGRAM_NUM_PREDICT", 500))

# High-confidence RAG: skip LLM rewrite for speed (still cited extract)
FAST_EXTRACT_SCORE = _env_float("FAST_EXTRACT_SCORE", 0.85)

# Models / Ollama — coding-focused chat model
CHAT_MODEL = _env("CHAT_MODEL", "qwen2.5-coder:1.5b")
EMBED_MODEL = _env("EMBED_MODEL", "nomic-embed-text")
OLLAMA_BASE_URL = _env("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
KEEP_ALIVE = _env("KEEP_ALIVE", "30m")
NUM_CTX = int(_env_float("NUM_CTX", 2048))
LLM_TEMPERATURE = _env_float("LLM_TEMPERATURE", 0.2)

# Provider switcher: ollama | gemini | nvidia
LLM_PROVIDER = _env("LLM_PROVIDER", "ollama").lower()
GEMINI_API_KEY = _env("GEMINI_API_KEY", "")
GEMINI_MODEL = _env("GEMINI_MODEL", "gemini-flash-latest")
NVIDIA_API_KEY = _env("NVIDIA_API_KEY", "")
NVIDIA_MODEL = _env("NVIDIA_MODEL", "z-ai/glm-5.2")
NVIDIA_BASE_URL = _env(
    "NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1"
).rstrip("/")
NVIDIA_MAX_TOKENS = int(_env_float("NVIDIA_MAX_TOKENS", 16384))
NVIDIA_TOP_P = _env_float("NVIDIA_TOP_P", 1.0)
NVIDIA_SEED = int(_env_float("NVIDIA_SEED", 42))
# Second NVIDIA key (NVIDIABuild-Autogen-50)
NVIDIA_BUILD_API_KEY = _env("NVIDIA_BUILD_API_KEY", "")
NVIDIA_BUILD_MODEL = _env("NVIDIA_BUILD_MODEL", "z-ai/glm-5.2")

# Reconcile defaults
RECONCILE_MAX_MODES = 3
RECONCILE_SECONDARY_PROVIDER = _env("RECONCILE_SECONDARY_PROVIDER", "gemini")

# Query embedding cache
EMBED_CACHE_SIZE = 64

# Framework tag (shown in UI)
FRAMEWORK = "langchain"

# Answer cascade modes that may be saved into the knowledge base
TRAINABLE_MODES = frozenset({"llm", "llm_grounded", "internet", "agent", "reconciled"})

# Domains preferred when training from web content
TRAINABLE_DOMAINS = frozenset(
    {
        "playwright.dev",
        "github.com",
        "avinash258.github.io",
    }
)

PROVIDER_IDS = ("ollama", "gemini", "nvidia", "nvidia_build")
PROVIDER_LABELS = {
    "ollama": "Local (Ollama)",
    "gemini": "Gemini",
    "nvidia": "NVIDIA (glm-5.2)",
    "nvidia_build": "NVIDIA Build (Autogen-50)",
}
NVIDIA_PROVIDER_IDS = frozenset({"nvidia", "nvidia_build"})

# Selectable chat models per provider (UI dropdown)
OLLAMA_MODEL_OPTIONS = (
    CHAT_MODEL,
    "qwen2.5-coder:1.5b",
    "qwen2.5-coder:7b",
    "qwen2.5:3b",
    "llama3.2:3b",
    "mistral:7b",
)
GEMINI_MODEL_OPTIONS = (
    GEMINI_MODEL,
    "gemini-flash-latest",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash",
)
NVIDIA_MODEL_OPTIONS = (
    NVIDIA_MODEL,
    "z-ai/glm-5.2",
    "meta/llama-3.1-8b-instruct",
    "meta/llama-3.1-70b-instruct",
    "mistralai/mistral-nemotron",
)
