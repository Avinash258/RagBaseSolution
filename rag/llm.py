"""Ollama LLM client (session + keep-alive for lower latency)."""

from __future__ import annotations

import requests

from rag.config import CHAT_MODEL, KEEP_ALIVE, NUM_CTX, OLLAMA_BASE_URL


class OllamaLLM:
    def __init__(
        self,
        model: str = CHAT_MODEL,
        base_url: str = OLLAMA_BASE_URL,
        timeout: int = 120,
    ) -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._session = requests.Session()

    def is_available(self) -> bool:
        try:
            r = self._session.get(f"{self.base_url}/api/tags", timeout=5)
            r.raise_for_status()
            names = [m.get("name") for m in r.json().get("models", [])]
            return self.model in names or any(self.model in (n or "") for n in names)
        except requests.RequestException:
            return False

    def warm_up(self) -> None:
        try:
            self.generate("OK", temperature=0.0, num_predict=8)
        except requests.RequestException:
            pass

    def generate(
        self,
        prompt: str,
        temperature: float = 0.2,
        num_predict: int = 256,
    ) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "keep_alive": KEEP_ALIVE,
            "options": {
                "temperature": temperature,
                "num_predict": num_predict,
                "num_ctx": NUM_CTX,
            },
        }
        r = self._session.post(
            f"{self.base_url}/api/generate",
            json=payload,
            timeout=self.timeout,
        )
        r.raise_for_status()
        return (r.json().get("response") or "").strip()
