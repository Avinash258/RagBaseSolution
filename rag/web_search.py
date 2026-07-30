"""Web fallback when RAG misses: Google (if available) + Playwright docs learn."""

from __future__ import annotations

import hashlib
import html as html_lib
import os
import re
from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.parse import parse_qs, quote_plus, unquote, urlparse

import requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

BLOCKED_HOSTS = {
    "accounts.google.com",
    "support.google.com",
    "policies.google.com",
    "maps.google.com",
    "youtube.com",
    "www.youtube.com",
    "webcache.googleusercontent.com",
}

# Official docs catalog used when Google HTML is blocked (common on corp networks)
PLAYWRIGHT_DOCS = {
    "https://playwright.dev/docs/intro": "install setup npm init playwright",
    "https://playwright.dev/docs/writing-tests": "write first test expect page goto",
    "https://playwright.dev/docs/running-tests": "run headed ui debug workers project",
    "https://playwright.dev/docs/test-assertions": "assert expect soft toBeVisible toHaveText",
    "https://playwright.dev/docs/locators": "locator getByRole getByLabel getByTestId selector",
    "https://playwright.dev/docs/actionability": "auto wait actionability attached visible enabled stable",
    "https://playwright.dev/docs/test-fixtures": "fixture extend beforeEach worker",
    "https://playwright.dev/docs/auth": "authentication login storageState reuse session",
    "https://playwright.dev/docs/network": "network request response intercept",
    "https://playwright.dev/docs/mock": "mock route fulfill abort api mock",
    "https://playwright.dev/docs/api-testing": "api request context post get",
    "https://playwright.dev/docs/pom": "page object model pom class",
    "https://playwright.dev/docs/trace-viewer-intro": "trace viewer debug timeline",
    "https://playwright.dev/docs/ci": "ci github actions pipeline",
    "https://playwright.dev/docs/best-practices": "best practices flaky isolation",
    "https://playwright.dev/docs/screenshots": "screenshot visual",
    "https://playwright.dev/docs/videos": "video record",
    "https://playwright.dev/docs/downloads": "download saveAs",
    "https://playwright.dev/docs/navigations": "navigation goto waitForURL",
    "https://playwright.dev/docs/frames": "iframe frameLocator",
    "https://playwright.dev/docs/dialogs": "dialog alert confirm prompt",
    "https://playwright.dev/docs/pages": "page context browser",
    "https://playwright.dev/docs/test-parallel": "parallel workers shard",
    "https://playwright.dev/docs/test-retries": "retry flaky",
    "https://playwright.dev/docs/test-timeouts": "timeout",
    "https://avinash258.github.io/PlaywrightLearning/": (
        "typescript study roadmap cheat sheet interview quiz"
    ),
}


@dataclass
class WebHit:
    title: str
    url: str
    snippet: str
    body: str = ""


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag: str, attrs) -> None:  # noqa: ANN001
        if tag in {"script", "style", "nav", "footer", "noscript", "svg", "header"}:
            self._skip += 1
        elif tag in {"p", "li", "h1", "h2", "h3", "h4", "pre", "code", "br"} and self._skip == 0:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "nav", "footer", "noscript", "svg", "header"} and self._skip:
            self._skip -= 1
        elif tag in {"p", "li", "h1", "h2", "h3", "h4", "pre"} and self._skip == 0:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip == 0 and data.strip():
            self.parts.append(data)


def html_to_text(raw_html: str) -> str:
    parser = _TextExtractor()
    try:
        parser.feed(raw_html)
    except Exception:  # noqa: BLE001
        return ""
    text = html_lib.unescape("".join(parser.parts))
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def google_search_url(question: str) -> str:
    return (
        "https://www.google.com/search?q="
        + quote_plus(f"playwright {question}")
        + "&hl=en"
    )


def search_google_cse(question: str, max_results: int = 5) -> list[WebHit]:
    """Optional official Google Custom Search JSON API."""
    api_key = os.getenv("GOOGLE_API_KEY", "").strip()
    cse_id = os.getenv("GOOGLE_CSE_ID", "").strip()
    if not api_key or not cse_id:
        return []
    try:
        r = requests.get(
            "https://www.googleapis.com/customsearch/v1",
            params={
                "key": api_key,
                "cx": cse_id,
                "q": f"playwright {question}",
                "num": min(max_results, 10),
            },
            timeout=20,
        )
        r.raise_for_status()
        items = r.json().get("items") or []
        return [
            WebHit(
                title=item.get("title") or item.get("link") or "Google result",
                url=item.get("link") or "",
                snippet=item.get("snippet") or "",
            )
            for item in items
            if item.get("link")
        ]
    except requests.RequestException:
        return []


def search_google_html(question: str, max_results: int = 5) -> list[WebHit]:
    """Best-effort Google HTML scrape (often blocked by JS/consent walls)."""
    session = requests.Session()
    session.headers.update(HEADERS)
    session.cookies.set("CONSENT", "YES+cb.20210328-17-p0.en+FX+410", domain=".google.com")
    try:
        resp = session.get(
            "https://www.google.com/search",
            params={
                "q": f"playwright {question}",
                "hl": "en",
                "num": max_results,
                "gbv": "1",
            },
            timeout=20,
        )
        resp.raise_for_status()
    except requests.RequestException:
        return []
    return _parse_google_results(resp.text, max_results=max_results)


def _parse_google_results(html: str, max_results: int) -> list[WebHit]:
    hits: list[WebHit] = []
    seen: set[str] = set()

    patterns = [
        r'href="(/url\?q=[^"&]+)"[^>]*>(.*?)</a>',
        r'href="(https?://(?!www\.google\.)[^"]+)"[^>]*>(.*?)</a>',
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, html, flags=re.I | re.S):
            href = match.group(1)
            title = re.sub(r"<[^>]+>", "", match.group(2))
            title = html_lib.unescape(title).strip()
            resolved = _resolve_google_href(href)
            if not resolved or resolved in seen:
                continue
            host = urlparse(resolved).netloc.lower()
            if any(host.endswith(b) or host == b for b in BLOCKED_HOSTS):
                continue
            if "google." in host:
                continue
            if len(title) < 3:
                title = resolved
            seen.add(resolved)
            hits.append(WebHit(title=title, url=resolved, snippet=""))
            if len(hits) >= max_results:
                return hits
    return hits


def _resolve_google_href(href: str) -> str | None:
    if href.startswith("/url?"):
        qs = parse_qs(urlparse(href).query)
        target = (qs.get("q") or qs.get("url") or [None])[0]
        return unquote(target) if target else None
    if href.startswith("http"):
        return href
    return None


def search_docs_catalog(question: str, max_results: int = 3) -> list[WebHit]:
    """Rank official Playwright docs by keyword overlap with the question."""
    tokens = set(re.findall(r"[a-z0-9_\.]{3,}", question.lower()))
    if not tokens:
        return []
    scored: list[tuple[int, str, str]] = []
    for url, keywords in PLAYWRIGHT_DOCS.items():
        keys = set(keywords.split())
        score = len(tokens & keys)
        # Boost exact API-ish tokens present in URL slug
        slug = urlparse(url).path.lower()
        score += sum(1 for t in tokens if t in slug)
        if score > 0:
            title = slug.strip("/").replace("docs/", "").replace("-", " ").title() or url
            scored.append((score, url, title))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [
        WebHit(title=title, url=url, snippet="official docs match")
        for _, url, title in scored[:max_results]
    ]


def fetch_page_text(url: str, max_chars: int = 5000) -> str:
    # Prefer Jina readable markdown for cleaner text when available
    try:
        jina = requests.get(
            f"https://r.jina.ai/{url}",
            headers={"User-Agent": "PlaywrightRAGBot/1.0", "Accept": "text/plain"},
            timeout=35,
        )
        if jina.status_code == 200 and len(jina.text) > 200:
            text = jina.text.strip()
            # Strip jina metadata headers if present
            if text.startswith("Title:"):
                parts = text.split("\n\n", 1)
                text = parts[1] if len(parts) > 1 else text
            return text[:max_chars]
    except requests.RequestException:
        pass

    try:
        resp = requests.get(url, headers=HEADERS, timeout=25)
        resp.raise_for_status()
        ctype = resp.headers.get("content-type", "")
        if "html" not in ctype and "text" not in ctype and "markdown" not in ctype:
            return ""
        return html_to_text(resp.text)[:max_chars]
    except requests.RequestException:
        return ""


def gather_web_answer(question: str, max_pages: int = 3) -> dict:
    """
    Find an answer on the web when RAG misses, then return content to train Chroma.
    Order: Google CSE → Google HTML → official Playwright docs catalog.
    """
    google_url = google_search_url(question)
    engine = "none"
    hits = search_google_cse(question, max_results=max_pages + 2)
    if hits:
        engine = "google_cse"
    else:
        hits = search_google_html(question, max_results=max_pages + 2)
        if hits:
            engine = "google_html"

    if not hits:
        hits = search_docs_catalog(question, max_results=max_pages)
        engine = "playwright_docs" if hits else "none"

    if not hits:
        return {
            "ok": False,
            "answer": "",
            "sources": [],
            "learned_markdown": "",
            "engine": "none",
            "google_url": google_url,
        }

    filled: list[WebHit] = []
    for hit in hits:
        body = fetch_page_text(hit.url)
        if len(body) < 120:
            continue
        hit.body = body
        filled.append(hit)
        if len(filled) >= max_pages:
            break

    if not filled:
        lines = [
            f"**Web search** (`{engine}`)",
            "",
            f"[Open Google search]({google_url})",
            "",
            "Found links but could not fetch page text:",
            "",
        ]
        for i, hit in enumerate(hits[:max_pages], start=1):
            lines.append(f"{i}. [{hit.title}]({hit.url})")
        return {
            "ok": True,
            "answer": "\n".join(lines),
            "sources": [{"title": h.title, "url": h.url} for h in hits[:max_pages]],
            "learned_markdown": "",
            "engine": engine,
            "google_url": google_url,
        }

    label = {
        "google_cse": "Google",
        "google_html": "Google",
        "playwright_docs": "Playwright docs (Google HTML blocked on this network)",
    }.get(engine, engine)

    answer_parts = [
        f"**From web — {label}** (training vector DB)",
        "",
        f"[Google search for this question]({google_url})",
        "",
        f"### {filled[0].title}",
        filled[0].body[:1800],
        "",
        "### Sources",
    ]
    for hit in filled:
        answer_parts.append(f"- [{hit.title}]({hit.url})")

    md_parts = [
        f"# Web learned: {question}",
        "",
        f"Original question: {question}",
        f"Engine: {engine}",
        f"Google: {google_url}",
        "",
    ]
    for hit in filled:
        md_parts.append(f"## {hit.title}")
        md_parts.append(f"Source: {hit.url}")
        md_parts.append("")
        md_parts.append(hit.body[:3500])
        md_parts.append("")

    return {
        "ok": True,
        "answer": "\n".join(answer_parts),
        "sources": [{"title": h.title, "url": h.url} for h in filled],
        "learned_markdown": "\n".join(md_parts).strip(),
        "engine": engine,
        "google_url": google_url,
        "question": question,
    }


def learned_filename(question: str) -> str:
    digest = hashlib.sha1(question.encode("utf-8")).hexdigest()[:10]
    slug = re.sub(r"[^a-z0-9]+", "_", question.lower()).strip("_")[:40] or "query"
    return f"web_learned_{slug}_{digest}.md"
