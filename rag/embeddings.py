"""Ollama embedding client with query cache."""

from __future__ import annotations

from collections import OrderedDict

import requests

from rag.config import (
    EMBED_CACHE_SIZE,
    EMBED_MODEL,
    KEEP_ALIVE,
    OLLAMA_BASE_URL,
)


class OllamaEmbedder:
    def __init__(
        self,
        model: str = EMBED_MODEL,
        base_url: str = OLLAMA_BASE_URL,
        timeout: int = 120,
    ) -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = requests.Session()
        self._query_cache: OrderedDict[str, list[float]] = OrderedDict()

    def is_available(self) -> bool:
        try:
            r = self._session.get(f"{self.base_url}/api/tags", timeout=5)
            r.raise_for_status()
            names = [m.get("name") for m in r.json().get("models", [])]
            return any(self.model == n or self.model in (n or "") for n in names)
        except requests.RequestException:
            return False

    def _prefix(self, text: str, kind: str) -> str:
        if "nomic" not in self.model:
            return text
        tag = "search_query" if kind == "query" else "search_document"
        return f"{tag}: {text}"

    def _cache_get(self, key: str) -> list[float] | None:
        if key not in self._query_cache:
            return None
        self._query_cache.move_to_end(key)
        return self._query_cache[key]

    def _cache_put(self, key: str, value: list[float]) -> None:
        self._query_cache[key] = value
        self._query_cache.move_to_end(key)
        while len(self._query_cache) > EMBED_CACHE_SIZE:
            self._query_cache.popitem(last=False)

    def embed(self, text: str, kind: str = "query") -> list[float]:
        cache_key = f"{kind}::{text.strip().lower()}"
        if kind == "query":
            cached = self._cache_get(cache_key)
            if cached is not None:
                return cached

        payload_text = self._prefix(text, kind)
        embedding: list[float] | None = None

        try:
            r = self._session.post(
                f"{self.base_url}/api/embed",
                json={
                    "model": self.model,
                    "input": payload_text,
                    "keep_alive": KEEP_ALIVE,
                },
                timeout=self.timeout,
            )
            if r.status_code == 200:
                embeddings = r.json().get("embeddings") or []
                if embeddings:
                    embedding = embeddings[0]
        except requests.RequestException:
            embedding = None

        if embedding is None:
            r = self._session.post(
                f"{self.base_url}/api/embeddings",
                json={
                    "model": self.model,
                    "prompt": payload_text,
                    "keep_alive": KEEP_ALIVE,
                },
                timeout=self.timeout,
            )
            r.raise_for_status()
            embedding = r.json().get("embedding")
            if not embedding:
                raise RuntimeError(f"No embedding returned for model {self.model}")

        if kind == "query":
            self._cache_put(cache_key, embedding)
        return embedding

    def embed_many(
        self,
        texts: list[str],
        kind: str = "document",
        batch_size: int = 16,
    ) -> list[list[float]]:
        out: list[list[float]] = []
        for i in range(0, len(texts), batch_size):
            raw_batch = texts[i : i + batch_size]
            batch = [self._prefix(t, kind) for t in raw_batch]
            try:
                r = self._session.post(
                    f"{self.base_url}/api/embed",
                    json={
                        "model": self.model,
                        "input": batch,
                        "keep_alive": KEEP_ALIVE,
                    },
                    timeout=self.timeout,
                )
                if r.status_code == 200:
                    embeddings = r.json().get("embeddings") or []
                    if len(embeddings) == len(batch):
                        out.extend(embeddings)
                        continue
            except requests.RequestException:
                pass
            out.extend(self.embed(t, kind=kind) for t in raw_batch)
        return out
