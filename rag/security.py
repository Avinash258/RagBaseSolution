"""Safety helpers: HTML escape and secret redaction before KB save."""

from __future__ import annotations

import re
from html import escape as html_escape
from urllib.parse import urlparse

SECRET_PATTERNS = [
    re.compile(r"Bearer\s+[A-Za-z0-9._\-]+", re.I),
    re.compile(r"api[_-]?key\s*[:=]\s*\S+", re.I),
    re.compile(r"password\s*[:=]\s*\S+", re.I),
    re.compile(r"secret\s*[:=]\s*\S+", re.I),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
]


def escape_html(value: object) -> str:
    return html_escape(str(value or ""), quote=True)


def redact_secrets(text: str) -> str:
    out = text or ""
    for pat in SECRET_PATTERNS:
        out = pat.sub("[REDACTED]", out)
    return out


def has_trainable_body(learned_markdown: str, *, min_chars: int = 80) -> bool:
    text = (learned_markdown or "").strip()
    if len(text) < min_chars:
        return False
    # Link-only / empty body heuristics
    lowered = text.lower()
    if "no page body" in lowered or "could not fetch" in lowered:
        return False
    # Require some non-URL substance
    without_urls = re.sub(r"https?://\S+", "", text)
    without_urls = re.sub(r"\s+", " ", without_urls).strip()
    return len(without_urls) >= min_chars


def source_domain(url: str) -> str:
    try:
        host = (urlparse(url).netloc or "").lower()
    except Exception:  # noqa: BLE001
        return ""
    if host.startswith("www."):
        host = host[4:]
    return host


def is_trainable_url(url: str, allow_domains: set[str] | frozenset[str]) -> bool:
    host = source_domain(url)
    if not host:
        return False
    for domain in allow_domains:
        if host == domain or host.endswith("." + domain) or domain in host:
            return True
    return False
