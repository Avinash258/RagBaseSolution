"""Unified LLM generate/stream for Ollama, Gemini, and NVIDIA."""

from __future__ import annotations

from typing import Iterator

import requests

from rag.config import (
    CHAT_MODEL,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GEMINI_MODEL_OPTIONS,
    LLM_TEMPERATURE,
    NVIDIA_API_KEY,
    NVIDIA_BASE_URL,
    NVIDIA_BUILD_API_KEY,
    NVIDIA_BUILD_MODEL,
    NVIDIA_MAX_TOKENS,
    NVIDIA_MODEL,
    NVIDIA_MODEL_OPTIONS,
    NVIDIA_PROVIDER_IDS,
    NVIDIA_SEED,
    NVIDIA_TOP_P,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL_OPTIONS,
    PROVIDER_IDS,
)

# Per-provider model overrides set by the UI
_model_overrides: dict[str, str] = {}


class ProviderError(RuntimeError):
    """Raised when a provider is misconfigured or unreachable."""


def normalize_provider(provider: str | None) -> str:
    p = (provider or "ollama").strip().lower()
    if p in ("local", "ollama", "qwen"):
        return "ollama"
    if p in ("nvidia_build", "nvidia-build", "nvidiabuild", "autogen"):
        return "nvidia_build"
    if p in PROVIDER_IDS:
        return p
    raise ProviderError(f"Unknown provider: {provider}")


def set_provider_model(provider: str, model: str) -> None:
    """Remember the UI-selected model for a provider."""
    p = normalize_provider(provider)
    model = (model or "").strip()
    if model:
        _model_overrides[p] = model


def clear_provider_models() -> None:
    _model_overrides.clear()


def default_model_for(provider: str) -> str:
    p = normalize_provider(provider)
    if p == "ollama":
        return CHAT_MODEL
    if p == "gemini":
        return GEMINI_MODEL
    if p == "nvidia_build":
        return NVIDIA_BUILD_MODEL or NVIDIA_MODEL
    if p == "nvidia":
        return NVIDIA_MODEL
    return CHAT_MODEL


def resolve_model(provider: str, model: str | None = None) -> str:
    p = normalize_provider(provider)
    if model and str(model).strip():
        return str(model).strip()
    if p in _model_overrides:
        return _model_overrides[p]
    return default_model_for(p)


def list_models(provider: str) -> list[str]:
    """Models shown in the UI dropdown for a provider."""
    p = normalize_provider(provider)
    if p == "ollama":
        names = list(OLLAMA_MODEL_OPTIONS)
        try:
            r = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3)
            r.raise_for_status()
            for m in r.json().get("models", []) or []:
                name = (m.get("name") or "").strip()
                if name and name not in names:
                    names.append(name)
        except requests.RequestException:
            pass
        out: list[str] = []
        for n in names:
            if n and n not in out:
                out.append(n)
        return out or [CHAT_MODEL]
    if p == "gemini":
        out = []
        for n in GEMINI_MODEL_OPTIONS:
            if n and n not in out:
                out.append(n)
        return out or [GEMINI_MODEL]
    if p in NVIDIA_PROVIDER_IDS:
        out = []
        for n in NVIDIA_MODEL_OPTIONS:
            if n and n not in out:
                out.append(n)
        if p == "nvidia_build" and NVIDIA_BUILD_MODEL and NVIDIA_BUILD_MODEL not in out:
            out.insert(0, NVIDIA_BUILD_MODEL)
        return out or [NVIDIA_MODEL]
    return [CHAT_MODEL]


def _nvidia_creds(provider: str) -> tuple[str, str]:
    """Return (api_key, model) for a NVIDIA provider id."""
    p = normalize_provider(provider)
    if p == "nvidia_build":
        return NVIDIA_BUILD_API_KEY, resolve_model(p)
    return NVIDIA_API_KEY, resolve_model(p)


def provider_ready(provider: str) -> tuple[bool, str]:
    """Return (ok, hint) for UI health checks."""
    p = normalize_provider(provider)
    model = resolve_model(p)
    if p == "ollama":
        try:
            r = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
            r.raise_for_status()
            names = [m.get("name") for m in r.json().get("models", [])]
            if model in names or any(model in (n or "") for n in names):
                return True, model
            return False, f"Pull model: ollama pull {model}"
        except requests.RequestException as exc:
            return False, f"Ollama unreachable ({exc})"
    if p == "gemini":
        if not GEMINI_API_KEY:
            return False, "Set GEMINI_API_KEY in .env"
        return True, model
    if p in NVIDIA_PROVIDER_IDS:
        key, _ = _nvidia_creds(p)
        env_name = (
            "NVIDIA_BUILD_API_KEY" if p == "nvidia_build" else "NVIDIA_API_KEY"
        )
        if not key:
            return False, f"Set {env_name} in .env"
        return True, model
    return False, f"Unknown provider: {provider}"


def generate(
    prompt: str,
    *,
    provider: str = "ollama",
    system: str = "",
    temperature: float = LLM_TEMPERATURE,
    num_predict: int = 280,
    model: str | None = None,
) -> str:
    p = normalize_provider(provider)
    if p == "ollama":
        return _ollama_generate(
            prompt,
            system=system,
            temperature=temperature,
            num_predict=num_predict,
            model=resolve_model(p, model),
        )
    if p == "gemini":
        return _gemini_generate(
            prompt,
            system=system,
            temperature=temperature,
            num_predict=num_predict,
            model=resolve_model(p, model),
        )
    if p not in NVIDIA_PROVIDER_IDS:
        raise ProviderError(f"Unknown provider: {provider}")
    return _nvidia_generate(
        prompt,
        system=system,
        temperature=temperature,
        num_predict=num_predict,
        model=resolve_model(p, model),
        provider=p,
    )


def stream(
    prompt: str,
    *,
    provider: str = "ollama",
    system: str = "",
    temperature: float = LLM_TEMPERATURE,
    num_predict: int = 280,
    model: str | None = None,
) -> Iterator[str]:
    p = normalize_provider(provider)
    resolved = resolve_model(p, model)
    if p == "ollama":
        yield from _ollama_stream(
            prompt,
            system=system,
            temperature=temperature,
            num_predict=num_predict,
            model=resolved,
        )
        return
    if p == "gemini":
        text = _gemini_generate(
            prompt,
            system=system,
            temperature=temperature,
            num_predict=num_predict,
            model=resolved,
        )
        if text:
            yield text
        return
    if p not in NVIDIA_PROVIDER_IDS:
        raise ProviderError(f"Unknown provider: {provider}")
    yield from _nvidia_stream(
        prompt,
        system=system,
        temperature=temperature,
        num_predict=num_predict,
        model=resolved,
        provider=p,
    )


def _ollama_generate(
    prompt: str,
    *,
    system: str,
    temperature: float,
    num_predict: int,
    model: str,
) -> str:
    ok, hint = provider_ready("ollama")
    if not ok:
        raise ProviderError(hint)
    body: dict = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": num_predict,
        },
    }
    if system.strip():
        body["system"] = system
    r = requests.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json=body,
        timeout=180,
    )
    r.raise_for_status()
    return (r.json().get("response") or "").strip()


def _ollama_stream(
    prompt: str,
    *,
    system: str,
    temperature: float,
    num_predict: int,
    model: str,
) -> Iterator[str]:
    ok, hint = provider_ready("ollama")
    if not ok:
        raise ProviderError(hint)
    body: dict = {
        "model": model,
        "prompt": prompt,
        "stream": True,
        "options": {
            "temperature": temperature,
            "num_predict": num_predict,
        },
    }
    if system.strip():
        body["system"] = system
    with requests.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json=body,
        timeout=180,
        stream=True,
    ) as r:
        r.raise_for_status()
        for line in r.iter_lines(decode_unicode=True):
            if not line:
                continue
            try:
                import json

                data = json.loads(line)
            except Exception:  # noqa: BLE001
                continue
            chunk = data.get("response") or ""
            if chunk:
                yield chunk
            if data.get("done"):
                break


def _gemini_generate(
    prompt: str,
    *,
    system: str,
    temperature: float,
    num_predict: int,
    model: str,
) -> str:
    if not GEMINI_API_KEY:
        raise ProviderError("Set GEMINI_API_KEY in .env")
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent"
    )
    contents = [{"role": "user", "parts": [{"text": prompt}]}]
    payload: dict = {
        "contents": contents,
        "generationConfig": {
            "temperature": temperature,
            # Flash/reasoning models may spend tokens on thoughts first
            "maxOutputTokens": max(256, int(num_predict)),
        },
    }
    if system.strip():
        payload["systemInstruction"] = {"parts": [{"text": system}]}
    r = requests.post(
        url,
        headers={
            "Content-Type": "application/json",
            "X-goog-api-key": GEMINI_API_KEY,
        },
        json=payload,
        timeout=180,
    )
    if r.status_code >= 400:
        raise ProviderError(f"Gemini error {r.status_code}: {r.text[:300]}")
    data = r.json()
    try:
        cand = data["candidates"][0]
        parts = (cand.get("content") or {}).get("parts") or []
        text = "".join(p.get("text", "") for p in parts).strip()
        if text:
            return text
        raise ProviderError(
            f"Empty Gemini content (finish={cand.get('finishReason')}). "
            "Try raising max tokens or switching GEMINI_MODEL."
        )
    except ProviderError:
        raise
    except (KeyError, IndexError, TypeError) as exc:
        raise ProviderError(f"Unexpected Gemini response: {data}") from exc


def _nvidia_client(provider: str = "nvidia"):
    key, _ = _nvidia_creds(provider)
    env_name = (
        "NVIDIA_BUILD_API_KEY" if provider == "nvidia_build" else "NVIDIA_API_KEY"
    )
    if not key:
        raise ProviderError(f"Set {env_name} in .env")
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise ProviderError(
            "Install openai package: pip install openai"
        ) from exc
    return OpenAI(base_url=NVIDIA_BASE_URL, api_key=key)


def _nvidia_messages(system: str, prompt: str) -> list[dict]:
    messages: list[dict] = []
    if system.strip():
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    return messages


def _nvidia_max_tokens(num_predict: int) -> int:
    # NVIDIA glm uses a large ceiling; ignore tiny local Ollama budgets
    return max(64, int(num_predict), int(NVIDIA_MAX_TOKENS))


def _nvidia_generate(
    prompt: str,
    *,
    system: str,
    temperature: float,
    num_predict: int,
    model: str,
    provider: str = "nvidia",
) -> str:
    client = _nvidia_client(provider)
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=_nvidia_messages(system, prompt),
            temperature=temperature,
            top_p=NVIDIA_TOP_P,
            max_tokens=_nvidia_max_tokens(num_predict),
            seed=NVIDIA_SEED,
            stream=False,
        )
    except Exception as exc:  # noqa: BLE001
        raise ProviderError(f"NVIDIA error: {exc}") from exc
    try:
        return (completion.choices[0].message.content or "").strip()
    except (AttributeError, IndexError, TypeError) as exc:
        raise ProviderError(f"Unexpected NVIDIA response: {completion}") from exc


def _nvidia_stream(
    prompt: str,
    *,
    system: str,
    temperature: float,
    num_predict: int,
    model: str,
    provider: str = "nvidia",
) -> Iterator[str]:
    client = _nvidia_client(provider)
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=_nvidia_messages(system, prompt),
            temperature=temperature,
            top_p=NVIDIA_TOP_P,
            max_tokens=_nvidia_max_tokens(num_predict),
            seed=NVIDIA_SEED,
            stream=True,
        )
    except Exception as exc:  # noqa: BLE001
        raise ProviderError(f"NVIDIA error: {exc}") from exc

    for chunk in completion:
        if not getattr(chunk, "choices", None):
            continue
        if len(chunk.choices) == 0:
            continue
        delta = getattr(chunk.choices[0], "delta", None)
        if delta is None:
            continue
        content = getattr(delta, "content", None)
        if content is not None:
            yield content
            continue
        # Some NVIDIA reasoning models stream thinking separately
        reasoning = getattr(delta, "reasoning_content", None)
        if reasoning:
            continue
