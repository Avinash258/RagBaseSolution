"""Playwright Testing Chatbot UI."""

from __future__ import annotations

import sys
from pathlib import Path
from urllib.parse import urlparse

import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rag.config import CHAT_MODEL, EMBED_MODEL
from rag.pipeline import PlaywrightRAGBot

st.set_page_config(
    page_title="Playwright Testing Chatbot",
    page_icon="🎭",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700&family=Source+Serif+4:wght@600&display=swap');

html, body, [class*="css"] {
  font-family: "Source Sans 3", sans-serif;
}
.stApp {
  background: linear-gradient(180deg, #f3f6f8 0%, #e9eef2 100%);
}
.block-container {
  max-width: 820px;
  padding-top: 0.6rem !important;
}
.app-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(243, 246, 248, 0.94);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid #d5dee6;
  padding: 0.85rem 0 0.75rem 0;
  margin-bottom: 1rem;
}
.app-title {
  font-family: "Source Serif 4", serif;
  font-size: 1.85rem;
  font-weight: 600;
  color: #15202b;
  margin: 0;
  letter-spacing: -0.02em;
}
.app-sub {
  margin: 0.2rem 0 0 0;
  color: #5a6b7a;
  font-size: 0.95rem;
}
.mode-tag {
  display: inline-block;
  font-size: 0.75rem;
  font-weight: 600;
  color: #1d4f4a;
  background: #dceeea;
  border: 1px solid #b9d8d2;
  padding: 0.15rem 0.55rem;
  border-radius: 6px;
  margin-bottom: 0.5rem;
}
.source-row {
  background: #fff;
  border: 1px solid #d7e0e8;
  border-radius: 10px;
  padding: 0.7rem 0.85rem;
  margin-bottom: 0.45rem;
}
.source-row strong { color: #15202b; }
.source-meta { color: #667788; font-size: 0.8rem; }
.user-q {
  font-size: 1.05rem;
  font-weight: 600;
  color: #15202b;
  margin: 1rem 0 0.4rem 0;
}
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner="Loading chatbot…")
def get_bot() -> PlaywrightRAGBot:
    bot = PlaywrightRAGBot(
        model=CHAT_MODEL,
        embed_model=EMBED_MODEL,
        top_k=3,
        rebuild_index=False,
    )
    warm = getattr(bot, "_warm_llm_quietly", None)
    if callable(warm):
        import threading

        threading.Thread(target=warm, daemon=True).start()
    return bot


bot = get_bot()

# Always-visible heading
st.markdown(
    """
<div class="app-header">
  <h1 class="app-title">Playwright Testing Chatbot</h1>
  <p class="app-sub">Vector DB first · local LLM next · internet if needed</p>
</div>
""",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.subheader("Status")
    st.write("Ollama:", "✅" if bot.llm.is_available() else "❌")
    st.write("Model:", bot.llm.model)
    st.write("Indexed chunks:", bot.retriever.count)
    st.write("History:", len(bot.history.list_entries(limit=5000)))
    st.markdown(
        "1. Search vector DB  \n"
        "2. Local LLM if weak  \n"
        "3. Internet if LLM fails  \n"
        "4. Mark **Correct** to train KB"
    )
    if st.button("Rebuild index"):
        with st.spinner("Re-embedding…"):
            n = bot.retriever.rebuild()
        st.success(f"{n} chunks")
        st.cache_resource.clear()
        st.rerun()
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()

    pending = bot.history.pending_correctable(limit=6)
    if pending:
        st.subheader("Save if correct")
        for entry in pending:
            st.caption(f"`{entry.get('mode')}` {(entry.get('question') or '')[:48]}")
            if st.button("Save to KB", key=f"side_{entry['id']}"):
                out = bot.mark_correct_and_train(entry["id"])
                if out.get("ok"):
                    st.success(f"+{out.get('trained_chunks', 0)} chunks")
                    st.rerun()
                else:
                    st.error(out.get("error"))


def _host(url: str) -> str:
    if not url:
        return ""
    try:
        return urlparse(url).netloc or url
    except Exception:  # noqa: BLE001
        return url


def render_sources(sources: list[dict]) -> None:
    if not sources:
        return
    with st.expander(f"Sources ({len(sources)})", expanded=False):
        for src in sources:
            url = src.get("url") or ""
            link = url if str(url).startswith("http") else ""
            title = src.get("title") or src.get("source") or "Source"
            n = src.get("n", "")
            preview = (src.get("preview") or "")[:180]
            meta = _host(link) or src.get("source", "")
            score = src.get("score")
            if isinstance(score, (int, float)) and 0 < score <= 1.05:
                meta = f"{meta} · {score:.2f}"
            st.markdown(
                f'<div class="source-row"><strong>[{n}] {title}</strong>'
                f'<div class="source-meta">{meta}</div>'
                f'<div>{preview}</div></div>',
                unsafe_allow_html=True,
            )
            if link:
                st.markdown(f"[Open source]({link})")


def render_result(msg: dict, idx: int) -> None:
    labels = {
        "rag": "Vector DB",
        "llm": "Local LLM",
        "llm_grounded": "LLM + RAG",
        "internet": "Internet",
        "none": "No answer",
    }
    mode = msg.get("mode", "")
    st.markdown(
        f'<span class="mode-tag">{labels.get(mode, mode)}</span>',
        unsafe_allow_html=True,
    )
    st.markdown(msg.get("content", ""))
    render_sources(msg.get("sources") or [])

    followups = [f for f in (msg.get("followups") or []) if "Save this answer" not in f]
    if followups:
        st.caption("Related questions")
        cols = st.columns(min(3, len(followups)))
        for j, fq in enumerate(followups):
            with cols[j % len(cols)]:
                if st.button(fq, key=f"fu_{idx}_{j}"):
                    st.session_state.pending_query = fq
                    st.rerun()

    if msg.get("can_save_to_kb") and msg.get("history_id") and not msg.get("saved_to_kb"):
        if st.button(
            "Correct — save to knowledge base",
            key=f"save_{msg['history_id']}_{idx}",
        ):
            with st.spinner("Saving to vector DB…"):
                out = bot.mark_correct_and_train(msg["history_id"])
            if out.get("ok"):
                st.session_state.messages[idx]["saved_to_kb"] = True
                st.success(f"Added {out.get('trained_chunks', 0)} chunks")
                st.rerun()
            else:
                st.error(out.get("error", "Save failed"))
    elif msg.get("saved_to_kb"):
        st.success("Saved to knowledge base")


if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_query" not in st.session_state:
    st.session_state.pending_query = ""

if not st.session_state.messages:
    st.write("Try one of these:")
    suggestions = [
        "How do I use getByRole locators?",
        "Mock an API with page.route",
        "Reuse login with storageState",
        "Debug flaky tests with Trace Viewer",
    ]
    c1, c2 = st.columns(2)
    for i, s in enumerate(suggestions):
        with (c1 if i % 2 == 0 else c2):
            if st.button(s, key=f"sug_{i}"):
                st.session_state.pending_query = s
                st.rerun()

for i, msg in enumerate(st.session_state.messages):
    if msg["role"] == "user":
        st.markdown(
            f'<p class="user-q">{msg["content"]}</p>',
            unsafe_allow_html=True,
        )
    else:
        with st.chat_message("assistant"):
            render_result(msg, i)

prompt = st.chat_input("Ask about Playwright testing…")
query = prompt or st.session_state.pending_query
if query:
    st.session_state.pending_query = ""
    st.session_state.messages.append({"role": "user", "content": query})
    with st.spinner("Working…"):
        try:
            result = bot.ask(query)
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": result.get("answer") or "_No response._",
                    "sources": result.get("sources") or [],
                    "mode": result.get("mode"),
                    "best_score": result.get("best_score"),
                    "history_id": result.get("history_id"),
                    "can_save_to_kb": bool(result.get("can_save_to_kb")),
                    "saved_to_kb": False,
                    "followups": result.get("followups") or [],
                }
            )
            st.rerun()
        except Exception as exc:  # noqa: BLE001
            st.error(f"Error: {exc}")
            st.session_state.messages.append(
                {"role": "assistant", "content": f"Error: {exc}", "sources": []}
            )
