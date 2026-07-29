"""LangChain Playwright cascade: Vector DB → LLM → internet → train if correct."""

from __future__ import annotations

import re
import threading
from pathlib import Path
from typing import Iterator

from rag.config import (
    BARE_NUM_PREDICT,
    CHAT_MODEL,
    EMBED_MODEL,
    FAST_EXTRACT_SCORE,
    FRAMEWORK,
    LLM_MIN_CHARS,
    MAX_SOURCES_FOR_PROMPT,
    RAG_MIN_SCORE,
    RETRIEVE_MIN_SCORE,
    SOURCE_CHAR_LIMIT,
    SYNTH_NUM_PREDICT,
    TOP_K,
    TRAINABLE_DOMAINS,
    TRAINABLE_MODES,
    WEAK_RAG_SCORE,
)
from rag.history import AnswerHistory
from rag.lc_ingest import ingest_markdown_file
from rag.lc_llm import LangChainLLM
from rag.lc_tools import run_web_fallback
from rag.lc_vectorstore import build_retriever, chunk_hits_to_sources
from rag.security import has_trainable_body, is_trainable_url, redact_secrets
from rag.web_search import learned_filename


class PlaywrightRAGBot:
    """Drop-in bot API backed by LangChain ChatOllama + Chroma retriever."""

    def __init__(
        self,
        knowledge_dir: Path | None = None,
        model: str = CHAT_MODEL,
        embed_model: str = EMBED_MODEL,
        top_k: int = TOP_K,
        rebuild_index: bool = False,
        rag_min_score: float = RAG_MIN_SCORE,
        warm_llm: bool = False,
    ) -> None:
        root = Path(__file__).resolve().parent
        self.knowledge_dir = knowledge_dir or (root / "knowledge")
        self.retriever = build_retriever(
            self.knowledge_dir,
            embed_model=embed_model,
            rebuild=rebuild_index,
        )
        self.llm = LangChainLLM(model=model)
        self.history = AnswerHistory()
        self.top_k = top_k
        self.embed_model = embed_model
        self.rag_min_score = rag_min_score
        self.framework = FRAMEWORK
        if warm_llm:
            threading.Thread(target=self._warm_llm_quietly, daemon=True).start()

    def _warm_llm_quietly(self) -> None:
        try:
            if self.llm.is_available():
                self.llm.warm_up()
        except Exception:  # noqa: BLE001
            pass

    def ask(self, question: str) -> dict:
        """
        Cascade (internet only after user says Not satisfied):
        1) Vector DB → synthesize (or fast extract if very confident)
        2) Local LangChain LLM (Qwen) if RAG is weak/missing
        3) Ask user if satisfied — call ask_internet() only if not
        """
        hits = self.retriever.retrieve(
            question, top_k=self.top_k, min_score=RETRIEVE_MIN_SCORE
        )
        best = hits[0][1] if hits else 0.0

        if hits and best >= self.rag_min_score:
            sources = chunk_hits_to_sources(hits[:MAX_SOURCES_FOR_PROMPT])
            if best >= FAST_EXTRACT_SCORE:
                answer = _extractive_answer(question, sources, origin="vector DB")
            else:
                answer = self._synthesize(question, sources, origin="vector DB")
            return self._finish(
                question,
                answer=answer,
                sources=sources,
                mode="rag",
                best=best,
                can_save=False,
                learned="",
                correct=None,
                can_search_web=True,
            )

        weak = hits[:2] if hits and best >= WEAK_RAG_SCORE else []
        weak_sources = chunk_hits_to_sources(weak) if weak else []
        llm_answer = ""
        mode = "llm"
        sources: list[dict] = []
        try:
            if weak_sources:
                llm_answer = self._synthesize(
                    question, weak_sources, origin="weak RAG + model"
                )
                if _is_proper_llm_answer(llm_answer):
                    mode = "llm_grounded"
                    sources = weak_sources
                else:
                    llm_answer = ""
            if not llm_answer:
                llm_answer = self.llm.answer_bare(
                    question,
                    temperature=0.3,
                    num_predict=BARE_NUM_PREDICT,
                )
                mode = "llm"
                sources = []
        except Exception:  # noqa: BLE001
            llm_answer = ""

        if _is_proper_llm_answer(llm_answer):
            learned = _markdown_from_qa(question, llm_answer, "local-llm")
            return self._finish(
                question,
                answer=llm_answer,
                sources=sources,
                mode=mode,
                best=best,
                can_save=True,
                learned=learned,
                correct=None,
                can_search_web=True,
            )

        # No auto-internet — ask the user to search the web if needed
        return self._finish(
            question,
            answer=(
                "I could not find a solid answer in the vector DB or local Qwen model. "
                "Are you satisfied, or should I search the internet / Playwright docs?"
            ),
            sources=[],
            mode="none",
            best=best,
            can_save=False,
            learned="",
            correct=None,
            can_search_web=True,
        )

    def ask_internet(self, question: str, *, prior_best: float = 0.0) -> dict:
        """Fetch from internet after the user says they are not satisfied."""
        web = run_web_fallback(question, max_pages=3)
        if web.get("ok") and (web.get("sources") or web.get("answer")):
            web_sources = _web_sources(web)
            answer = self._synthesize(
                question, web_sources, origin="internet"
            )
            if not _is_proper_llm_answer(answer):
                answer = web.get("answer") or _extractive_answer(
                    question, web_sources, origin="internet"
                )
            learned = web.get("learned_markdown") or _markdown_from_qa(
                question, answer, web.get("engine", "web")
            )
            can_save = _web_can_save(web, learned)
            if can_save:
                answer += (
                    "\n\n_Saved to history. Mark **Correct** only if accurate — "
                    "it will be added to the local vector database. "
                    "Do not save secrets or private data._"
                )
            else:
                answer += (
                    "\n\n_Web links were found but page text was too thin to train "
                    "the knowledge base. Refine the question or open the sources._"
                )
                learned = ""
            result = self._finish(
                question,
                answer=answer,
                sources=web_sources,
                mode="internet",
                best=prior_best,
                can_save=can_save,
                learned=learned,
                correct=None,
                can_search_web=False,
            )
            result["web_engine"] = web.get("engine", "web")
            result["google_url"] = web.get("google_url", "")
            return result

        return self._finish(
            question,
            answer=(
                "Internet search did not return a useful Playwright answer. "
                "Try rephrasing the question."
            ),
            sources=[],
            mode="none",
            best=prior_best,
            can_save=False,
            learned="",
            correct=False,
            can_search_web=False,
        )

    def ask_stream(self, question: str) -> Iterator[dict]:
        """
        Yield progress events, then a final result dict.
        Internet is NOT auto-run — user must choose Not satisfied.
        Events: {"type": "status"|"token"|"final", ...}
        """
        hits = self.retriever.retrieve(
            question, top_k=self.top_k, min_score=RETRIEVE_MIN_SCORE
        )
        best = hits[0][1] if hits else 0.0
        yield {"type": "status", "message": "Searching vector DB…", "best": best}

        if hits and best >= self.rag_min_score:
            sources = chunk_hits_to_sources(hits[:MAX_SOURCES_FOR_PROMPT])
            if best >= FAST_EXTRACT_SCORE:
                answer = _extractive_answer(question, sources, origin="vector DB")
                result = self._finish(
                    question,
                    answer=answer,
                    sources=sources,
                    mode="rag",
                    best=best,
                    can_save=False,
                    learned="",
                    correct=None,
                    can_search_web=True,
                )
                yield {"type": "final", "result": result}
                return

            yield {"type": "status", "message": "Synthesizing from sources…"}
            parts: list[str] = []
            try:
                for token in self._stream_synthesize(
                    question, sources, origin="vector DB"
                ):
                    parts.append(token)
                    yield {"type": "token", "text": token}
            except Exception:  # noqa: BLE001
                parts = []
            answer = "".join(parts).strip()
            if not _is_proper_llm_answer(answer):
                answer = _extractive_answer(question, sources, origin="vector DB")
            result = self._finish(
                question,
                answer=answer,
                sources=sources,
                mode="rag",
                best=best,
                can_save=False,
                learned="",
                correct=None,
                can_search_web=True,
            )
            yield {"type": "final", "result": result}
            return

        weak = hits[:2] if hits and best >= WEAK_RAG_SCORE else []
        weak_sources = chunk_hits_to_sources(weak) if weak else []
        llm_answer = ""
        mode = "llm"
        sources: list[dict] = []

        if weak_sources:
            yield {"type": "status", "message": "Grounding answer with weak RAG…"}
            parts = []
            try:
                for token in self._stream_synthesize(
                    question, weak_sources, origin="weak RAG + model"
                ):
                    parts.append(token)
                    yield {"type": "token", "text": token}
            except Exception:  # noqa: BLE001
                parts = []
            llm_answer = "".join(parts).strip()
            if _is_proper_llm_answer(llm_answer):
                mode = "llm_grounded"
                sources = weak_sources
            else:
                llm_answer = ""

        if not llm_answer:
            yield {"type": "status", "message": "Asking local Qwen coding LLM…"}
            parts = []
            try:
                for token in self.llm.stream_bare(
                    question,
                    temperature=0.3,
                    num_predict=BARE_NUM_PREDICT,
                ):
                    parts.append(token)
                    yield {"type": "token", "text": token}
            except Exception:  # noqa: BLE001
                parts = []
            llm_answer = "".join(parts).strip()
            mode = "llm"
            sources = []

        if _is_proper_llm_answer(llm_answer):
            learned = _markdown_from_qa(question, llm_answer, "local-llm")
            result = self._finish(
                question,
                answer=llm_answer,
                sources=sources,
                mode=mode,
                best=best,
                can_save=True,
                learned=learned,
                correct=None,
                can_search_web=True,
            )
            yield {"type": "final", "result": result}
            return

        result = self._finish(
            question,
            answer=(
                "I could not find a solid answer in the vector DB or local Qwen model. "
                "Are you satisfied, or should I search the internet / Playwright docs?"
            ),
            sources=[],
            mode="none",
            best=best,
            can_save=False,
            learned="",
            correct=None,
            can_search_web=True,
        )
        yield {"type": "final", "result": result}

    def ask_internet_stream(
        self, question: str, *, prior_best: float = 0.0
    ) -> Iterator[dict]:
        """Stream internet fallback after user clicks Not satisfied."""
        yield {"type": "status", "message": "Searching the internet…"}
        web = run_web_fallback(question, max_pages=3)
        if web.get("ok") and (web.get("sources") or web.get("answer")):
            web_sources = _web_sources(web)
            parts: list[str] = []
            try:
                for token in self._stream_synthesize(
                    question, web_sources, origin="internet"
                ):
                    parts.append(token)
                    yield {"type": "token", "text": token}
            except Exception:  # noqa: BLE001
                parts = []
            answer = "".join(parts).strip()
            if not _is_proper_llm_answer(answer):
                answer = web.get("answer") or _extractive_answer(
                    question, web_sources, origin="internet"
                )
            learned = web.get("learned_markdown") or _markdown_from_qa(
                question, answer, web.get("engine", "web")
            )
            can_save = _web_can_save(web, learned)
            if can_save:
                answer += (
                    "\n\n_Saved to history. Mark **Correct** only if accurate — "
                    "it will be added to the local vector database. "
                    "Do not save secrets or private data._"
                )
            else:
                answer += (
                    "\n\n_Web links were found but page text was too thin to train "
                    "the knowledge base._"
                )
                learned = ""
            result = self._finish(
                question,
                answer=answer,
                sources=web_sources,
                mode="internet",
                best=prior_best,
                can_save=can_save,
                learned=learned,
                correct=None,
                can_search_web=False,
            )
            result["web_engine"] = web.get("engine", "web")
            result["google_url"] = web.get("google_url", "")
            yield {"type": "final", "result": result}
            return

        result = self._finish(
            question,
            answer=(
                "Internet search did not return a useful Playwright answer. "
                "Try rephrasing the question."
            ),
            sources=[],
            mode="none",
            best=prior_best,
            can_save=False,
            learned="",
            correct=False,
            can_search_web=False,
        )
        yield {"type": "final", "result": result}

    def _finish(
        self,
        question: str,
        *,
        answer: str,
        sources: list,
        mode: str,
        best: float,
        can_save: bool,
        learned: str,
        correct: bool | None,
        can_search_web: bool = False,
    ) -> dict:
        followups = _followups(question, mode=mode)
        entry = self.history.append(
            question=question,
            answer=answer,
            mode=mode,
            best_score=best,
            sources=sources,
            learned_markdown=learned,
            correct=correct,
        )
        return {
            "answer": answer,
            "sources": sources,
            "used_rag": mode == "rag",
            "mode": mode,
            "vector_db": "chromadb",
            "framework": self.framework,
            "embed_model": self.embed_model,
            "indexed_chunks": self.retriever.count,
            "best_score": round(best, 4),
            "trained": False,
            "can_save_to_kb": can_save,
            "can_search_web": can_search_web,
            "learned_markdown": learned,
            "followups": followups,
            "history_id": entry["id"],
            "question": question,
        }

    def _sources_block(self, sources: list[dict]) -> str:
        blocks = []
        for s in sources[:MAX_SOURCES_FOR_PROMPT]:
            n = s.get("n") or (sources.index(s) + 1)
            s["n"] = n
            body = (s.get("text") or s.get("preview") or "").strip()
            blocks.append(
                f"[{n}] {s.get('title', 'Source')} ({s.get('source', '')})\n"
                f"{_trim(body, SOURCE_CHAR_LIMIT)}"
            )
        return "\n\n".join(blocks)

    def _synthesize(self, question: str, sources: list[dict], origin: str) -> str:
        if not sources:
            return ""
        try:
            text = self.llm.answer_from_sources(
                question,
                self._sources_block(sources),
                origin,
                temperature=0.2,
                num_predict=SYNTH_NUM_PREDICT,
            )
        except Exception:  # noqa: BLE001
            text = ""
        if _is_proper_llm_answer(text):
            return text
        return _extractive_answer(question, sources, origin=origin)


    def _stream_synthesize(
        self, question: str, sources: list[dict], origin: str
    ) -> Iterator[str]:
        yield from self.llm.stream_from_sources(
            question,
            self._sources_block(sources),
            origin,
            temperature=0.2,
            num_predict=SYNTH_NUM_PREDICT,
        )

    def mark_correct_and_train(self, history_id: str) -> dict:
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

        markdown = (entry.get("learned_markdown") or "").strip()
        if not markdown:
            markdown = _markdown_from_qa(
                entry.get("question", ""),
                entry.get("answer", ""),
                entry.get("mode", "history"),
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


def _web_sources(web: dict) -> list[dict]:
    web_sources = []
    for i, s in enumerate(web.get("sources") or [], start=1):
        web_sources.append(
            {
                "n": i,
                "id": f"web-{i}",
                "source": s.get("url", "web"),
                "url": s.get("url", ""),
                "title": s.get("title", f"Source {i}"),
                "score": 1.0,
                "preview": (s.get("url") or "")[:180],
                "text": "",
            }
        )
    bodies = _split_learned_bodies(web.get("learned_markdown") or "")
    for i, src in enumerate(web_sources):
        if i < len(bodies):
            src["text"] = bodies[i][:1800]
            src["preview"] = bodies[i][:220].replace("\n", " ")
    if not any(s.get("text") for s in web_sources) and web.get("answer"):
        if web_sources:
            web_sources[0]["text"] = web["answer"][:2000]
        else:
            web_sources = [
                {
                    "n": 1,
                    "id": "web-1",
                    "source": web.get("google_url") or "internet",
                    "url": web.get("google_url") or "",
                    "title": "Web result",
                    "score": 1.0,
                    "preview": "",
                    "text": web["answer"][:2000],
                }
            ]
    return web_sources[:MAX_SOURCES_FOR_PROMPT]


def _web_can_save(web: dict, learned: str) -> bool:
    if not has_trainable_body(learned):
        return False
    urls = [s.get("url") or "" for s in (web.get("sources") or [])]
    if not urls:
        # Local-doc catalog answers may still be trainable
        return True
    return any(is_trainable_url(u, TRAINABLE_DOMAINS) for u in urls if u)


def _extractive_answer(
    question: str, sources: list[dict], origin: str = "vector DB"
) -> str:
    if not sources:
        return ""
    top = sources[0]
    lines = [
        f"**From {origin}** for: {question}",
        "",
        f"### [{top.get('n', 1)}] {top.get('title', 'Source')}",
        _trim(top.get("text") or top.get("preview") or "", 1200),
    ]
    if len(sources) > 1:
        lines.append("")
        lines.append(
            "Also see: "
            + ", ".join(f"[{s.get('n')}] {s.get('title')}" for s in sources[1:])
        )
    return "\n".join(lines)


def _followups(question: str, mode: str) -> list[str]:
    q = question.lower()
    if "locator" in q or "getby" in q:
        ideas = [
            "When should I use getByTestId vs getByRole?",
            "How do I fix strict mode locator violations?",
            "Show a Page Object example using locators",
        ]
    elif "mock" in q or "route" in q:
        ideas = [
            "How do I mock a POST API with page.route?",
            "Difference between route.fulfill and route.abort?",
            "How do I do API testing with request fixture?",
        ]
    elif "auth" in q or "login" in q:
        ideas = [
            "How do I reuse login with storageState?",
            "How to set up global authentication setup?",
            "Best practices for multi-role auth in Playwright?",
        ]
    else:
        ideas = [
            "Show a minimal Playwright test example",
            "How do web-first assertions work?",
            "How do I debug with Trace Viewer?",
        ]
    return ideas[:3]


def _split_learned_bodies(markdown: str) -> list[str]:
    if not markdown:
        return []
    parts = re.split(r"\n## ", markdown)
    bodies = []
    for part in parts[1:] if len(parts) > 1 else []:
        lines = part.splitlines()
        body = "\n".join(lines[1:]).strip()
        if body:
            bodies.append(body)
    return bodies


def _is_proper_llm_answer(text: str) -> bool:
    text = (text or "").strip()
    if len(text) < LLM_MIN_CHARS:
        return False
    lowered = text.lower()
    bad = (
        "i don't know",
        "i do not know",
        "cannot help",
        "no idea",
        "empty response",
    )
    return not any(b in lowered for b in bad)


def _markdown_from_qa(question: str, answer: str, source: str) -> str:
    return (
        f"# Learned answer: {question}\n\n"
        f"Source: {source}\n\n"
        f"## Question\n{question}\n\n"
        f"## Answer\n{answer}\n"
    )


def _trim(text: str, limit: int) -> str:
    text = (text or "").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"
