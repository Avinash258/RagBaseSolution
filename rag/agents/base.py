"""Base specialist agent with mode-scoped RAG + provider generation."""

from __future__ import annotations

from pathlib import Path
from typing import Iterator

from rag.config import (
    BARE_NUM_PREDICT,
    EMBED_MODEL,
    LLM_MIN_CHARS,
    MAX_SOURCES_FOR_PROMPT,
    RAG_MIN_SCORE,
    RETRIEVE_MIN_SCORE,
    SOURCE_CHAR_LIMIT,
    SYNTH_NUM_PREDICT,
    TOP_K,
    WEAK_RAG_SCORE,
)
from rag.agents.scope import scope_user_prefix, scoped_system
from rag.history import AnswerHistory
from rag.lc_vectorstore import chunk_hits_to_sources
from rag.modes import ModeSpec, mode_knowledge_dir
from rag.providers import ProviderError, generate, stream
from rag.retriever import ChromaRetriever


class BaseModeAgent:
    """Per-mode agent: optional folder RAG → provider LLM with mode system prompt."""

    mode_id: str = ""
    system_prompt: str = "You are a helpful testing specialist."

    def __init__(
        self,
        spec: ModeSpec,
        *,
        embed_model: str = EMBED_MODEL,
        history: AnswerHistory | None = None,
        rebuild_index: bool = False,
    ) -> None:
        self.spec = spec
        self.mode_id = spec.id
        self.embed_model = embed_model
        self.history = history or AnswerHistory()
        self.knowledge_dir = mode_knowledge_dir(spec.id)
        # Ensure scope rules are always attached for this mode
        self.system_prompt = scoped_system(spec.id, self.system_prompt)
        self.retriever: ChromaRetriever | None = None
        if spec.supports_rag:
            persist = (
                Path(__file__).resolve().parent.parent
                / "chroma_db"
                / "modes"
                / spec.id
            )
            self.knowledge_dir.mkdir(parents=True, exist_ok=True)
            self.retriever = ChromaRetriever(
                knowledge_dir=self.knowledge_dir,
                persist_dir=persist,
                embed_model=embed_model,
                rebuild=rebuild_index,
                auto_rebuild=False,
            )

    def ask(
        self,
        question: str,
        *,
        provider: str = "ollama",
    ) -> dict:
        drafts: list[dict] = []
        sources: list[dict] = []
        best = 0.0
        answer = ""
        mode = "agent"

        if self.retriever is not None:
            hits = self.retriever.retrieve(
                question, top_k=TOP_K, min_score=RETRIEVE_MIN_SCORE
            )
            best = hits[0][1] if hits else 0.0
            if hits and best >= RAG_MIN_SCORE:
                sources = chunk_hits_to_sources(hits[:MAX_SOURCES_FOR_PROMPT])
                answer = self._synthesize(question, sources, provider=provider)
                if _ok(answer):
                    mode = "rag"
            elif hits and best >= WEAK_RAG_SCORE:
                sources = chunk_hits_to_sources(hits[:2])
                answer = self._synthesize(
                    question, sources, provider=provider, origin="weak RAG"
                )
                if _ok(answer):
                    mode = "llm_grounded"

        if not _ok(answer):
            answer = self._bare(question, provider=provider)
            mode = "llm" if _ok(answer) else "none"
            if mode == "none":
                answer = (
                    "I could not produce a solid answer for this mode. "
                    "Try rephrasing or switch provider."
                )

        drafts.append({"label": f"{self.spec.label} ({provider})", "content": answer})
        return self._finish(
            question,
            answer=answer,
            sources=sources,
            mode=mode,
            best=best,
            drafts=drafts,
            provider=provider,
        )

    def ask_stream(
        self,
        question: str,
        *,
        provider: str = "ollama",
    ) -> Iterator[dict]:
        yield {"type": "status", "message": f"{self.spec.label}: working…"}
        # Streaming via generate then token-ish yield for non-ollama simplicity
        result = None
        try:
            # Prefer true stream for bare path when no strong RAG
            if self.retriever is not None:
                yield {"type": "status", "message": "Searching mode knowledge…"}
                hits = self.retriever.retrieve(
                    question, top_k=TOP_K, min_score=RETRIEVE_MIN_SCORE
                )
                best = hits[0][1] if hits else 0.0
                if hits and best >= RAG_MIN_SCORE:
                    sources = chunk_hits_to_sources(hits[:MAX_SOURCES_FOR_PROMPT])
                    yield {"type": "status", "message": "Synthesizing from sources…"}
                    parts: list[str] = []
                    for tok in self._stream_synthesize(
                        question, sources, provider=provider
                    ):
                        parts.append(tok)
                        yield {"type": "token", "text": tok}
                    answer = "".join(parts).strip()
                    if not _ok(answer):
                        answer = self._synthesize(
                            question, sources, provider=provider
                        )
                    result = self._finish(
                        question,
                        answer=answer,
                        sources=sources,
                        mode="rag",
                        best=best,
                        drafts=[
                            {
                                "label": f"{self.spec.label} ({provider})",
                                "content": answer,
                            }
                        ],
                        provider=provider,
                    )
                    yield {"type": "final", "result": result}
                    return

            yield {"type": "status", "message": "Asking specialist LLM…"}
            parts = []
            prefix = scope_user_prefix(self.mode_id, self.spec.label)
            for tok in stream(
                f"{prefix}Question: {question}\n\nAnswer:",
                provider=provider,
                system=self.system_prompt,
                temperature=0.3,
                num_predict=BARE_NUM_PREDICT,
            ):
                parts.append(tok)
                yield {"type": "token", "text": tok}
            answer = "".join(parts).strip()
            mode = "llm" if _ok(answer) else "none"
            if not _ok(answer):
                answer = (
                    "I could not produce a solid answer for this mode. "
                    "Try rephrasing or switch provider."
                )
            result = self._finish(
                question,
                answer=answer,
                sources=[],
                mode=mode,
                best=0.0,
                drafts=[
                    {
                        "label": f"{self.spec.label} ({provider})",
                        "content": answer,
                    }
                ],
                provider=provider,
            )
            yield {"type": "final", "result": result}
        except ProviderError as exc:
            result = self._finish(
                question,
                answer=f"Provider error: {exc}",
                sources=[],
                mode="none",
                best=0.0,
                drafts=[],
                provider=provider,
            )
            yield {"type": "final", "result": result}

    def ask_rag_draft(self, question: str, *, provider: str = "ollama") -> dict:
        """RAG-only draft for RAG+LLM reconcile (no bare LLM fallback)."""
        if self.retriever is None:
            return {
                "answer": "",
                "sources": [],
                "label": f"{self.spec.label} RAG",
            }
        hits = self.retriever.retrieve(
            question, top_k=TOP_K, min_score=RETRIEVE_MIN_SCORE
        )
        if not hits:
            return {
                "answer": "",
                "sources": [],
                "label": f"{self.spec.label} RAG",
            }
        sources = chunk_hits_to_sources(hits[:MAX_SOURCES_FOR_PROMPT])
        answer = self._synthesize(question, sources, provider=provider)
        return {
            "answer": answer,
            "sources": sources,
            "label": f"{self.spec.label} RAG ({provider})",
            "best_score": hits[0][1],
        }

    def ask_llm_draft(self, question: str, *, provider: str = "ollama") -> dict:
        """Bare LLM draft for RAG+LLM reconcile."""
        answer = self._bare(question, provider=provider)
        return {
            "answer": answer,
            "sources": [],
            "label": f"{self.spec.label} LLM ({provider})",
        }

    def rebuild_index(self) -> int:
        if self.retriever is None:
            return 0
        return self.retriever.rebuild()

    def mark_correct_and_train(self, history_id: str) -> dict:
        from rag.config import TRAINABLE_MODES
        from rag.lc_ingest import ingest_markdown_file
        from rag.security import has_trainable_body, redact_secrets
        from rag.web_search import learned_filename

        entry = self.history.get(history_id)
        if not entry:
            return {"ok": False, "error": f"History id not found: {history_id}"}
        if entry.get("saved_to_kb"):
            return {
                "ok": True,
                "already_saved": True,
                "learned_file": entry.get("learned_file", ""),
                "trained_chunks": 0,
            }
        if entry.get("mode") not in TRAINABLE_MODES:
            return {
                "ok": False,
                "error": f"Mode '{entry.get('mode')}' is not trainable.",
            }
        if self.retriever is None:
            return {"ok": False, "error": "This mode has no vector index to train."}

        markdown = (entry.get("learned_markdown") or "").strip()
        if not markdown:
            markdown = (
                f"# Learned answer: {entry.get('question', '')}\n\n"
                f"## Question\n{entry.get('question', '')}\n\n"
                f"## Answer\n{entry.get('answer', '')}\n"
            )
        markdown = redact_secrets(markdown)
        if not has_trainable_body(markdown):
            return {
                "ok": False,
                "error": "Not enough trainable content to add to the vector DB.",
            }
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)
        filename = learned_filename(entry.get("question") or history_id)
        path = self.knowledge_dir / filename
        path.write_text(markdown + "\n", encoding="utf-8")
        chunks = ingest_markdown_file(self.retriever, path)
        self.history.mark_correct(
            history_id, saved_to_kb=True, learned_file=filename
        )
        return {
            "ok": True,
            "already_saved": False,
            "learned_file": filename,
            "trained_chunks": len(chunks),
            "indexed_chunks": self.retriever.count,
        }

    def _bare(self, question: str, *, provider: str) -> str:
        prefix = scope_user_prefix(self.mode_id, self.spec.label)
        try:
            return generate(
                f"{prefix}Question: {question}\n\nAnswer:",
                provider=provider,
                system=self.system_prompt,
                temperature=0.3,
                num_predict=BARE_NUM_PREDICT,
            )
        except ProviderError:
            return ""

    def _synthesize(
        self,
        question: str,
        sources: list[dict],
        *,
        provider: str,
        origin: str = "mode knowledge",
    ) -> str:
        block = _sources_block(sources)
        prefix = scope_user_prefix(self.mode_id, self.spec.label)
        prompt = (
            f"{prefix}Origin: {origin}\nQuestion: {question}\n\n"
            f"Sources:\n{block}\n\n"
            "Answer using the sources when relevant. Stay in this agent's domain:"
        )
        try:
            return generate(
                prompt,
                provider=provider,
                system=self.system_prompt
                + "\nUse sources when helpful. Cite as [1], [2]. Be concise.",
                temperature=0.2,
                num_predict=SYNTH_NUM_PREDICT,
            )
        except ProviderError:
            return ""

    def _stream_synthesize(
        self,
        question: str,
        sources: list[dict],
        *,
        provider: str,
        origin: str = "mode knowledge",
    ) -> Iterator[str]:
        block = _sources_block(sources)
        prefix = scope_user_prefix(self.mode_id, self.spec.label)
        prompt = (
            f"{prefix}Origin: {origin}\nQuestion: {question}\n\n"
            f"Sources:\n{block}\n\n"
            "Answer using the sources when relevant. Stay in this agent's domain:"
        )
        yield from stream(
            prompt,
            provider=provider,
            system=self.system_prompt
            + "\nUse sources when helpful. Cite as [1], [2]. Be concise.",
            temperature=0.2,
            num_predict=SYNTH_NUM_PREDICT,
        )

    def _finish(
        self,
        question: str,
        *,
        answer: str,
        sources: list,
        mode: str,
        best: float,
        drafts: list[dict],
        provider: str,
        reconciled: bool = False,
        reconcile_strategy: str = "off",
        mermaid_source: str = "",
        mermaid_valid: bool | None = None,
        mermaid_error: str = "",
        can_search_web: bool | None = None,
        can_save: bool | None = None,
    ) -> dict:
        if can_search_web is None:
            can_search_web = bool(self.spec.allow_web and mode != "internet")
        if can_save is None:
            can_save = mode in {"llm", "llm_grounded", "agent", "reconciled"}
        learned = ""
        if can_save:
            learned = (
                f"# Learned answer: {question}\n\n"
                f"Source: {self.mode_id}/{provider}\n\n"
                f"## Question\n{question}\n\n"
                f"## Answer\n{answer}\n"
            )
        entry = self.history.append(
            question=question,
            answer=answer,
            mode="reconciled" if reconciled else mode,
            best_score=best,
            sources=sources,
            learned_markdown=learned,
            correct=None,
        )
        out = {
            "answer": answer,
            "sources": sources,
            "mode": "reconciled" if reconciled else mode,
            "best_score": round(best, 4),
            "can_save_to_kb": can_save,
            "can_search_web": can_search_web,
            "learned_markdown": learned,
            "followups": list(self.spec.suggestions[:3]),
            "history_id": entry["id"],
            "question": question,
            "mode_id": self.mode_id,
            "mode_label": self.spec.label,
            "provider": provider,
            "drafts": drafts,
            "reconciled": reconciled,
            "reconcile_strategy": reconcile_strategy,
            "framework": "langchain",
        }
        if mermaid_source or mermaid_valid is not None:
            out["mermaid_source"] = mermaid_source
            out["mermaid_valid"] = bool(mermaid_valid)
            out["mermaid_error"] = mermaid_error
        return out


def _sources_block(sources: list[dict]) -> str:
    blocks = []
    for i, s in enumerate(sources[:MAX_SOURCES_FOR_PROMPT], start=1):
        s["n"] = s.get("n") or i
        body = (s.get("text") or s.get("preview") or "").strip()
        if len(body) > SOURCE_CHAR_LIMIT:
            body = body[: SOURCE_CHAR_LIMIT - 1] + "…"
        blocks.append(
            f"[{s['n']}] {s.get('title', 'Source')} ({s.get('source', '')})\n{body}"
        )
    return "\n\n".join(blocks)


def _ok(text: str) -> bool:
    text = (text or "").strip()
    if len(text) < LLM_MIN_CHARS:
        return False
    lowered = text.lower()
    bad = ("i don't know", "i do not know", "cannot help", "no idea", "empty response")
    return not any(b in lowered for b in bad)
