"""Ingest Playwright docs from web sources into the local knowledge base."""

from __future__ import annotations

import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests

ROOT = Path(__file__).resolve().parent
KNOWLEDGE_DIR = ROOT / "rag" / "knowledge"
UPLOAD_SOURCE = (
    Path.home()
    / ".cursor"
    / "projects"
    / "c-Projectclass"
    / "uploads"
    / "PlaywrightLearning-0.md"
)
# Fallback to agent-tools / local copy if upload path differs
LOCAL_MIRROR = ROOT / "rag" / "sources" / "PlaywrightLearning.md"

PLAYWRIGHT_LEARNING_URL = "https://avinash258.github.io/PlaywrightLearning/"
OFFICIAL_DOCS = [
    "https://playwright.dev/docs/intro",
    "https://playwright.dev/docs/writing-tests",
    "https://playwright.dev/docs/running-tests",
    "https://playwright.dev/docs/test-assertions",
    "https://playwright.dev/docs/locators",
    "https://playwright.dev/docs/actionability",
    "https://playwright.dev/docs/test-fixtures",
    "https://playwright.dev/docs/auth",
    "https://playwright.dev/docs/network",
    "https://playwright.dev/docs/mock",
    "https://playwright.dev/docs/api-testing",
    "https://playwright.dev/docs/pom",
    "https://playwright.dev/docs/trace-viewer-intro",
    "https://playwright.dev/docs/ci",
    "https://playwright.dev/docs/best-practices",
]


class _HTMLToText(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag: str, attrs) -> None:  # noqa: ANN001
        if tag in {"script", "style", "nav", "footer", "noscript"}:
            self._skip += 1
        elif tag in {"h1", "h2", "h3", "h4"} and self._skip == 0:
            level = int(tag[1])
            self.parts.append("\n" + ("#" * level) + " ")
        elif tag in {"p", "li", "pre", "tr"} and self._skip == 0:
            self.parts.append("\n")
        elif tag == "br" and self._skip == 0:
            self.parts.append("\n")
        elif tag == "code" and self._skip == 0:
            self.parts.append("`")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "nav", "footer", "noscript"} and self._skip:
            self._skip -= 1
        elif tag == "code" and self._skip == 0:
            self.parts.append("`")
        elif tag in {"p", "li", "pre", "h1", "h2", "h3", "h4"} and self._skip == 0:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip == 0 and data.strip():
            self.parts.append(data)


def html_to_markdownish(html: str) -> str:
    parser = _HTMLToText()
    parser.feed(html)
    text = "".join(parser.parts)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def fetch_url(url: str, timeout: int = 45) -> str:
    headers = {"User-Agent": "PlaywrightRAGBot/1.0 (+local training)"}
    r = requests.get(url, headers=headers, timeout=timeout)
    r.raise_for_status()
    ctype = r.headers.get("content-type", "")
    if "html" in ctype or url.endswith("/") or ".html" in url:
        return html_to_markdownish(r.text)
    return r.text


def slug_from_url(url: str) -> str:
    path = urlparse(url).path.strip("/").replace("/", "_")
    return path or "index"


def write_knowledge(name: str, title: str, body: str, source_url: str) -> Path:
    KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
    path = KNOWLEDGE_DIR / f"{name}.md"
    content = (
        f"# {title}\n\n"
        f"Source: {source_url}\n\n"
        f"{body.strip()}\n"
    )
    path.write_text(content, encoding="utf-8")
    return path


def ingest_playwright_learning() -> Path:
    """Prefer uploaded/local full study material; fall back to live fetch."""
    candidates = [
        UPLOAD_SOURCE,
        Path(
            r"C:\Users\avinash.sharma.DIGITALA\.cursor\projects\c-Projectclass"
            r"\uploads\PlaywrightLearning-0.md"
        ),
        LOCAL_MIRROR,
    ]
    text = None
    used = None
    for c in candidates:
        if c.exists():
            text = c.read_text(encoding="utf-8")
            used = c
            break
    if text is None:
        print(f"Fetching live: {PLAYWRIGHT_LEARNING_URL}")
        text = fetch_url(PLAYWRIGHT_LEARNING_URL)
        used = PLAYWRIGHT_LEARNING_URL
        LOCAL_MIRROR.parent.mkdir(parents=True, exist_ok=True)
        LOCAL_MIRROR.write_text(text, encoding="utf-8")

    # Drop nav chrome at top if present
    text = re.sub(
        r"(?s)^Source URL:.*?\nTitle:.*?\n",
        "",
        text,
        count=1,
    )
    path = write_knowledge(
        "web_playwright_learning",
        "Playwright + TypeScript Study Material",
        text,
        PLAYWRIGHT_LEARNING_URL,
    )
    print(f"Ingested PlaywrightLearning from {used} -> {path.name}")
    return path


def ingest_official_docs() -> list[Path]:
    written: list[Path] = []
    for url in OFFICIAL_DOCS:
        try:
            print(f"Fetching {url} ...")
            body = fetch_url(url)
            if len(body) < 200:
                print(f"  skip (too short): {url}")
                continue
            name = f"web_official_{slug_from_url(url)}"
            title = f"Playwright Docs — {slug_from_url(url).replace('_', ' ')}"
            path = write_knowledge(name, title, body, url)
            written.append(path)
            print(f"  saved {path.name} ({len(body)} chars)")
        except requests.RequestException as exc:
            print(f"  failed {url}: {exc}")
    return written


def clear_old_seed_docs() -> None:
    """Keep web-trained docs; remove the small original seed set if present."""
    for path in KNOWLEDGE_DIR.glob("0*.md"):
        path.unlink(missing_ok=True)
        print(f"Removed old seed: {path.name}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Train RAG knowledge from websites")
    parser.add_argument("--keep-seed", action="store_true", help="Keep old 01_*.md seeds")
    parser.add_argument("--skip-official", action="store_true")
    parser.add_argument("--skip-learning", action="store_true")
    parser.add_argument("--reindex", action="store_true", help="Rebuild Chroma after ingest")
    args = parser.parse_args()

    if not args.keep_seed:
        clear_old_seed_docs()

    if not args.skip_learning:
        ingest_playwright_learning()
    if not args.skip_official:
        ingest_official_docs()

    files = sorted(KNOWLEDGE_DIR.glob("*.md"))
    print(f"\nKnowledge files: {len(files)}")
    for f in files:
        print(f"  - {f.name}")

    if args.reindex:
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))
        from rag.retriever import ChromaRetriever

        print("\nRebuilding ChromaDB index...")
        retriever = ChromaRetriever(knowledge_dir=KNOWLEDGE_DIR, rebuild=True)
        print(f"Indexed {retriever.count} chunks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
