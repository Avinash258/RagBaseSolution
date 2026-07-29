"""Playwright Testing Chatbot UI — NEW VISION / SoftServe look & feel."""

from __future__ import annotations

import base64
import sys
from pathlib import Path
from urllib.parse import urlparse

import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rag.config import CHAT_MODEL, EMBED_MODEL, FRAMEWORK
from rag.history import AnswerHistory
from rag.pipeline import PlaywrightRAGBot

LOGO_PATH = ROOT / "assets" / "new-vision-logo.png"


def _logo_data_uri() -> str:
    if not LOGO_PATH.exists():
        return ""
    data = base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{data}"


st.set_page_config(
    page_title="NEW VISION · Playwright Chatbot",
    page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else "▶",
    layout="centered",
    initial_sidebar_state="expanded",
)

# SoftServe NEW VISION palette
NV_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600;700&family=Outfit:wght@500;600;700&display=swap');

:root {
  --nv-ink: #3d3f42;
  --nv-ink-soft: #5c5f63;
  --nv-muted: #7a7e83;
  --nv-orange: #f8971d;
  --nv-yellow: #ffd200;
  --nv-gold: #c69214;
  --nv-navy: #005587;
  --nv-cyan: #00a3e0;
  --nv-bg0: #eef6fb;
  --nv-bg1: #f7fbfd;
  --nv-card: #ffffff;
  --nv-line: #d5e4ef;
}

html, body, [class*="css"], .stMarkdown, .stText, .stCaption {
  font-family: "Barlow", sans-serif !important;
  color: var(--nv-ink);
}

.stApp {
  background:
    radial-gradient(ellipse 80% 50% at 100% 0%, rgba(0, 163, 224, 0.12), transparent 55%),
    radial-gradient(ellipse 60% 40% at 0% 100%, rgba(248, 151, 29, 0.10), transparent 50%),
    linear-gradient(165deg, var(--nv-bg0) 0%, var(--nv-bg1) 45%, #ffffff 100%);
}

.block-container {
  max-width: 880px;
  padding-top: 0.4rem !important;
  padding-bottom: 2.5rem !important;
}

/* Let sticky header work inside Streamlit's scroll container */
html, body {
  overflow: auto !important;
}
[data-testid="stAppViewContainer"] {
  overflow-y: auto !important;
  height: 100vh !important;
}
section.main,
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
.main .block-container,
div[data-testid="stVerticalBlock"] {
  overflow: visible !important;
}

/* Pin the markdown wrapper that contains the brand header */
div[data-testid="stMarkdownContainer"]:has(.app-header),
div[data-testid="stElementContainer"]:has(.app-header) {
  position: sticky !important;
  top: 0 !important;
  z-index: 1000 !important;
  background: rgba(247, 251, 253, 0.97) !important;
}

/* Sidebar brand panel */
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #f4f9fc 0%, #eaf3f9 100%) !important;
  border-right: 1px solid var(--nv-line);
}
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {
  font-family: "Outfit", sans-serif !important;
  color: var(--nv-navy) !important;
  letter-spacing: 0.02em;
}

/* Center brand header — frozen (sticky) while chat scrolls */
.app-header {
  position: sticky !important;
  top: 0 !important;
  z-index: 1000 !important;
  background: rgba(247, 251, 253, 0.97) !important;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 3px solid transparent;
  border-image: linear-gradient(
    90deg,
    var(--nv-orange) 0%,
    var(--nv-yellow) 25%,
    var(--nv-gold) 50%,
    var(--nv-navy) 75%,
    var(--nv-cyan) 100%
  ) 1;
  padding: 0.75rem 0.25rem 0.9rem 0.25rem;
  margin: 0 0 1.15rem 0;
  display: flex;
  align-items: center;
  gap: 1.1rem;
  box-shadow: 0 6px 18px rgba(0, 85, 135, 0.08);
}

.app-header img.nv-logo {
  height: 72px;
  width: auto;
  display: block;
  flex-shrink: 0;
}

.app-header-copy {
  min-width: 0;
}

.app-kicker {
  font-family: "Outfit", sans-serif;
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--nv-cyan);
  margin: 0 0 0.15rem 0;
}

.app-title {
  font-family: "Outfit", sans-serif;
  font-size: 1.65rem;
  font-weight: 700;
  color: var(--nv-ink);
  margin: 0;
  letter-spacing: -0.02em;
  line-height: 1.15;
}

.app-sub {
  margin: 0.28rem 0 0 0;
  color: var(--nv-muted);
  font-size: 0.92rem;
  font-weight: 500;
}

.nv-chevron {
  display: inline-block;
  width: 0;
  height: 0;
  margin-right: 0.35rem;
  border-top: 0.35rem solid transparent;
  border-bottom: 0.35rem solid transparent;
  border-left: 0.55rem solid var(--nv-orange);
}

.mode-tag {
  display: inline-block;
  font-family: "Outfit", sans-serif;
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--nv-navy);
  background: rgba(0, 163, 224, 0.12);
  border: 1px solid rgba(0, 133, 182, 0.28);
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
  margin-bottom: 0.55rem;
}

.source-row {
  background: var(--nv-card);
  border: 1px solid var(--nv-line);
  border-left: 3px solid var(--nv-cyan);
  border-radius: 8px;
  padding: 0.7rem 0.85rem;
  margin-bottom: 0.45rem;
  box-shadow: 0 1px 0 rgba(0, 85, 135, 0.04);
}
.source-row strong { color: var(--nv-ink); }
.source-meta { color: var(--nv-muted); font-size: 0.8rem; }

.user-q {
  font-family: "Outfit", sans-serif;
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--nv-navy);
  margin: 1rem 0 0.4rem 0;
  padding-left: 0.65rem;
  border-left: 3px solid var(--nv-orange);
}

.nv-footer {
  margin-top: 1.5rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--nv-line);
  font-size: 0.78rem;
  color: var(--nv-muted);
  letter-spacing: 0.04em;
}

/* Primary buttons — SoftServe cyan/navy */
div.stButton > button[kind="primary"],
div.stButton > button {
  font-family: "Barlow", sans-serif !important;
  font-weight: 600 !important;
  border-radius: 6px !important;
  border: 1px solid rgba(0, 85, 135, 0.22) !important;
  background: linear-gradient(180deg, #ffffff 0%, #f0f7fb 100%) !important;
  color: var(--nv-navy) !important;
  transition: border-color 0.15s ease, box-shadow 0.15s ease, transform 0.12s ease;
}
div.stButton > button:hover {
  border-color: var(--nv-cyan) !important;
  box-shadow: 0 2px 10px rgba(0, 163, 224, 0.18) !important;
  transform: translateY(-1px);
}

/* Chat input */
[data-testid="stChatInput"] textarea {
  border-radius: 10px !important;
}
[data-testid="stChatInput"] > div {
  border-color: var(--nv-line) !important;
}

/* Soften default chat bubbles */
[data-testid="stChatMessage"] {
  background: rgba(255, 255, 255, 0.72) !important;
  border: 1px solid var(--nv-line);
  border-radius: 12px;
  padding: 0.35rem 0.5rem;
}

.nv-sidebar-logo {
  display: block;
  width: 100%;
  max-width: 200px;
  margin: 0.2rem auto 0.85rem auto;
}
.nv-tagline {
  text-align: center;
  font-family: "Outfit", sans-serif;
  font-size: 0.68rem;
  font-weight: 600;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--nv-ink-soft);
  margin: -0.4rem 0 1rem 0;
}
.nv-steps {
  background: #fff;
  border: 1px solid var(--nv-line);
  border-radius: 10px;
  padding: 0.7rem 0.85rem;
  font-size: 0.88rem;
  line-height: 1.45;
}

.nv-suggestions {
  margin: 0.35rem 0 1rem 0;
  padding: 0.85rem 1rem 0.95rem 1rem;
  background: rgba(255, 255, 255, 0.82);
  border: 1px solid var(--nv-line);
  border-radius: 12px;
  border-top: 3px solid var(--nv-cyan);
}
.nv-suggestions-title {
  font-family: "Outfit", sans-serif;
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--nv-ink);
  margin: 0 0 0.55rem 0;
}
.nv-suggestions-hold {
  font-size: 0.8rem;
  color: var(--nv-muted);
  margin: 0 0 0.65rem 0;
}

.nv-feedback {
  margin-top: 0.85rem;
  padding: 0.75rem 0.9rem;
  background: linear-gradient(180deg, #ffffff 0%, #f3f8fb 100%);
  border: 1px solid var(--nv-line);
  border-radius: 10px;
  border-left: 3px solid var(--nv-orange);
}
.nv-feedback-title {
  font-family: "Outfit", sans-serif;
  font-size: 0.82rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--nv-navy);
  margin: 0 0 0.35rem 0;
}
.nv-feedback-hint {
  font-size: 0.85rem;
  color: var(--nv-muted);
  margin: 0 0 0.55rem 0;
}
.nv-feedback-done {
  font-size: 0.9rem;
  color: var(--nv-navy);
  font-weight: 600;
  margin: 0;
}
</style>
"""

st.markdown(NV_CSS, unsafe_allow_html=True)


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
_logo_uri = _logo_data_uri()

# Brand header
if _logo_uri:
    st.markdown(
        f"""
<div class="app-header">
  <img class="nv-logo" src="{_logo_uri}" alt="NEW VISION — A SoftServe Company" />
  <div class="app-header-copy">
    <p class="app-kicker">Think forward</p>
    <h1 class="app-title">Playwright Testing Chatbot</h1>
    <p class="app-sub"><span class="nv-chevron"></span>Vector DB → Qwen → satisfied? → internet if needed</p>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
<div class="app-header">
  <div class="app-header-copy">
    <p class="app-kicker">NEW VISION · SoftServe</p>
    <h1 class="app-title">Playwright Testing Chatbot</h1>
    <p class="app-sub">Vector DB → Qwen → satisfied? → internet if needed</p>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), use_container_width=True)
        st.markdown(
            '<p class="nv-tagline">Think forward</p>',
            unsafe_allow_html=True,
        )
    st.subheader("Status")
    st.write("Framework:", FRAMEWORK)
    st.write("Ollama:", "✅" if bot.llm.is_available() else "❌")
    st.write("Model:", bot.llm.model)
    st.write("Indexed chunks:", bot.retriever.count)
    st.write("History:", len(bot.history.list_entries(limit=5000)))
    st.markdown(
        '<div class="nv-steps">'
        "1. Search vector DB<br/>"
        "2. Qwen LLM if weak<br/>"
        "3. Ask if you are <strong>satisfied</strong><br/>"
        "4. Internet only if <strong>not satisfied</strong><br/>"
        "5. Mark <strong>Correct</strong> to train KB"
        "</div>",
        unsafe_allow_html=True,
    )
    st.caption(f"Pull model: `ollama pull {CHAT_MODEL}`")
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


def render_feedback(msg: dict, idx: int) -> None:
    """Feedback on this response — rating + optional comment."""
    history_id = msg.get("history_id")
    if not history_id:
        return

    fb = msg.get("feedback") or {}
    if fb.get("rating"):
        label = (
            "Helpful"
            if fb.get("rating") == "helpful"
            else "Not helpful"
        )
        comment = (fb.get("comment") or "").strip()
        extra = f" — {comment}" if comment else ""
        st.markdown(
            f'<div class="nv-feedback"><p class="nv-feedback-done">'
            f'Thanks for your feedback: <strong>{label}</strong>{extra}'
            f"</p></div>",
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        '<div class="nv-feedback">'
        '<p class="nv-feedback-title">Feedback on this response</p>'
        '<p class="nv-feedback-hint">Was this answer useful for your Playwright question?</p>'
        "</div>",
        unsafe_allow_html=True,
    )

    rating_key = f"fb_rating_{idx}"
    comment_key = f"fb_comment_{idx}"
    if rating_key not in st.session_state:
        st.session_state[rating_key] = "Helpful"

    c1, c2 = st.columns([1, 2])
    with c1:
        rating_label = st.radio(
            "Rating",
            ["Helpful", "Not helpful"],
            key=rating_key,
            horizontal=True,
            label_visibility="collapsed",
        )
    with c2:
        comment = st.text_input(
            "Optional comment",
            key=comment_key,
            placeholder="What worked or what was missing?",
            label_visibility="collapsed",
        )

    if st.button("Submit feedback", key=f"fb_submit_{idx}"):
        rating = "helpful" if rating_label == "Helpful" else "not_helpful"
        # Use a fresh AnswerHistory handle so Streamlit cache cannot keep a stale class
        history = AnswerHistory(path=bot.history.path)
        saved = history.set_feedback(
            history_id, rating=rating, comment=comment or ""
        )
        if saved:
            st.session_state.messages[idx]["feedback"] = saved.get("feedback") or {
                "rating": rating,
                "comment": comment or "",
            }
            st.rerun()
        else:
            st.error("Could not save feedback.")


def render_result(msg: dict, idx: int) -> None:
    labels = {
        "rag": "Vector DB",
        "llm": "Local LLM (Qwen)",
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

    # Satisfaction gate → internet only if user is not satisfied
    if msg.get("can_search_web") and not msg.get("satisfaction_done"):
        st.caption("Are you satisfied with this answer?")
        c_yes, c_no = st.columns(2)
        with c_yes:
            if st.button("Yes — satisfied", key=f"sat_yes_{idx}"):
                st.session_state.messages[idx]["satisfaction_done"] = True
                st.session_state.messages[idx]["satisfied"] = True
                st.session_state.messages[idx]["can_search_web"] = False
                st.rerun()
        with c_no:
            if st.button("No — search internet", key=f"sat_no_{idx}"):
                question = msg.get("question") or ""
                # Prefer the preceding user message
                if not question:
                    for j in range(idx - 1, -1, -1):
                        if st.session_state.messages[j].get("role") == "user":
                            question = st.session_state.messages[j].get("content", "")
                            break
                st.session_state.messages[idx]["satisfaction_done"] = True
                st.session_state.messages[idx]["satisfied"] = False
                st.session_state.messages[idx]["can_search_web"] = False
                st.session_state.pending_web = {
                    "question": question,
                    "prior_best": float(msg.get("best_score") or 0.0),
                }
                st.rerun()
    elif msg.get("satisfied") is True:
        st.success("Marked as satisfied")
    elif msg.get("satisfied") is False and mode != "internet":
        st.caption("Searching internet because you were not satisfied…")

    # Feedback on response (always available for persisted answers)
    if mode != "none" or msg.get("history_id"):
        render_feedback(msg, idx)

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
if "pending_web" not in st.session_state:
    st.session_state.pending_web = None

SUGGESTIONS = [
    "How do I use getByRole locators?",
    "Mock an API with page.route",
    "Reuse login with storageState",
    "Debug flaky tests with Trace Viewer",
]


def render_suggestions(*, waiting: bool = False) -> None:
    """Keep suggested questions visible, including while the next answer loads."""
    hold_note = (
        "Holding suggestions while the next result loads…"
        if waiting
        else "Pick a question or type your own below."
    )
    st.markdown(
        f'<div class="nv-suggestions">'
        f'<p class="nv-suggestions-title">Suggested questions</p>'
        f'<p class="nv-suggestions-hold">{hold_note}</p>'
        f"</div>",
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2)
    for i, s in enumerate(SUGGESTIONS):
        with (c1 if i % 2 == 0 else c2):
            if st.button(s, key=f"sug_{i}", disabled=waiting):
                st.session_state.pending_query = s
                st.rerun()


# Hold this section while the next result is coming (user msg with no assistant yet)
_msgs = st.session_state.messages
_waiting = bool(_msgs) and _msgs[-1].get("role") == "user"
_show_suggestions = (not _msgs) or _waiting or st.session_state.pending_query or st.session_state.pending_web
if _show_suggestions:
    render_suggestions(waiting=_waiting or bool(st.session_state.pending_query) or bool(st.session_state.pending_web))
    if not _msgs:
        st.markdown(
            '<p class="nv-footer">NEW VISION · A SoftServe Company · Playwright Testing Assistant</p>',
            unsafe_allow_html=True,
        )

for i, msg in enumerate(st.session_state.messages):
    if msg["role"] == "user":
        st.markdown(
            f'<p class="user-q">{msg["content"]}</p>',
            unsafe_allow_html=True,
        )
    else:
        with st.chat_message("assistant"):
            render_result(msg, i)

# Internet only after user clicks "Not satisfied"
pending_web = st.session_state.pending_web
if pending_web:
    # Keep suggestions held above while internet result streams in
    st.session_state.pending_web = None
    question = (pending_web.get("question") or "").strip()
    prior_best = float(pending_web.get("prior_best") or 0.0)
    if question:
        status = st.empty()
        stream_box = st.empty()
        try:
            result = None
            tokens: list[str] = []
            for event in bot.ask_internet_stream(question, prior_best=prior_best):
                etype = event.get("type")
                if etype == "status":
                    status.info(event.get("message") or "Searching internet…")
                elif etype == "token":
                    tokens.append(event.get("text") or "")
                    stream_box.markdown("".join(tokens))
                elif etype == "final":
                    result = event.get("result") or {}
            status.empty()
            stream_box.empty()
            if not result:
                result = {"answer": "".join(tokens) or "_No response._", "sources": []}
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": result.get("answer") or "_No response._",
                    "sources": result.get("sources") or [],
                    "mode": result.get("mode"),
                    "best_score": result.get("best_score"),
                    "history_id": result.get("history_id"),
                    "can_save_to_kb": bool(result.get("can_save_to_kb")),
                    "can_search_web": False,
                    "saved_to_kb": False,
                    "followups": result.get("followups") or [],
                    "framework": result.get("framework") or FRAMEWORK,
                    "question": question,
                    "satisfaction_done": True,
                }
            )
            st.rerun()
        except Exception as exc:  # noqa: BLE001
            status.empty()
            st.error(f"Error: {exc}")

prompt = st.chat_input("Ask about Playwright testing…")
typed_or_suggestion = prompt or st.session_state.pending_query

# Stage 1: capture question, keep Suggested questions held, then rerun
if typed_or_suggestion and not st.session_state.get("_pending_answer_for"):
    st.session_state.pending_query = ""
    st.session_state.messages.append(
        {"role": "user", "content": typed_or_suggestion}
    )
    st.session_state._pending_answer_for = typed_or_suggestion
    st.rerun()

# Stage 2: fetch answer while suggestions stay on screen
query = st.session_state.get("_pending_answer_for") or ""
if query:
    status = st.empty()
    stream_box = st.empty()
    try:
        result = None
        tokens: list[str] = []
        for event in bot.ask_stream(query):
            etype = event.get("type")
            if etype == "status":
                status.info(event.get("message") or "Working…")
            elif etype == "token":
                tokens.append(event.get("text") or "")
                stream_box.markdown("".join(tokens))
            elif etype == "final":
                result = event.get("result") or {}
        status.empty()
        stream_box.empty()
        if not result:
            result = {"answer": "".join(tokens) or "_No response._", "sources": []}
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": result.get("answer") or "_No response._",
                "sources": result.get("sources") or [],
                "mode": result.get("mode"),
                "best_score": result.get("best_score"),
                "history_id": result.get("history_id"),
                "can_save_to_kb": bool(result.get("can_save_to_kb")),
                "can_search_web": bool(result.get("can_search_web")),
                "saved_to_kb": False,
                "followups": result.get("followups") or [],
                "framework": result.get("framework") or FRAMEWORK,
                "question": result.get("question") or query,
                "satisfaction_done": False,
            }
        )
        st.session_state._pending_answer_for = ""
        st.rerun()
    except Exception as exc:  # noqa: BLE001
        status.empty()
        st.session_state._pending_answer_for = ""
        st.error(f"Error: {exc}")
        st.session_state.messages.append(
            {"role": "assistant", "content": f"Error: {exc}", "sources": []}
        )
