"""Concrete specialist agents — one class per mode."""

from __future__ import annotations

from typing import Iterator

from rag.agents.base import BaseModeAgent
from rag.agents.scope import offtopic_redirect, scoped_system
from rag.config import DIAGRAM_NUM_PREDICT
from rag.diagram import (
    WORKFLOW_SYSTEM,
    build_workflow_prompt,
    process_diagram_answer,
)
from rag.lc_pipeline import PlaywrightRAGBot
from rag.modes import ModeSpec, get_mode
from rag.providers import ProviderError, generate, stream


class PlaywrightKbAgent(BaseModeAgent):
    """Wraps existing PlaywrightRAGBot cascade; provider used for non-Ollama."""

    system_prompt = scoped_system(
        "playwright_kb",
        "You are the Playwright KB agent. Prefer TypeScript with @playwright/test. "
        "Use resilient locators. Do not invent APIs.",
    )

    def __init__(self, spec: ModeSpec | None = None, **kwargs) -> None:
        spec = spec or get_mode("playwright_kb")
        # Playwright uses the main knowledge root / existing bot — skip mode chroma
        self.spec = spec
        self.mode_id = spec.id
        self.system_prompt = PlaywrightKbAgent.system_prompt
        self.history = kwargs.get("history")
        rebuild = bool(kwargs.get("rebuild_index", False))
        self.bot = PlaywrightRAGBot(rebuild_index=rebuild)
        if self.history is not None:
            self.bot.history = self.history
        else:
            self.history = self.bot.history
        self.retriever = self.bot.retriever
        self.embed_model = self.bot.embed_model
        self.knowledge_dir = self.bot.knowledge_dir

    def ask(self, question: str, *, provider: str = "ollama") -> dict:
        redirect = offtopic_redirect(self.mode_id, question)
        if redirect:
            return self._finish(
                question,
                answer=redirect,
                sources=[],
                mode="agent",
                best=0.0,
                drafts=[{"label": f"{self.spec.label} (scope)", "content": redirect}],
                provider=provider,
                can_save=False,
            )
        if provider == "ollama":
            from rag.providers import resolve_model

            self.bot.llm.model = resolve_model("ollama")
            result = self.bot.ask(question)
        else:
            # Cloud provider: bare/synth via providers, optional RAG context
            result = super().ask(question, provider=provider)
            result["can_search_web"] = True
            return result
        result["mode_id"] = self.mode_id
        result["mode_label"] = self.spec.label
        result["provider"] = provider
        result["drafts"] = [
            {"label": f"{self.spec.label} ({provider})", "content": result.get("answer", "")}
        ]
        result["reconciled"] = False
        result["reconcile_strategy"] = "off"
        return result

    def ask_stream(self, question: str, *, provider: str = "ollama") -> Iterator[dict]:
        redirect = offtopic_redirect(self.mode_id, question)
        if redirect:
            yield {"type": "status", "message": "Checking agent scope…"}
            result = self._finish(
                question,
                answer=redirect,
                sources=[],
                mode="agent",
                best=0.0,
                drafts=[{"label": f"{self.spec.label} (scope)", "content": redirect}],
                provider=provider,
                can_save=False,
            )
            yield {"type": "token", "text": redirect}
            yield {"type": "final", "result": result}
            return
        if provider != "ollama":
            yield from super().ask_stream(question, provider=provider)
            return
        from rag.providers import resolve_model

        self.bot.llm.model = resolve_model("ollama")
        for event in self.bot.ask_stream(question):
            if event.get("type") == "final":
                result = event.get("result") or {}
                result["mode_id"] = self.mode_id
                result["mode_label"] = self.spec.label
                result["provider"] = provider
                result.setdefault(
                    "drafts",
                    [
                        {
                            "label": f"{self.spec.label} ({provider})",
                            "content": result.get("answer", ""),
                        }
                    ],
                )
                result["reconciled"] = False
                result["reconcile_strategy"] = "off"
                yield {"type": "final", "result": result}
            else:
                yield event

    def ask_internet(self, question: str, *, prior_best: float = 0.0) -> dict:
        result = self.bot.ask_internet(question, prior_best=prior_best)
        result["mode_id"] = self.mode_id
        result["mode_label"] = self.spec.label
        result["provider"] = "ollama"
        result["drafts"] = [
            {"label": "Internet", "content": result.get("answer", "")}
        ]
        result["reconciled"] = False
        result["reconcile_strategy"] = "off"
        return result

    def ask_internet_stream(
        self, question: str, *, prior_best: float = 0.0
    ) -> Iterator[dict]:
        for event in self.bot.ask_internet_stream(question, prior_best=prior_best):
            if event.get("type") == "final":
                result = event.get("result") or {}
                result["mode_id"] = self.mode_id
                result["mode_label"] = self.spec.label
                result["provider"] = "ollama"
                result.setdefault(
                    "drafts",
                    [{"label": "Internet", "content": result.get("answer", "")}],
                )
                result["reconciled"] = False
                result["reconcile_strategy"] = "off"
                yield {"type": "final", "result": result}
            else:
                yield event

    def mark_correct_and_train(self, history_id: str) -> dict:
        return self.bot.mark_correct_and_train(history_id)

    def rebuild_index(self) -> int:
        return self.bot.retriever.rebuild()

    def ask_rag_draft(self, question: str, *, provider: str = "ollama") -> dict:
        hits = self.retriever.retrieve(question, top_k=3, min_score=0.15)
        if not hits:
            return {"answer": "", "sources": [], "label": "Playwright RAG"}
        from rag.lc_vectorstore import chunk_hits_to_sources

        sources = chunk_hits_to_sources(hits[:3])
        if provider == "ollama":
            answer = self.bot._synthesize(question, sources, origin="vector DB")
        else:
            answer = self._synthesize(question, sources, provider=provider)
        return {
            "answer": answer,
            "sources": sources,
            "label": f"Playwright RAG ({provider})",
            "best_score": hits[0][1],
        }

    def ask_llm_draft(self, question: str, *, provider: str = "ollama") -> dict:
        if provider == "ollama":
            try:
                answer = self.bot.llm.answer_bare(question, temperature=0.3)
            except Exception:  # noqa: BLE001
                answer = ""
        else:
            answer = self._bare(question, provider=provider)
        return {
            "answer": answer,
            "sources": [],
            "label": f"Playwright LLM ({provider})",
        }


class SyntheticDataAgent(BaseModeAgent):
    system_prompt = scoped_system(
        "synthetic_data",
        "You are a synthetic test-data specialist. "
        "Produce realistic, privacy-safe fixtures (no real PII). "
        "Prefer tables or JSON. Explain assumptions briefly.",
    )

    def __init__(self, spec: ModeSpec | None = None, **kwargs) -> None:
        super().__init__(spec or get_mode("synthetic_data"), **kwargs)


class ManualCasesAgent(BaseModeAgent):
    system_prompt = scoped_system(
        "manual_cases",
        "You are a manual test-case designer. "
        "Output structured cases: ID, Title, Preconditions, Steps, Expected. "
        "Cover positive, negative, and edge paths when useful.",
    )

    def __init__(self, spec: ModeSpec | None = None, **kwargs) -> None:
        super().__init__(spec or get_mode("manual_cases"), **kwargs)


class TestStrategyAgent(BaseModeAgent):
    system_prompt = scoped_system(
        "test_strategy",
        "You are a test-strategy consultant. "
        "Produce clear strategy sections: scope, approach, environments, "
        "risks, entry/exit criteria, tooling. Be practical and concise.",
    )

    def __init__(self, spec: ModeSpec | None = None, **kwargs) -> None:
        super().__init__(spec or get_mode("test_strategy"), **kwargs)


class EstimationAgent(BaseModeAgent):
    system_prompt = scoped_system(
        "estimation",
        "You are a QA estimation specialist. "
        "Give effort ranges (hours/days), assumptions, risks, and a breakdown. "
        "State confidence. Do not fabricate precise calendar dates.",
    )

    def __init__(self, spec: ModeSpec | None = None, **kwargs) -> None:
        super().__init__(spec or get_mode("estimation"), **kwargs)


class AgileAgent(BaseModeAgent):
    system_prompt = scoped_system(
        "agile",
        "You are an Agile QA coach for Scrum/Kanban teams. "
        "Advise on ceremonies, DoD, shift-left, and collaboration. "
        "Keep advice actionable for testers and developers.",
    )

    def __init__(self, spec: ModeSpec | None = None, **kwargs) -> None:
        super().__init__(spec or get_mode("agile"), **kwargs)


class DefectLifecycleAgent(BaseModeAgent):
    system_prompt = scoped_system(
        "defect_lifecycle",
        "You are a defect-lifecycle and triage specialist. "
        "Help with severity/priority, states, retest, and root-cause notes. "
        "Be precise and process-oriented.",
    )

    def __init__(self, spec: ModeSpec | None = None, **kwargs) -> None:
        super().__init__(spec or get_mode("defect_lifecycle"), **kwargs)


class WorkflowDiagramAgent(BaseModeAgent):
    """Requirements → Mermaid flowchart (light RAG examples optional)."""

    system_prompt = scoped_system("workflow_diagram", WORKFLOW_SYSTEM)

    def __init__(self, spec: ModeSpec | None = None, **kwargs) -> None:
        # supports_rag False in spec — BaseModeAgent skips retriever
        super().__init__(spec or get_mode("workflow_diagram"), **kwargs)

    def ask(self, question: str, *, provider: str = "ollama") -> dict:
        try:
            raw = generate(
                build_workflow_prompt(question),
                provider=provider,
                system=self.system_prompt,
                temperature=0.2,
                num_predict=DIAGRAM_NUM_PREDICT,
            )
        except ProviderError as exc:
            return self._finish(
                question,
                answer=f"Provider error: {exc}",
                sources=[],
                mode="none",
                best=0.0,
                drafts=[],
                provider=provider,
                can_search_web=False,
                can_save=False,
            )
        processed = process_diagram_answer(raw)
        return self._finish(
            question,
            answer=processed["answer"],
            sources=[],
            mode="agent" if processed["mermaid_valid"] else "none",
            best=0.0,
            drafts=[{"label": f"Workflow ({provider})", "content": raw}],
            provider=provider,
            mermaid_source=processed.get("mermaid_source", ""),
            mermaid_valid=processed.get("mermaid_valid"),
            mermaid_error=processed.get("mermaid_error", ""),
            can_search_web=False,
            can_save=processed.get("mermaid_valid", False),
        )

    def ask_stream(self, question: str, *, provider: str = "ollama") -> Iterator[dict]:
        yield {"type": "status", "message": "Building workflow diagram…"}
        parts: list[str] = []
        try:
            for tok in stream(
                build_workflow_prompt(question),
                provider=provider,
                system=self.system_prompt,
                temperature=0.2,
                num_predict=DIAGRAM_NUM_PREDICT,
            ):
                parts.append(tok)
                yield {"type": "token", "text": tok}
        except ProviderError as exc:
            result = self._finish(
                question,
                answer=f"Provider error: {exc}",
                sources=[],
                mode="none",
                best=0.0,
                drafts=[],
                provider=provider,
                can_search_web=False,
                can_save=False,
            )
            yield {"type": "final", "result": result}
            return
        raw = "".join(parts).strip()
        processed = process_diagram_answer(raw)
        result = self._finish(
            question,
            answer=processed["answer"],
            sources=[],
            mode="agent" if processed["mermaid_valid"] else "none",
            best=0.0,
            drafts=[{"label": f"Workflow ({provider})", "content": raw}],
            provider=provider,
            mermaid_source=processed.get("mermaid_source", ""),
            mermaid_valid=processed.get("mermaid_valid"),
            mermaid_error=processed.get("mermaid_error", ""),
            can_search_web=False,
            can_save=processed.get("mermaid_valid", False),
        )
        yield {"type": "final", "result": result}

    def ask_llm_draft(self, question: str, *, provider: str = "ollama") -> dict:
        try:
            raw = generate(
                build_workflow_prompt(question),
                provider=provider,
                system=self.system_prompt,
                temperature=0.45,
                num_predict=DIAGRAM_NUM_PREDICT,
            )
        except ProviderError:
            raw = ""
        return {
            "answer": raw,
            "sources": [],
            "label": f"Workflow LLM ({provider})",
        }

    def ask_rag_draft(self, question: str, *, provider: str = "ollama") -> dict:
        # Second temperature draft used as stand-in when RAG unsupported
        try:
            raw = generate(
                build_workflow_prompt(question),
                provider=provider,
                system=self.system_prompt,
                temperature=0.15,
                num_predict=DIAGRAM_NUM_PREDICT,
            )
        except ProviderError:
            raw = ""
        return {
            "answer": raw,
            "sources": [],
            "label": f"Workflow draft A ({provider})",
        }


AGENT_CLASSES = {
    "playwright_kb": PlaywrightKbAgent,
    "synthetic_data": SyntheticDataAgent,
    "manual_cases": ManualCasesAgent,
    "test_strategy": TestStrategyAgent,
    "estimation": EstimationAgent,
    "agile": AgileAgent,
    "defect_lifecycle": DefectLifecycleAgent,
    "workflow_diagram": WorkflowDiagramAgent,
}
