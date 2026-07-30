"""Multi-mode Testing Hub — Arena-inspired UI with specialist agents + AI Reconcile."""

from __future__ import annotations

import base64
import html
import sys
from pathlib import Path
from urllib.parse import urlparse

import streamlit as st
import streamlit.components.v1 as components

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rag.agents.hub import AgentHub, all_mode_cards
from rag.config import (
    CHAT_MODEL,
    EMBED_MODEL,
    FRAMEWORK,
    PROVIDER_IDS,
    PROVIDER_LABELS,
)
from rag.history import AnswerHistory
from rag.modes import get_mode
from rag.providers import list_models, provider_ready, set_provider_model
from rag.security import escape_html

LOGO_PATH = ROOT / "assets" / "new-vision-logo.png"

STRATEGY_OPTIONS = {
    "Off (single answer)": "off",
    "Two providers": "two_providers",
    "RAG + LLM": "rag_llm",
    "Multi-mode": "multi_mode",
}


def _logo_data_uri() -> str:
    if not LOGO_PATH.exists():
        return ""
    data = base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{data}"


st.set_page_config(
    page_title="NEW VISION · Testing Hub",
    page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else "▶",
    layout="wide",
    initial_sidebar_state="expanded",
)

NV_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600;700&family=Outfit:wght@500;600;700&display=swap');

:root {
  --nv-ink: #2f3438;
  --nv-ink-soft: #5c5f63;
  --nv-muted: #8a8f94;
  --nv-orange: #f8971d;
  --nv-yellow: #ffd200;
  --nv-gold: #c69214;
  --nv-navy: #005587;
  --nv-cyan: #00a3e0;
  --nv-bg: #f7f9fb;
  --nv-sidebar: #f0f4f8;
  --nv-card: #ffffff;
  --nv-line: #e3ebf2;
  --nv-header-h: 56px;
}

html, body, [class*="css"], .stMarkdown, .stText, .stCaption {
  font-family: "Barlow", sans-serif !important;
  color: var(--nv-ink);
}

.stApp { background: var(--nv-bg) !important; }
[data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > .main,
section.main { background: var(--nv-bg) !important; }

.block-container {
  max-width: 820px;
  padding-top: 0.75rem !important;
  padding-bottom: 8.5rem !important;
}

/* Frozen single-row top menu */
.fixed-heading-menu {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  width: 100vw !important;
  height: var(--nv-header-h) !important;
  z-index: 999 !important;
  display: flex !important;
  align-items: center !important;
  gap: 0.85rem;
  padding: 0 1.1rem !important;
  margin: 0 !important;
  box-sizing: border-box !important;
  overflow: hidden !important;
  background: #ffffff !important;
  border-bottom: 1px solid var(--nv-line);
  box-shadow: 0 1px 0 rgba(0, 85, 135, 0.04);
}
.fixed-heading-menu::after {
  content: "";
  position: absolute;
  left: 0; right: 0; bottom: 0;
  height: 2px;
  background: linear-gradient(90deg, var(--nv-orange), var(--nv-yellow), var(--nv-navy), var(--nv-cyan));
}
.app-header {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  min-width: 0;
  flex: 1 1 auto;
  background: transparent !important;
  border: none !important;
  margin: 0;
  padding: 0;
  box-shadow: none !important;
}
.app-header img.nv-logo {
  height: 32px;
  width: auto;
  display: block;
  flex-shrink: 0;
}
.app-title {
  font-family: "Outfit", sans-serif;
  font-size: 0.98rem;
  font-weight: 700;
  color: var(--nv-ink);
  margin: 0;
  line-height: 1.2;
  white-space: nowrap;
}
.app-kicker, .app-sub, .agent-header-desc { display: none !important; }
.menu-agent { margin-left: auto; flex-shrink: 0; max-width: 42%; }
.agent-pill {
  display: inline-flex;
  align-items: center;
  font-family: "Outfit", sans-serif;
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--nv-navy);
  background: rgba(0, 163, 224, 0.10);
  border: 1px solid rgba(0, 133, 182, 0.22);
  border-radius: 999px;
  padding: 0.28rem 0.75rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}
.fixed-heading-spacer {
  display: block !important;
  height: var(--nv-header-h) !important;
  min-height: var(--nv-header-h) !important;
  width: 100%;
  visibility: hidden;
  pointer-events: none;
  margin: 0 !important;
  padding: 0 !important;
}

header[data-testid="stHeader"] { display: none !important; }
div[data-testid="stDecoration"] { display: none !important; }

/* Sidebar under header */
section[data-testid="stSidebar"] {
  background: var(--nv-sidebar) !important;
  border-right: 1px solid var(--nv-line) !important;
  top: var(--nv-header-h) !important;
  height: calc(100vh - var(--nv-header-h)) !important;
  max-height: calc(100vh - var(--nv-header-h)) !important;
  margin-top: 0 !important;
  padding-top: 0 !important;
  z-index: 100 !important;
  overflow-x: hidden !important;
  transform: none !important;
}
section[data-testid="stSidebar"] > div:first-child {
  padding-top: 0 !important;
  margin-top: 0 !important;
  height: 100% !important;
  overflow-x: hidden !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarHeader"],
section[data-testid="stSidebar"] [data-testid="stLogoSpacer"],
section[data-testid="stSidebar"] [data-testid="stLogo"] {
  display: none !important;
  height: 0 !important;
  min-height: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
  padding: 0.45rem 0.6rem 1rem 0.6rem !important;
  overflow-x: hidden !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
  padding-top: 0 !important;
  margin-top: 0 !important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarContent"] > div:first-child {
  padding-top: 0 !important;
}

.agent-nav-title {
  font-family: "Outfit", sans-serif;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--nv-muted);
  margin: 0.55rem 0 0.25rem 0.15rem;
}
.agent-active-hint { display: none !important; }
.settings-status {
  display: inline-block;
  font-size: 0.72rem;
  font-weight: 600;
  color: #0b6e4f;
  background: rgba(16, 185, 129, 0.12);
  border: 1px solid rgba(16, 185, 129, 0.25);
  border-radius: 999px;
  padding: 0.12rem 0.5rem;
  margin: 0.25rem 0 0.45rem 0;
}
.settings-status.warn {
  color: #9a3412;
  background: rgba(248, 151, 29, 0.14);
  border-color: rgba(248, 151, 29, 0.35);
}

section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
  border-radius: 10px !important;
  border-color: var(--nv-line) !important;
  background: #fff !important;
}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stMultiSelect label {
  font-weight: 600 !important;
  color: var(--nv-ink-soft) !important;
  font-size: 0.78rem !important;
}
section[data-testid="stSidebar"] hr {
  margin: 0.55rem 0 !important;
  border-color: var(--nv-line) !important;
}
section[data-testid="stSidebar"] div.stButton > button {
  text-align: left !important;
  justify-content: flex-start !important;
  width: 100% !important;
  max-width: 100% !important;
  box-sizing: border-box !important;
  border-radius: 10px !important;
  border: 1px solid transparent !important;
  background: transparent !important;
  color: var(--nv-ink) !important;
  font-weight: 500 !important;
  font-size: 0.9rem !important;
  padding: 0.45rem 0.65rem !important;
  box-shadow: none !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}
section[data-testid="stSidebar"] div.stButton > button:hover {
  background: rgba(0, 163, 224, 0.10) !important;
  color: var(--nv-navy) !important;
  transform: none !important;
  border-color: transparent !important;
}
section[data-testid="stSidebar"] div.stButton > button[kind="primary"],
section[data-testid="stSidebar"] div.stButton > button[data-testid="baseButton-primary"],
section[data-testid="stSidebar"] button[kind="primary"] {
  background: linear-gradient(90deg, rgba(0, 163, 224, 0.18), rgba(0, 85, 135, 0.10)) !important;
  background-color: rgba(0, 163, 224, 0.14) !important;
  border: 1px solid rgba(0, 85, 135, 0.35) !important;
  border-left: 4px solid var(--nv-orange) !important;
  color: var(--nv-navy) !important;
  font-weight: 700 !important;
  box-shadow: 0 1px 4px rgba(0, 85, 135, 0.10) !important;
}
/* Keep New chat as a clear CTA, not the active-agent look */
section[data-testid="stSidebar"] div.stButton:has(button[kind="secondary"]) {
  margin-bottom: 0.05rem;
}

section[data-testid="stSidebar"] [data-testid="stExpander"] {
  background: #fff !important;
  border: 1px solid var(--nv-line) !important;
  border-radius: 12px !important;
}
section[data-testid="stSidebar"] .stButton,
section[data-testid="stSidebar"] div[data-testid="stSelectbox"],
section[data-testid="stSidebar"] div[data-testid="stMultiSelect"] {
  max-width: 100% !important;
}

div[data-baseweb="popover"],
div[data-baseweb="menu"],
ul[role="listbox"],
body > div[data-baseweb="popover"] {
  z-index: 100000 !important;
}

[data-testid="stBottom"],
[data-testid="stBottomBlockContainer"],
.stChatFloatingInputContainer,
div[data-testid="stChatInput"] { z-index: 200 !important; }
[data-testid="stBottom"] {
  background: linear-gradient(180deg, rgba(247,249,251,0) 0%, var(--nv-bg) 35%) !important;
  padding-bottom: 0.5rem !important;
  padding-top: 0.5rem !important;
}
[data-testid="stChatInput"] {
  background: #ffffff !important;
  border: 1px solid var(--nv-line) !important;
  border-radius: 18px !important;
  box-shadow: 0 2px 12px rgba(0, 85, 135, 0.08) !important;
}
[data-testid="stChatInput"] textarea {
  font-size: 0.95rem !important;
  line-height: 1.45 !important;
}
[data-testid="collapsedControl"],
[data-testid="stSidebarCollapsedControl"] {
  top: calc(var(--nv-header-h) + 0.35rem) !important;
  z-index: 1000 !important;
}

.nv-loading {
  display: flex; align-items: center; gap: 0.9rem;
  margin: 0.5rem 0 0.85rem 0; padding: 0.75rem 0.9rem;
  background: #fff; border: 1px solid var(--nv-line);
  border-left: 3px solid var(--nv-cyan); border-radius: 12px;
}
.nv-loading-msg {
  font-family: "Outfit", sans-serif; font-weight: 600;
  color: var(--nv-navy); font-size: 0.92rem;
}
.nv-loading-sub { color: var(--nv-muted); font-size: 0.78rem; margin-top: 0.1rem; }
.nv-scene { width: 64px; height: 56px; position: relative; flex-shrink: 0; }
.nv-scene-search .doc {
  position: absolute; left: 6px; top: 8px; width: 30px; height: 38px;
  background: #fff; border: 2px solid var(--nv-navy); border-radius: 4px; overflow: hidden;
}
.nv-scene-search .doc span {
  display: block; height: 3px; margin: 6px 5px 0; background: rgba(0,85,135,0.25);
  border-radius: 2px; animation: nv-lines 1.2s ease-in-out infinite;
}
.nv-scene-search .doc span:nth-child(2) { width: 70%; animation-delay: 0.1s; }
.nv-scene-search .doc span:nth-child(3) { width: 55%; animation-delay: 0.2s; }
.nv-scene-search .lens {
  position: absolute; right: 2px; bottom: 4px; width: 22px; height: 22px;
  border: 3px solid var(--nv-orange); border-radius: 50%;
  background: rgba(255,255,255,0.55); animation: nv-scan 1.4s ease-in-out infinite;
}
.nv-scene-search .lens::after {
  content: ""; position: absolute; right: -7px; bottom: -5px; width: 10px; height: 3px;
  background: var(--nv-gold); border-radius: 2px; transform: rotate(45deg);
}
.nv-scene-type .screen {
  position: absolute; inset: 6px 2px 8px 2px;
  background: linear-gradient(160deg, var(--nv-navy), #003d5c);
  border-radius: 6px; padding: 7px;
}
.nv-scene-type .cursor-line {
  height: 7px; width: 0; background: var(--nv-cyan); border-radius: 2px;
  animation: nv-type-grow 1.5s steps(12, end) infinite; margin-bottom: 5px;
}
.nv-scene-type .cursor-line:nth-child(2) { animation-delay: 0.15s; background: var(--nv-orange); }
.nv-scene-type .blink {
  display: inline-block; width: 2px; height: 9px; background: var(--nv-gold);
  animation: nv-blink 0.7s step-end infinite;
}
.nv-scene-merge .blob { position: absolute; width: 20px; height: 20px; border-radius: 50%; top: 16px; }
.nv-scene-merge .a { left: 4px; background: var(--nv-cyan); animation: nv-merge-a 1.3s ease-in-out infinite; }
.nv-scene-merge .b { right: 4px; background: var(--nv-orange); animation: nv-merge-b 1.3s ease-in-out infinite; }
.nv-scene-merge .c {
  left: 22px; top: 16px; width: 20px; height: 20px; border-radius: 50%;
  background: linear-gradient(135deg, var(--nv-cyan), var(--nv-orange));
  opacity: 0; animation: nv-merge-c 1.3s ease-in-out infinite;
}
.nv-scene-web .globe {
  position: absolute; left: 12px; top: 6px; width: 40px; height: 40px;
  border: 3px solid var(--nv-navy); border-radius: 50%;
  background: radial-gradient(circle at 35% 35%, rgba(0,163,224,0.35), transparent 50%);
  animation: nv-spin 2.4s linear infinite;
}
.nv-scene-web .orbit {
  position: absolute; left: 4px; top: 0; width: 54px; height: 54px;
  border: 1px dashed rgba(248,151,29,0.55); border-radius: 50%;
  animation: nv-spin 3.2s linear infinite reverse;
}
.nv-scene-web .sat {
  position: absolute; top: -3px; left: 23px; width: 7px; height: 7px;
  border-radius: 50%; background: var(--nv-orange);
}
.nv-scene-flow .n { position: absolute; width: 14px; height: 11px; border-radius: 3px; }
.nv-scene-flow .n1 { left: 6px; top: 8px; background: var(--nv-cyan); animation: nv-pulse 1.2s ease-in-out infinite; }
.nv-scene-flow .n2 { left: 24px; top: 22px; background: var(--nv-orange); animation: nv-pulse 1.2s ease-in-out 0.2s infinite; }
.nv-scene-flow .n3 { left: 42px; top: 8px; background: var(--nv-gold); animation: nv-pulse 1.2s ease-in-out 0.4s infinite; }
.nv-scene-flow .e { position: absolute; height: 2px; background: var(--nv-navy); opacity: 0.4; }
.nv-scene-flow .e1 { left: 18px; top: 12px; width: 16px; transform: rotate(40deg); animation: nv-draw 1.2s ease-in-out infinite; }
.nv-scene-flow .e2 { left: 36px; top: 12px; width: 16px; transform: rotate(-40deg); animation: nv-draw 1.2s ease-in-out 0.2s infinite; }
.nv-scene-work .mask {
  position: absolute; left: 8px; top: 6px; width: 26px; height: 32px;
  border: 3px solid var(--nv-navy); border-radius: 12px 12px 7px 7px;
  background: linear-gradient(180deg, rgba(0,163,224,0.2), rgba(248,151,29,0.15));
  animation: nv-nod 0.9s ease-in-out infinite alternate;
}
.nv-scene-work .eye { position: absolute; top: 10px; width: 4px; height: 4px; border-radius: 50%; background: var(--nv-navy); }
.nv-scene-work .eye.l { left: 5px; }
.nv-scene-work .eye.r { right: 5px; }
.nv-scene-work .ball {
  position: absolute; right: 6px; bottom: 10px; width: 14px; height: 14px; border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, #ff8a65, #e53935);
  animation: nv-bounce-ball 0.7s ease-in-out infinite alternate;
}
@keyframes nv-lines { 0%, 100% { opacity: 0.35; } 50% { opacity: 1; } }
@keyframes nv-scan { 0% { transform: translate(-4px, 4px); } 50% { transform: translate(-12px, -6px); } 100% { transform: translate(-4px, 4px); } }
@keyframes nv-type-grow { 0% { width: 0; } 60%, 100% { width: 85%; } }
@keyframes nv-blink { 50% { opacity: 0; } }
@keyframes nv-merge-a { 0%, 20% { transform: translateX(0); } 55%, 70% { transform: translateX(14px); } 100% { transform: translateX(0); } }
@keyframes nv-merge-b { 0%, 20% { transform: translateX(0); } 55%, 70% { transform: translateX(-14px); } 100% { transform: translateX(0); } }
@keyframes nv-merge-c { 0%, 45% { opacity: 0; transform: scale(0.4); } 60%, 75% { opacity: 1; transform: scale(1.05); } 100% { opacity: 0; transform: scale(0.6); } }
@keyframes nv-spin { to { transform: rotate(360deg); } }
@keyframes nv-pulse { 0%, 100% { transform: scale(1); opacity: 0.75; } 50% { transform: scale(1.12); opacity: 1; } }
@keyframes nv-draw { 0%, 100% { opacity: 0.15; } 50% { opacity: 0.7; } }
@keyframes nv-nod { from { transform: translateY(0) rotate(-3deg); } to { transform: translateY(3px) rotate(3deg); } }
@keyframes nv-bounce-ball { from { transform: translateY(0); } to { transform: translateY(-8px); } }

.mode-tag {
  display: inline-block;
  font-family: "Outfit", sans-serif;
  font-size: 0.68rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--nv-navy);
  background: rgba(0, 163, 224, 0.10);
  border: 1px solid rgba(0, 133, 182, 0.20);
  padding: 0.18rem 0.55rem;
  border-radius: 999px;
  margin: 0 0.3rem 0.5rem 0;
}
.source-row {
  background: var(--nv-card);
  border: 1px solid var(--nv-line);
  border-left: 3px solid var(--nv-cyan);
  border-radius: 10px;
  padding: 0.65rem 0.8rem;
  margin-bottom: 0.4rem;
}
.user-q {
  font-family: "Outfit", sans-serif;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--nv-ink);
  margin: 0.85rem 0 0.55rem 0;
  padding: 0;
  border: none;
}
.nv-feedback {
  margin-top: 0.75rem;
  margin-bottom: 1.25rem;
  padding: 0.75rem 0.9rem;
  background: #fff;
  border: 1px solid var(--nv-line);
  border-radius: 12px;
  border-left: 3px solid var(--nv-orange);
}
.nv-feedback-title {
  font-family: "Outfit", sans-serif;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--nv-navy);
  margin: 0 0 0.3rem 0;
}
.nv-feedback-hint { font-size: 0.85rem; color: var(--nv-muted); margin: 0 0 0.5rem 0; }
.nv-feedback-done { font-size: 0.9rem; color: var(--nv-navy); font-weight: 600; margin: 0; }

div.stButton > button {
  font-family: "Barlow", sans-serif !important;
  font-weight: 600 !important;
  border-radius: 10px !important;
}
[data-testid="stChatMessage"] {
  background: #ffffff !important;
  border: 1px solid var(--nv-line);
  border-radius: 14px;
  padding: 0.35rem 0.25rem;
}
</style>
"""



st.markdown(NV_CSS, unsafe_allow_html=True)


@st.cache_resource(show_spinner="Loading Testing Hub…")
def get_hub(_cache_version: str = "hub-v1") -> AgentHub:
    hub = AgentHub(rebuild_index=False)
    warm = getattr(hub.playwright.bot, "_warm_llm_quietly", None)
    if callable(warm):
        import threading

        threading.Thread(target=warm, daemon=True).start()
    return hub


hub = get_hub()
hub.history = AnswerHistory(path=hub.history.path)
hub.playwright.bot.history = hub.history
_logo_uri = _logo_data_uri()

# Session defaults — default into first specialist (ChatGPT-style, no landing cards)
_CARDS = all_mode_cards()
_DEFAULT_MODE = _CARDS[0]["id"] if _CARDS else "playwright_kb"
if "active_mode" not in st.session_state or not st.session_state.active_mode:
    st.session_state.active_mode = _DEFAULT_MODE
if "messages_by_mode" not in st.session_state:
    st.session_state.messages_by_mode = {}
if "messages" not in st.session_state:
    st.session_state.messages = st.session_state.messages_by_mode.get(
        st.session_state.active_mode, []
    )
if "pending_query" not in st.session_state:
    st.session_state.pending_query = ""
if "pending_web" not in st.session_state:
    st.session_state.pending_web = None
if "pending_reconcile" not in st.session_state:
    st.session_state.pending_reconcile = None
if "provider" not in st.session_state:
    st.session_state.provider = "ollama"
if "secondary_provider" not in st.session_state:
    st.session_state.secondary_provider = "gemini"
if "chat_model" not in st.session_state:
    st.session_state.chat_model = ""
if "secondary_model" not in st.session_state:
    st.session_state.secondary_model = ""
if "reconcile_strategy" not in st.session_state:
    st.session_state.reconcile_strategy = "off"
if "multi_modes" not in st.session_state:
    spec0 = get_mode(st.session_state.active_mode)
    st.session_state.multi_modes = [
        st.session_state.active_mode,
        *list(spec0.related_modes),
    ][:3]


def _switch_mode(new_mode: str) -> None:
    """Persist current chat and open another agent (sidebar nav)."""
    cur = st.session_state.active_mode
    if cur:
        st.session_state.messages_by_mode[cur] = list(st.session_state.messages)
    st.session_state.active_mode = new_mode
    st.session_state.messages = list(
        st.session_state.messages_by_mode.get(new_mode, [])
    )
    st.session_state.pending_query = ""
    st.session_state.pending_web = None
    st.session_state.pending_reconcile = None
    st.session_state._pending_answer_for = ""
    spec = get_mode(new_mode)
    st.session_state.multi_modes = [new_mode, *list(spec.related_modes)][:3]


# —— Left sidebar: agents + settings ——
mode_id = st.session_state.active_mode
spec = get_mode(mode_id)

_NAV_SHORT = {
    "playwright_kb": "Playwright KB",
    "synthetic_data": "Synthetic data",
    "manual_cases": "Manual cases",
    "test_strategy": "Test strategy",
    "estimation": "Estimation",
    "agile": "Agile",
    "defect_lifecycle": "Defect lifecycle",
    "workflow_diagram": "Workflow diagram",
}

with st.sidebar:
    if st.button("＋ New chat", use_container_width=True, key="nav_new_chat"):
        st.session_state.messages = []
        st.session_state.messages_by_mode[st.session_state.active_mode] = []
        st.session_state.pending_query = ""
        st.session_state._pending_answer_for = ""
        st.rerun()

    st.markdown(
        '<p class="agent-nav-title">Agents</p>',
        unsafe_allow_html=True,
    )
    for card in _CARDS:
        is_active = card["id"] == st.session_state.active_mode
        short = _NAV_SHORT.get(card["id"], card["label"])
        label = f"●  {short}" if is_active else short
        if st.button(
            label,
            key=f"nav_{card['id']}",
            use_container_width=True,
            type="primary" if is_active else "secondary",
            help=card["description"],
        ):
            if not is_active:
                _switch_mode(card["id"])
                st.rerun()

    st.divider()
    with st.expander("Settings", expanded=False):
        provider_labels = [PROVIDER_LABELS[p] for p in PROVIDER_IDS]
        provider_idx = (
            PROVIDER_IDS.index(st.session_state.provider)
            if st.session_state.provider in PROVIDER_IDS
            else 0
        )
        picked = st.selectbox(
            "Provider",
            provider_labels,
            index=provider_idx,
            key="ui_provider",
            help="Where to run the primary answer",
        )
        new_provider = PROVIDER_IDS[provider_labels.index(picked)]
        if new_provider != st.session_state.provider:
            st.session_state.provider = new_provider
            st.session_state.chat_model = ""

        primary_models = list_models(st.session_state.provider)
        if st.session_state.chat_model not in primary_models:
            st.session_state.chat_model = primary_models[0]
        st.selectbox(
            "Model",
            primary_models,
            key="chat_model",
            help="Chat model for the selected provider",
        )
        set_provider_model(st.session_state.provider, st.session_state.chat_model)

        ok, hint = provider_ready(st.session_state.provider)
        st.markdown(
            f'<span class="settings-status{"" if ok else " warn"}">'
            f'{"Ready" if ok else "Setup needed"} · {escape_html(hint)}</span>',
            unsafe_allow_html=True,
        )

        strat_labels = list(STRATEGY_OPTIONS.keys())
        current_strat = st.session_state.reconcile_strategy
        inv = {v: k for k, v in STRATEGY_OPTIONS.items()}
        strat_label = st.selectbox(
            "AI Reconcile",
            strat_labels,
            index=strat_labels.index(inv.get(current_strat, strat_labels[0])),
            key="ui_reconcile",
        )
        st.session_state.reconcile_strategy = STRATEGY_OPTIONS[strat_label]

        sec_labels = [PROVIDER_LABELS[p] for p in PROVIDER_IDS]
        sec_idx = (
            PROVIDER_IDS.index(st.session_state.secondary_provider)
            if st.session_state.secondary_provider in PROVIDER_IDS
            else 1
        )
        sec_picked = st.selectbox(
            "Secondary provider",
            sec_labels,
            index=sec_idx,
            key="ui_secondary_provider",
            help="Used for Two providers / on-demand Reconcile",
        )
        new_sec = PROVIDER_IDS[sec_labels.index(sec_picked)]
        if new_sec != st.session_state.secondary_provider:
            st.session_state.secondary_provider = new_sec
            st.session_state.secondary_model = ""

        secondary_models = list_models(st.session_state.secondary_provider)
        if st.session_state.secondary_model not in secondary_models:
            st.session_state.secondary_model = secondary_models[0]
        st.selectbox(
            "Secondary model",
            secondary_models,
            key="secondary_model",
        )
        set_provider_model(
            st.session_state.secondary_provider, st.session_state.secondary_model
        )

        if st.session_state.reconcile_strategy == "multi_mode":
            all_ids = [m["id"] for m in all_mode_cards()]
            selected = st.multiselect(
                "Modes to reconcile (max 3)",
                options=all_ids,
                default=[m for m in st.session_state.multi_modes if m in all_ids][:3]
                or [mode_id],
                format_func=lambda mid: get_mode(mid).label,
                key="ui_multi_modes",
            )
            st.session_state.multi_modes = selected[:3]

    with st.expander("Tech Data", expanded=False):
        st.write("Framework:", FRAMEWORK)
        st.write("Active mode:", mode_id)
        st.write("Chat model:", CHAT_MODEL)
        st.write("Embed model:", EMBED_MODEL)
        for p in PROVIDER_IDS:
            ready, detail = provider_ready(p)
            st.write(f"{PROVIDER_LABELS[p]}:", "✅" if ready else "❌", detail)
        st.write("Playwright indexed chunks:", hub.retriever.count)
        st.write("History:", AnswerHistory(path=hub.history.path).count())
        if st.button("Rebuild indexes"):
            with st.spinner("Re-embedding…"):
                counts = hub.rebuild_all()
            st.success(str(counts))
            st.cache_resource.clear()
            st.rerun()
        if st.button("Clear chat", key="tech_clear_chat"):
            st.session_state.messages = []
            st.session_state.messages_by_mode[mode_id] = []
            st.rerun()
        pending = hub.history.pending_correctable(limit=6)
        if pending:
            st.caption("Save if correct")
            for entry in pending:
                st.caption(
                    f"`{entry.get('mode')}` {(entry.get('question') or '')[:40]}"
                )
                if st.button("Save to KB", key=f"side_{entry['id']}"):
                    out = hub.mark_correct_and_train(entry["id"], mode_id=mode_id)
                    if out.get("ok"):
                        st.success(f"+{out.get('trained_chunks', 0)} chunks")
                        st.rerun()
                    else:
                        st.error(out.get("error"))


# Frozen top menu bar
_nav_short = _NAV_SHORT.get(mode_id, spec.label)
if _logo_uri:
    st.markdown(
        f"""
<div class="fixed-heading-menu">
  <div class="app-header">
    <img class="nv-logo" src="{_logo_uri}" alt="NEW VISION" />
    <h1 class="app-title">Multi-mode Testing Hub</h1>
  </div>
  <div class="menu-agent">
    <span class="agent-pill">{escape_html(_nav_short)}</span>
  </div>
</div>
<div class="fixed-heading-spacer"></div>
""",
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f"""
<div class="fixed-heading-menu">
  <div class="app-header">
    <h1 class="app-title">NEW VISION · Testing Hub</h1>
  </div>
  <div class="menu-agent">
    <span class="agent-pill">{escape_html(_nav_short)}</span>
  </div>
</div>
<div class="fixed-heading-spacer"></div>
""",
        unsafe_allow_html=True,
    )


def _host(url: str) -> str:
    if not url:
        return ""
    try:
        return urlparse(url).netloc or url
    except Exception:  # noqa: BLE001
        return url


def _loading_scene(message: str) -> tuple[str, str]:
    """Pick animation HTML + subtitle from the status message text."""
    m = (message or "").lower()
    if any(k in m for k in ("reconcil", "draft a", "draft b", "merge", "on-demand")):
        html_scene = """
  <div class="nv-scene nv-scene-merge" aria-hidden="true">
    <div class="blob a"></div>
    <div class="blob b"></div>
    <div class="c"></div>
  </div>"""
        return html_scene, "Merging perspectives · NEW VISION"
    if any(k in m for k in ("internet", "web", "grounding")):
        html_scene = """
  <div class="nv-scene nv-scene-web" aria-hidden="true">
    <div class="orbit"><div class="sat"></div></div>
    <div class="globe"></div>
  </div>"""
        return html_scene, "Live web lookup · NEW VISION"
    if any(k in m for k in ("diagram", "workflow", "mermaid")):
        html_scene = """
  <div class="nv-scene nv-scene-flow" aria-hidden="true">
    <div class="n n1"></div>
    <div class="n n2"></div>
    <div class="n n3"></div>
    <div class="e e1"></div>
    <div class="e e2"></div>
  </div>"""
        return html_scene, "Drawing the flow · NEW VISION"
    if any(
        k in m
        for k in (
            "search",
            "vector",
            "knowledge",
            "sources",
            "rag",
            "mode knowledge",
        )
    ):
        html_scene = """
  <div class="nv-scene nv-scene-search" aria-hidden="true">
    <div class="doc"><span></span><span></span><span></span></div>
    <div class="lens"></div>
  </div>"""
        return html_scene, "Scanning knowledge · NEW VISION"
    if any(
        k in m
        for k in (
            "synthesiz",
            "asking",
            "llm",
            "qwen",
            "running",
            "working",
            "building",
        )
    ):
        html_scene = """
  <div class="nv-scene nv-scene-type" aria-hidden="true">
    <div class="screen">
      <div class="cursor-line"></div>
      <div class="cursor-line"></div>
      <span class="blink"></span>
    </div>
  </div>"""
        return html_scene, "Composing answer · NEW VISION"
    html_scene = """
  <div class="nv-scene nv-scene-work" aria-hidden="true">
    <div class="mask">
      <div class="eye l"></div>
      <div class="eye r"></div>
    </div>
    <div class="ball"></div>
  </div>"""
    return html_scene, "Agent at work · NEW VISION"


def show_loading(placeholder, message: str = "Working…") -> None:
    """SoftServe loader whose animation matches the status text."""
    scene_html, subtitle = _loading_scene(message)
    placeholder.markdown(
        f"""
<div class="nv-loading">
{scene_html}
  <div>
    <div class="nv-loading-msg">{escape_html(message)}</div>
    <div class="nv-loading-sub">{escape_html(subtitle)}</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_mermaid(source: str) -> None:
    if not source:
        return
    escaped = html.escape(source)
    components.html(
        f"""
<div class="mermaid">
{escaped}
</div>
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
  mermaid.initialize({{ startOnLoad: true, theme: 'neutral' }});
</script>
""",
        height=420,
        scrolling=True,
    )


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
                f'<div class="source-row"><strong>[{escape_html(n)}] '
                f"{escape_html(title)}</strong>"
                f'<div class="source-meta">{escape_html(meta)}</div>'
                f"<div>{escape_html(preview)}</div></div>",
                unsafe_allow_html=True,
            )
            if link:
                st.markdown(f"[Open source]({link})")


def render_feedback(msg: dict, idx: int) -> None:
    history_id = msg.get("history_id")
    if not history_id:
        return
    fb = msg.get("feedback") or {}
    if fb.get("rating"):
        label = "Helpful" if fb.get("rating") == "helpful" else "Not helpful"
        comment = (fb.get("comment") or "").strip()
        extra = f" — {escape_html(comment)}" if comment else ""
        st.markdown(
            f'<div class="nv-feedback"><p class="nv-feedback-done">'
            f"Thanks for your feedback: <strong>{escape_html(label)}</strong>{extra}"
            f"</p></div>",
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        '<div class="nv-feedback">'
        '<p class="nv-feedback-title">Feedback on this response</p>'
        '<p class="nv-feedback-hint">Was this answer useful?</p>'
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
        history = AnswerHistory(path=hub.history.path)
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
        "llm": "LLM",
        "llm_grounded": "LLM + RAG",
        "internet": "Internet",
        "agent": "Specialist agent",
        "reconciled": "AI Reconciled",
        "none": "No answer",
    }
    mode = msg.get("mode", "")
    st.markdown(
        f'<span class="mode-tag">{labels.get(mode, mode)}</span>'
        f'<span class="mode-tag">{escape_html(msg.get("mode_label") or "")}</span>'
        f'<span class="mode-tag">{escape_html(PROVIDER_LABELS.get(msg.get("provider") or "", msg.get("provider") or ""))}</span>',
        unsafe_allow_html=True,
    )

    mermaid_source = msg.get("mermaid_source") or ""
    if mermaid_source and msg.get("mermaid_valid"):
        render_mermaid(mermaid_source)
        st.code(mermaid_source, language="mermaid")
        st.download_button(
            "Download Mermaid (.md)",
            data=f"```mermaid\n{mermaid_source}\n```\n",
            file_name="workflow.md",
            mime="text/markdown",
            key=f"dl_mmd_{idx}",
        )
    elif msg.get("mermaid_error"):
        st.warning(msg.get("mermaid_error"))
        st.markdown(msg.get("content", ""))
    else:
        st.markdown(msg.get("content", ""))

    drafts = msg.get("drafts") or []
    if len(drafts) > 1 or msg.get("reconciled"):
        with st.expander("Show drafts", expanded=False):
            for d in drafts:
                st.markdown(f"**{d.get('label', 'Draft')}**")
                st.markdown(d.get("content") or "_empty_")
                st.divider()

    render_sources(msg.get("sources") or [])

    # On-demand reconcile (strategy 4)
    if (
        not msg.get("reconciled")
        and msg.get("role") != "user"
        and mode not in ("none",)
        and msg.get("content")
    ):
        if st.button("Reconcile with secondary provider", key=f"ondemand_{idx}"):
            st.session_state.pending_reconcile = {
                "question": msg.get("question") or "",
                "existing_answer": msg.get("content") or "",
                "mode_id": msg.get("mode_id") or st.session_state.active_mode,
                "primary_provider": msg.get("provider")
                or st.session_state.provider,
                "drafts": msg.get("drafts") or [],
            }
            st.rerun()

    # Satisfaction gate (Playwright only)
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
                if not question:
                    for j in range(idx - 1, -1, -1):
                        if st.session_state.messages[j].get("role") == "user":
                            question = st.session_state.messages[j].get(
                                "content", ""
                            )
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

    if mode != "none" or msg.get("history_id"):
        render_feedback(msg, idx)

    if msg.get("can_save_to_kb") and msg.get("history_id") and not msg.get("saved_to_kb"):
        st.caption(
            "Correct — save to KB only if accurate. Do not save secrets."
        )
        if st.button(
            "Correct — save to knowledge base",
            key=f"save_{msg['history_id']}_{idx}",
        ):
            with st.spinner("Saving to vector DB…"):
                out = hub.mark_correct_and_train(
                    msg["history_id"],
                    mode_id=msg.get("mode_id") or st.session_state.active_mode,
                )
            if out.get("ok"):
                st.session_state.messages[idx]["saved_to_kb"] = True
                st.success(f"Added {out.get('trained_chunks', 0)} chunks")
                st.rerun()
            else:
                st.error(out.get("error", "Save failed"))
    elif msg.get("saved_to_kb"):
        st.success("Saved to knowledge base")


# —— Chat body (scrolls under fixed heading menu) ——
suggestions = list(spec.suggestions)
_msgs = st.session_state.messages
_waiting = bool(_msgs) and _msgs[-1].get("role") == "user"
if not _msgs or _waiting or st.session_state.pending_query:
    st.caption("Suggested prompts")
    sc1, sc2 = st.columns(2)
    for i, s in enumerate(suggestions):
        with sc1 if i % 2 == 0 else sc2:
            if st.button(s, key=f"sug_{i}", disabled=_waiting):
                st.session_state.pending_query = s
                st.rerun()

for i, msg in enumerate(st.session_state.messages):
    if msg["role"] == "user":
        st.markdown(
            f'<p class="user-q">{escape_html(msg.get("content", ""))}</p>',
            unsafe_allow_html=True,
        )
    else:
        with st.chat_message("assistant"):
            render_result(msg, i)


def _append_assistant(result: dict, *, question: str) -> None:
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": result.get("answer") or "_No response._",
            "sources": result.get("sources") or [],
            "mode": result.get("mode"),
            "mode_id": result.get("mode_id") or mode_id,
            "mode_label": result.get("mode_label") or spec.label,
            "provider": result.get("provider") or st.session_state.provider,
            "best_score": result.get("best_score"),
            "history_id": result.get("history_id"),
            "can_save_to_kb": bool(result.get("can_save_to_kb")),
            "can_search_web": bool(result.get("can_search_web")),
            "saved_to_kb": False,
            "followups": result.get("followups") or [],
            "framework": result.get("framework") or FRAMEWORK,
            "question": result.get("question") or question,
            "satisfaction_done": False,
            "drafts": result.get("drafts") or [],
            "reconciled": bool(result.get("reconciled")),
            "reconcile_strategy": result.get("reconcile_strategy") or "off",
            "mermaid_source": result.get("mermaid_source") or "",
            "mermaid_valid": result.get("mermaid_valid"),
            "mermaid_error": result.get("mermaid_error") or "",
        }
    )
    st.session_state.messages_by_mode[mode_id] = list(st.session_state.messages)


# On-demand reconcile
pending_reconcile = st.session_state.pending_reconcile
if pending_reconcile:
    st.session_state.pending_reconcile = None
    q = (pending_reconcile.get("question") or "").strip()
    if q:
        status = st.empty()
        stream_box = st.empty()
        try:
            result = None
            tokens: list[str] = []
            for event in hub.reconcile_on_demand(
                q,
                pending_reconcile.get("existing_answer") or "",
                mode_id=pending_reconcile.get("mode_id") or mode_id,
                primary_provider=pending_reconcile.get("primary_provider")
                or st.session_state.provider,
                secondary_provider=st.session_state.secondary_provider,
                existing_drafts=pending_reconcile.get("drafts"),
            ):
                etype = event.get("type")
                if etype == "status":
                    show_loading(status, event.get("message") or "Reconciling…")
                elif etype == "token":
                    tokens.append(event.get("text") or "")
                    stream_box.markdown("".join(tokens))
                elif etype == "final":
                    result = event.get("result") or {}
            status.empty()
            stream_box.empty()
            if not result:
                result = {"answer": "".join(tokens) or "_No response._"}
            _append_assistant(result, question=q)
            st.rerun()
        except Exception as exc:  # noqa: BLE001
            status.empty()
            st.error(f"Error: {exc}")

# Internet after not satisfied
pending_web = st.session_state.pending_web
if pending_web:
    st.session_state.pending_web = None
    question = (pending_web.get("question") or "").strip()
    prior_best = float(pending_web.get("prior_best") or 0.0)
    if question:
        status = st.empty()
        stream_box = st.empty()
        try:
            result = None
            tokens: list[str] = []
            for event in hub.ask_internet_stream(question, prior_best=prior_best):
                etype = event.get("type")
                if etype == "status":
                    show_loading(status, event.get("message") or "Searching internet…")
                elif etype == "token":
                    tokens.append(event.get("text") or "")
                    stream_box.markdown("".join(tokens))
                elif etype == "final":
                    result = event.get("result") or {}
            status.empty()
            stream_box.empty()
            if not result:
                result = {"answer": "".join(tokens) or "_No response._", "sources": []}
            _append_assistant(result, question=question)
            st.session_state.messages[-1]["satisfaction_done"] = True
            st.session_state.messages[-1]["can_search_web"] = False
            st.rerun()
        except Exception as exc:  # noqa: BLE001
            status.empty()
            st.error(f"Error: {exc}")

placeholder = (
    "Paste requirement details for a workflow diagram…"
    if mode_id == "workflow_diagram"
    else f"Ask the {spec.label}…"
)
prompt = st.chat_input(placeholder)
typed_or_suggestion = prompt or st.session_state.pending_query

if typed_or_suggestion and not st.session_state.get("_pending_answer_for"):
    st.session_state.pending_query = ""
    st.session_state.messages.append(
        {"role": "user", "content": typed_or_suggestion}
    )
    st.session_state.messages_by_mode[mode_id] = list(st.session_state.messages)
    st.session_state._pending_answer_for = typed_or_suggestion
    st.rerun()

query = st.session_state.get("_pending_answer_for") or ""
if query:
    status = st.empty()
    stream_box = st.empty()
    try:
        result = None
        tokens: list[str] = []
        for event in hub.ask_stream(
            query,
            mode_id=mode_id,
            provider=st.session_state.provider,
            reconcile_strategy=st.session_state.reconcile_strategy,
            secondary_provider=st.session_state.secondary_provider,
            multi_modes=st.session_state.multi_modes or None,
        ):
            etype = event.get("type")
            if etype == "status":
                show_loading(status, event.get("message") or "Working…")
            elif etype == "token":
                tokens.append(event.get("text") or "")
                stream_box.markdown("".join(tokens))
            elif etype == "final":
                result = event.get("result") or {}
        status.empty()
        stream_box.empty()
        if not result:
            result = {"answer": "".join(tokens) or "_No response._", "sources": []}
        _append_assistant(result, question=query)
        st.session_state._pending_answer_for = ""
        st.rerun()
    except Exception as exc:  # noqa: BLE001
        status.empty()
        st.session_state._pending_answer_for = ""
        st.error(f"Error: {exc}")
        st.session_state.messages.append(
            {"role": "assistant", "content": f"Error: {exc}", "sources": []}
        )
