"""AI Reconcile — merge multiple drafts into one final answer."""

from __future__ import annotations

from typing import Iterator

from rag.config import RECONCILE_NUM_PREDICT
from rag.diagram import process_diagram_answer
from rag.providers import ProviderError, generate, stream

RECONCILE_SYSTEM = (
    "You are a senior QA lead reconciling multiple draft answers.\n"
    "Produce ONE final answer that:\n"
    "- Merges the strongest, non-conflicting points\n"
    "- Prefers concrete steps, examples, and citations when present\n"
    "- Removes duplication and contradictions (state assumptions if needed)\n"
    "- Does not invent APIs, tools, or facts not supported by the drafts\n"
    "- Stays concise and actionable\n"
    "If drafts include Mermaid, output one valid mermaid fenced flowchart."
)


class ReconcileAgent:
    def __init__(self, provider: str = "ollama") -> None:
        self.provider = provider

    def merge(
        self,
        question: str,
        drafts: list[dict],
        *,
        provider: str | None = None,
        mode_id: str = "",
    ) -> dict:
        provider = provider or self.provider
        usable = [d for d in drafts if (d.get("content") or d.get("answer") or "").strip()]
        if not usable:
            return {
                "answer": "No drafts available to reconcile.",
                "drafts": drafts,
                "reconciled": False,
            }
        if len(usable) == 1:
            text = usable[0].get("content") or usable[0].get("answer") or ""
            return {
                "answer": text,
                "drafts": drafts,
                "reconciled": False,
                "note": "Only one draft — returned as-is.",
            }

        prompt = _build_prompt(question, usable)
        try:
            raw = generate(
                prompt,
                provider=provider,
                system=RECONCILE_SYSTEM,
                temperature=0.2,
                num_predict=RECONCILE_NUM_PREDICT,
            )
        except ProviderError as exc:
            # Fallback: concatenate best drafts
            joined = "\n\n---\n\n".join(
                f"**{d.get('label', 'Draft')}**\n{(d.get('content') or d.get('answer') or '')}"
                for d in usable
            )
            return {
                "answer": f"_Reconcile provider error ({exc}). Showing drafts:_\n\n{joined}",
                "drafts": drafts,
                "reconciled": False,
            }

        answer = raw
        mermaid_meta = {}
        if mode_id == "workflow_diagram":
            mermaid_meta = process_diagram_answer(raw)
            answer = mermaid_meta["answer"]

        out = {
            "answer": answer,
            "drafts": [
                {
                    "label": d.get("label", "Draft"),
                    "content": d.get("content") or d.get("answer") or "",
                }
                for d in usable
            ],
            "reconciled": True,
            "note": f"Reconciled {len(usable)} drafts.",
        }
        if mermaid_meta:
            out["mermaid_source"] = mermaid_meta.get("mermaid_source", "")
            out["mermaid_valid"] = mermaid_meta.get("mermaid_valid")
            out["mermaid_error"] = mermaid_meta.get("mermaid_error", "")
        return out

    def merge_stream(
        self,
        question: str,
        drafts: list[dict],
        *,
        provider: str | None = None,
        mode_id: str = "",
    ) -> Iterator[dict]:
        yield {"type": "status", "message": "Reconciling drafts…"}
        provider = provider or self.provider
        usable = [d for d in drafts if (d.get("content") or d.get("answer") or "").strip()]
        if len(usable) <= 1:
            result = self.merge(question, drafts, provider=provider, mode_id=mode_id)
            yield {"type": "final", "result": result}
            return

        prompt = _build_prompt(question, usable)
        parts: list[str] = []
        try:
            for tok in stream(
                prompt,
                provider=provider,
                system=RECONCILE_SYSTEM,
                temperature=0.2,
                num_predict=RECONCILE_NUM_PREDICT,
            ):
                parts.append(tok)
                yield {"type": "token", "text": tok}
        except ProviderError as exc:
            result = self.merge(question, drafts, provider=provider, mode_id=mode_id)
            result["answer"] = f"_Reconcile stream error ({exc})._\n\n" + result.get(
                "answer", ""
            )
            yield {"type": "final", "result": result}
            return

        raw = "".join(parts).strip()
        answer = raw
        mermaid_meta = {}
        if mode_id == "workflow_diagram":
            mermaid_meta = process_diagram_answer(raw)
            answer = mermaid_meta["answer"]
        result = {
            "answer": answer,
            "drafts": [
                {
                    "label": d.get("label", "Draft"),
                    "content": d.get("content") or d.get("answer") or "",
                }
                for d in usable
            ],
            "reconciled": True,
            "note": f"Reconciled {len(usable)} drafts.",
        }
        if mermaid_meta:
            result["mermaid_source"] = mermaid_meta.get("mermaid_source", "")
            result["mermaid_valid"] = mermaid_meta.get("mermaid_valid")
            result["mermaid_error"] = mermaid_meta.get("mermaid_error", "")
        yield {"type": "final", "result": result}


def _build_prompt(question: str, drafts: list[dict]) -> str:
    blocks = []
    for i, d in enumerate(drafts, start=1):
        label = d.get("label") or f"Draft {i}"
        text = (d.get("content") or d.get("answer") or "").strip()
        blocks.append(f"### {label}\n{text}")
    return (
        f"User question:\n{question}\n\n"
        f"Draft answers to reconcile:\n\n" + "\n\n".join(blocks) + "\n\n"
        "Final reconciled answer:"
    )
