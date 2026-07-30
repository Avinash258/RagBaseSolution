"""Agent hub — routes modes and AI Reconcile strategies."""

from __future__ import annotations

from typing import Iterator

from rag.agents.reconcile import ReconcileAgent
from rag.agents.specialists import AGENT_CLASSES
from rag.config import RECONCILE_MAX_MODES, RECONCILE_SECONDARY_PROVIDER
from rag.history import AnswerHistory
from rag.modes import ensure_mode_folders, get_mode, list_modes
from rag.providers import normalize_provider, provider_ready


class AgentHub:
    """Constructs specialist agents once and runs ask / reconcile flows."""

    def __init__(self, *, rebuild_index: bool = False) -> None:
        ensure_mode_folders()
        self.history = AnswerHistory()
        self.agents = {}
        for mode_id, cls in AGENT_CLASSES.items():
            self.agents[mode_id] = cls(
                get_mode(mode_id),
                history=self.history,
                rebuild_index=rebuild_index,
            )
        self.reconcile = ReconcileAgent()
        # Expose Playwright bot helpers for UI compatibility
        self.playwright = self.agents["playwright_kb"]

    @property
    def llm(self):
        return self.playwright.bot.llm

    @property
    def retriever(self):
        return self.playwright.retriever

    @property
    def embed_model(self) -> str:
        return self.playwright.embed_model

    def get_agent(self, mode_id: str):
        if mode_id not in self.agents:
            raise KeyError(f"Unknown mode: {mode_id}")
        return self.agents[mode_id]

    def mark_correct_and_train(
        self, history_id: str, *, mode_id: str | None = None
    ) -> dict:
        mid = mode_id or "playwright_kb"
        agent = self.agents.get(mid) or self.playwright
        return agent.mark_correct_and_train(history_id)

    def rebuild_all(self) -> dict[str, int]:
        counts = {}
        for mode_id, agent in self.agents.items():
            try:
                counts[mode_id] = int(agent.rebuild_index() or 0)
            except Exception:  # noqa: BLE001
                counts[mode_id] = 0
        return counts

    def ask_stream(
        self,
        question: str,
        *,
        mode_id: str = "playwright_kb",
        provider: str = "ollama",
        reconcile_strategy: str = "off",
        secondary_provider: str | None = None,
        multi_modes: list[str] | None = None,
    ) -> Iterator[dict]:
        """
        Strategies:
          off | two_providers | rag_llm | multi_mode
        On-demand reconcile is handled separately via reconcile_on_demand().
        """
        provider = normalize_provider(provider)
        strategy = (reconcile_strategy or "off").strip().lower()
        secondary = normalize_provider(
            secondary_provider or RECONCILE_SECONDARY_PROVIDER
        )
        if secondary == provider and strategy == "two_providers":
            # Pick a different secondary when possible
            for cand in ("gemini", "nvidia", "nvidia_build", "ollama"):
                if cand != provider:
                    ok, _ = provider_ready(cand)
                    if ok:
                        secondary = cand
                        break

        if strategy in ("", "off", "none"):
            yield from self.get_agent(mode_id).ask_stream(
                question, provider=provider
            )
            return

        if strategy in ("two_providers", "two_provider", "providers"):
            yield from self._two_providers(
                question,
                mode_id=mode_id,
                primary=provider,
                secondary=secondary,
            )
            return

        if strategy in ("rag_llm", "rag+llm", "rag_plus_llm"):
            yield from self._rag_llm(
                question, mode_id=mode_id, provider=provider
            )
            return

        if strategy in ("multi_mode", "multimode", "multi"):
            modes = multi_modes or self._default_multi_modes(mode_id)
            yield from self._multi_mode(
                question, modes=modes, provider=provider
            )
            return

        # Unknown → single path
        yield from self.get_agent(mode_id).ask_stream(question, provider=provider)

    def reconcile_on_demand(
        self,
        question: str,
        existing_answer: str,
        *,
        mode_id: str = "playwright_kb",
        primary_provider: str = "ollama",
        secondary_provider: str | None = None,
        existing_drafts: list[dict] | None = None,
    ) -> Iterator[dict]:
        """Strategy 4: merge existing answer with a fresh secondary draft."""
        secondary = normalize_provider(
            secondary_provider or RECONCILE_SECONDARY_PROVIDER
        )
        primary = normalize_provider(primary_provider)
        if secondary == primary:
            for cand in ("gemini", "nvidia", "nvidia_build", "ollama"):
                if cand != primary:
                    ok, _ = provider_ready(cand)
                    if ok:
                        secondary = cand
                        break

        yield {
            "type": "status",
            "message": f"On-demand reconcile: drafting with {secondary}…",
        }
        agent = self.get_agent(mode_id)
        draft_b = agent.ask(question, provider=secondary)
        drafts = list(existing_drafts or [])
        if not drafts and existing_answer:
            drafts.append(
                {
                    "label": f"Original ({primary})",
                    "content": existing_answer,
                }
            )
        drafts.append(
            {
                "label": f"{agent.spec.label} ({secondary})",
                "content": draft_b.get("answer", ""),
            }
        )
        yield from self._finalize_reconcile(
            question,
            drafts,
            mode_id=mode_id,
            provider=primary,
            strategy="on_demand",
            sources=draft_b.get("sources") or [],
            can_search_web=bool(get_mode(mode_id).allow_web),
        )

    def ask_internet_stream(
        self, question: str, *, prior_best: float = 0.0
    ) -> Iterator[dict]:
        yield from self.playwright.ask_internet_stream(
            question, prior_best=prior_best
        )

    def _default_multi_modes(self, mode_id: str) -> list[str]:
        spec = get_mode(mode_id)
        modes = [mode_id]
        for mid in spec.related_modes:
            if mid not in modes:
                modes.append(mid)
            if len(modes) >= RECONCILE_MAX_MODES:
                break
        return modes[:RECONCILE_MAX_MODES]

    def _two_providers(
        self,
        question: str,
        *,
        mode_id: str,
        primary: str,
        secondary: str,
    ) -> Iterator[dict]:
        agent = self.get_agent(mode_id)
        yield {
            "type": "status",
            "message": f"Draft A via {primary}…",
        }
        a = agent.ask(question, provider=primary)
        yield {
            "type": "status",
            "message": f"Draft B via {secondary}…",
        }
        b = agent.ask(question, provider=secondary)
        drafts = [
            {"label": f"{agent.spec.label} ({primary})", "content": a.get("answer", "")},
            {
                "label": f"{agent.spec.label} ({secondary})",
                "content": b.get("answer", ""),
            },
        ]
        sources = (a.get("sources") or []) or (b.get("sources") or [])
        yield from self._finalize_reconcile(
            question,
            drafts,
            mode_id=mode_id,
            provider=primary,
            strategy="two_providers",
            sources=sources,
            can_search_web=bool(agent.spec.allow_web),
        )

    def _rag_llm(
        self, question: str, *, mode_id: str, provider: str
    ) -> Iterator[dict]:
        agent = self.get_agent(mode_id)
        yield {"type": "status", "message": "RAG draft…"}
        rag = agent.ask_rag_draft(question, provider=provider)
        yield {"type": "status", "message": "LLM draft…"}
        llm = agent.ask_llm_draft(question, provider=provider)
        drafts = [
            {"label": rag.get("label", "RAG"), "content": rag.get("answer", "")},
            {"label": llm.get("label", "LLM"), "content": llm.get("answer", "")},
        ]
        yield from self._finalize_reconcile(
            question,
            drafts,
            mode_id=mode_id,
            provider=provider,
            strategy="rag_llm",
            sources=rag.get("sources") or [],
            can_search_web=bool(agent.spec.allow_web),
        )

    def _multi_mode(
        self, question: str, *, modes: list[str], provider: str
    ) -> Iterator[dict]:
        drafts = []
        sources: list = []
        for mid in modes[:RECONCILE_MAX_MODES]:
            if mid not in self.agents:
                continue
            agent = self.agents[mid]
            yield {
                "type": "status",
                "message": f"Running {agent.spec.label}…",
            }
            result = agent.ask(question, provider=provider)
            drafts.append(
                {
                    "label": f"{agent.spec.label} ({provider})",
                    "content": result.get("answer", ""),
                }
            )
            if not sources and result.get("sources"):
                sources = result["sources"]
        primary_mode = modes[0] if modes else "playwright_kb"
        yield from self._finalize_reconcile(
            question,
            drafts,
            mode_id=primary_mode,
            provider=provider,
            strategy="multi_mode",
            sources=sources,
            can_search_web=bool(get_mode(primary_mode).allow_web),
        )

    def _finalize_reconcile(
        self,
        question: str,
        drafts: list[dict],
        *,
        mode_id: str,
        provider: str,
        strategy: str,
        sources: list,
        can_search_web: bool,
    ) -> Iterator[dict]:
        agent = self.get_agent(mode_id)
        merged = None
        for event in self.reconcile.merge_stream(
            question, drafts, provider=provider, mode_id=mode_id
        ):
            if event.get("type") == "final":
                merged = event.get("result") or {}
            else:
                yield event
        if not merged:
            merged = self.reconcile.merge(
                question, drafts, provider=provider, mode_id=mode_id
            )
        answer = merged.get("answer") or ""
        result = agent._finish(
            question,
            answer=answer,
            sources=sources,
            mode="reconciled",
            best=0.0,
            drafts=merged.get("drafts") or drafts,
            provider=provider,
            reconciled=True,
            reconcile_strategy=strategy,
            mermaid_source=merged.get("mermaid_source", ""),
            mermaid_valid=merged.get("mermaid_valid"),
            mermaid_error=merged.get("mermaid_error", ""),
            can_search_web=can_search_web,
            can_save=True,
        )
        yield {"type": "final", "result": result}


def default_mode_id() -> str:
    return "playwright_kb"


def all_mode_cards() -> list[dict]:
    return [
        {
            "id": m.id,
            "label": m.label,
            "description": m.description,
            "suggestions": list(m.suggestions),
            "allow_web": m.allow_web,
            "supports_rag": m.supports_rag,
        }
        for m in list_modes()
    ]
