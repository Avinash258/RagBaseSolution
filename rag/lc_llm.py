"""LangChain ChatOllama wrapper for Playwright Q&A."""

from __future__ import annotations

from typing import Iterator

import requests
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from rag.config import (
    CHAT_MODEL,
    KEEP_ALIVE,
    LLM_TEMPERATURE,
    NUM_CTX,
    OLLAMA_BASE_URL,
)

PLAYWRIGHT_SYSTEM = (
    "You are the Playwright KB agent for NEW VISION Testing Hub.\n"
    "Answer ONLY Playwright automation topics: @playwright/test, locators, fixtures, "
    "hooks, traces, network mocking, auth/storageState, CI, and TypeScript/JS test code.\n"
    "Prefer TypeScript with @playwright/test. "
    "Use resilient locators (getByRole, getByLabel, getByTestId). "
    "Give a direct answer, then a short code example when useful. "
    "If you are not sure, say you do not know. Do not invent APIs.\n"
    "If the question is NOT about Playwright (manual cases, Agile, estimation, "
    "defect process, synthetic data, general strategy), refuse briefly and tell the user "
    "to switch to that specialist agent in the sidebar. Do not answer off-topic in depth."
)

SYNTH_SYSTEM = (
    "You are the Playwright KB agent.\n"
    "Use ONLY the provided Playwright knowledge sources. Cite as [1], [2]. Be concise.\n"
    "Stay on Playwright automation — do not drift into unrelated QA topics.\n"
    "Start with a direct answer, then a short code example if useful.\n"
    "Prefer TypeScript with @playwright/test. Do not invent APIs.\n"
    "If sources and question are not about Playwright, say so and suggest switching agents."
)


def build_chat_ollama(
    model: str = CHAT_MODEL,
    *,
    temperature: float = LLM_TEMPERATURE,
    num_predict: int = 256,
    base_url: str = OLLAMA_BASE_URL,
) -> ChatOllama:
    return ChatOllama(
        model=model,
        base_url=base_url,
        temperature=temperature,
        num_predict=num_predict,
        num_ctx=NUM_CTX,
        keep_alive=KEEP_ALIVE,
    )


class LangChainLLM:
    """Thin facade so the rest of the app can call generate/stream/is_available."""

    def __init__(
        self,
        model: str = CHAT_MODEL,
        base_url: str = OLLAMA_BASE_URL,
        timeout: int = 120,
    ) -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._llm = build_chat_ollama(model, base_url=base_url)
        self._bare_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", PLAYWRIGHT_SYSTEM),
                ("human", "Question: {question}\n\nAnswer:"),
            ]
        )
        self._synth_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYNTH_SYSTEM),
                (
                    "human",
                    "Origin: {origin}\nQuestion: {question}\n\nSources:\n{sources}\n\nAnswer:",
                ),
            ]
        )

    def is_available(self) -> bool:
        try:
            r = requests.get(f"{self.base_url}/api/tags", timeout=5)
            r.raise_for_status()
            names = [m.get("name") for m in r.json().get("models", [])]
            return self.model in names or any(
                self.model in (n or "") for n in names
            )
        except requests.RequestException:
            return False

    def warm_up(self) -> None:
        try:
            self.generate("OK", temperature=0.0, num_predict=8)
        except Exception:  # noqa: BLE001
            pass

    def _client(
        self, *, temperature: float, num_predict: int
    ) -> ChatOllama:
        return build_chat_ollama(
            self.model,
            temperature=temperature,
            num_predict=num_predict,
            base_url=self.base_url,
        )

    def generate(
        self,
        prompt: str,
        temperature: float = LLM_TEMPERATURE,
        num_predict: int = 256,
    ) -> str:
        llm = self._client(temperature=temperature, num_predict=num_predict)
        msg = llm.invoke([HumanMessage(content=prompt)])
        return _content(msg)

    def answer_bare(
        self,
        question: str,
        *,
        temperature: float = 0.3,
        num_predict: int = 240,
    ) -> str:
        llm = self._client(temperature=temperature, num_predict=num_predict)
        chain = self._bare_prompt | llm
        msg = chain.invoke({"question": question})
        return _content(msg)

    def answer_from_sources(
        self,
        question: str,
        sources_block: str,
        origin: str,
        *,
        temperature: float = 0.2,
        num_predict: int = 280,
    ) -> str:
        llm = self._client(temperature=temperature, num_predict=num_predict)
        chain = self._synth_prompt | llm
        msg = chain.invoke(
            {
                "origin": origin,
                "question": question,
                "sources": sources_block,
            }
        )
        return _content(msg)

    def stream_bare(
        self,
        question: str,
        *,
        temperature: float = 0.3,
        num_predict: int = 240,
    ) -> Iterator[str]:
        llm = self._client(temperature=temperature, num_predict=num_predict)
        chain = self._bare_prompt | llm
        for chunk in chain.stream({"question": question}):
            text = _delta(chunk)
            if text:
                yield text

    def stream_from_sources(
        self,
        question: str,
        sources_block: str,
        origin: str,
        *,
        temperature: float = 0.2,
        num_predict: int = 280,
    ) -> Iterator[str]:
        llm = self._client(temperature=temperature, num_predict=num_predict)
        chain = self._synth_prompt | llm
        for chunk in chain.stream(
            {
                "origin": origin,
                "question": question,
                "sources": sources_block,
            }
        ):
            text = _delta(chunk)
            if text:
                yield text


def _content(msg) -> str:
    return _delta(msg).strip()


def _delta(msg) -> str:
    """Extract text from a message or stream chunk (do not strip mid-stream)."""
    if msg is None:
        return ""
    content = getattr(msg, "content", msg)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and "text" in item:
                parts.append(str(item["text"]))
        return "".join(parts)
    return str(content or "")
