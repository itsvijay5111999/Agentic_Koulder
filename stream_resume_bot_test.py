"""
Responsive Streamlit frontend for the agentic chatbot.

Run with:
    streamlit run stream_resume_bot_test.py
"""

import base64
import html
import json
import os
import time
import traceback
import uuid
from io import BytesIO

import streamlit as st
from langchain_core.messages import HumanMessage, ToolMessage
from PIL import Image


APP_DEBUG = os.getenv("STREAMLIT_APP_DEBUG", "").lower() in {"1", "true", "yes", "on"}


def debug_log(message: str) -> None:
    """Log only when explicitly enabled; avoids leaking prompts, paths, and env info."""
    if APP_DEBUG:
        print(f"[streamlit-ui] {message}")


st.set_page_config(
    page_title="Agentic AI",
    page_icon="A",
    layout="wide",
    initial_sidebar_state="expanded",
)


try:
    from backend import chatbot, requires_deep_research, test_deep_agent_connection
except Exception as exc:
    debug_log(traceback.format_exc())
    st.error("Backend is unavailable. Check backend.py, dependencies, required environment variables, and deployment logs.")
    if APP_DEBUG:
        st.caption(f"Backend startup error: {type(exc).__name__}: {exc}")
    st.stop()


st.markdown(
    """
<style>
:root {
    color-scheme: dark;
    --app-bg: #05060a;
    --panel: #11131a;
    --panel-soft: #181b24;
    --ink: #f8fafc;
    --muted: #cbd5e1;
    --muted-soft: #94a3b8;
    --line: #2d3340;
    --line-strong: #465162;
    --sidebar: #07080d;
    --sidebar-panel: #12151d;
    --sidebar-line: #303746;
    --green: #4ade80;
    --teal: #2dd4bf;
    --indigo: #a78bfa;
    --amber: #fbbf24;
    --coral: #fb7185;
    --danger-bg: #3b1118;
    --warning-bg: #35260a;
    --success-bg: #0f2f1b;
    --text-on-light: #0f172a;
    --shadow: 0 20px 56px rgba(0, 0, 0, 0.45);
    --radius: 8px;
}

.stApp {
    background:
        radial-gradient(circle at 18% 0%, rgba(255, 255, 255, 0.11), transparent 28%),
        radial-gradient(circle at 86% 12%, rgba(255, 255, 255, 0.07), transparent 30%),
        linear-gradient(145deg, #05060a 0%, #0d1018 48%, #171b24 100%),
        var(--app-bg);
    color: var(--ink);
    font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

#MainMenu, footer, header { visibility: hidden; }

.stApp,
.stApp p,
.stApp label {
    color: var(--ink);
}

.stApp a {
    color: var(--teal) !important;
}

.stApp a:hover {
    color: #67e8f9 !important;
}

.block-container {
    max-width: 1180px;
    padding: 1.25rem 1.6rem 6rem !important;
}

section[data-testid="stSidebar"] {
    background: var(--sidebar) !important;
    border-right: 1px solid var(--sidebar-line);
}

section[data-testid="stSidebar"] * {
    color: #f2f2f2;
}

section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
    color: var(--ink) !important;
}

section[data-testid="stSidebar"] [data-testid="stMetric"] {
    background: var(--sidebar-panel);
    border: 1px solid var(--sidebar-line);
    border-radius: var(--radius);
    padding: 0.8rem;
}

section[data-testid="stSidebar"] [data-testid="stMetricLabel"] p,
section[data-testid="stSidebar"] [data-testid="stMetricValue"] {
    color: #f2f2f2 !important;
}

.app-shell {
    display: grid;
    gap: 1rem;
}

.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 1rem;
    background: rgba(13, 13, 15, 0.78);
    border: 1px solid var(--line);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    padding: 0.85rem 1rem;
    backdrop-filter: blur(18px);
}

.brand-lockup {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    min-width: 0;
}

.brand-mark {
    width: 2.25rem;
    height: 2.25rem;
    border-radius: var(--radius);
    display: grid;
    place-items: center;
    background: #ffffff;
    color: var(--text-on-light) !important;
    font-weight: 800;
    letter-spacing: 0;
}

.brand-title {
    font-size: clamp(1rem, 2vw, 1.25rem);
    line-height: 1.2;
    font-weight: 760;
    letter-spacing: 0;
    color: var(--ink);
}

.brand-subtitle {
    margin-top: 0.14rem;
    color: var(--muted);
    font-size: 0.78rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.status-row {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 0.5rem;
    flex-wrap: wrap;
}

.status-pill,
.thread-pill {
    border: 1px solid var(--line);
    border-radius: 999px;
    background: var(--panel);
    color: var(--muted);
    font-size: 0.76rem;
    line-height: 1;
    padding: 0.45rem 0.65rem;
    white-space: nowrap;
}

.status-pill strong {
    color: var(--green);
}

.deep-agent-pill {
    position: relative;
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    border: 1px solid transparent;
    border-radius: 999px;
    background:
        linear-gradient(var(--panel), var(--panel)) padding-box,
        linear-gradient(120deg, #4285f4, #a142f4, #ea4335, #fbbc04, #34a853, #00acc1, #4285f4) border-box;
    background-size: 100% 100%, 300% 300%;
    color: var(--ink) !important;
    font-size: 0.76rem;
    font-weight: 720;
    line-height: 1;
    padding: 0.45rem 0.72rem;
    white-space: nowrap;
    box-shadow: 0 8px 24px rgba(66, 133, 244, 0.14);
    animation: deepAgentBorderFlow 4.8s linear infinite;
}

.deep-agent-pill span {
    color: inherit !important;
}

.deep-agent-spark {
    width: 0.5rem;
    height: 0.5rem;
    border-radius: 999px;
    background: linear-gradient(135deg, #4285f4, #a142f4, #ea4335, #fbbc04, #34a853, #00acc1);
    background-size: 260% 260%;
    box-shadow: 0 0 14px rgba(45, 212, 191, 0.72);
    flex: 0 0 auto;
    animation:
        deepAgentGlow 1.8s ease-in-out infinite,
        deepAgentBorderFlow 3.6s linear infinite;
}

.deep-agent-card {
    position: relative;
    overflow: hidden;
    border: 1px solid transparent;
    border-radius: var(--radius);
    background:
        linear-gradient(var(--sidebar-panel), var(--sidebar-panel)) padding-box,
        linear-gradient(135deg, #4285f4, #a142f4, #ea4335, #fbbc04, #34a853, #00acc1, #4285f4) border-box;
    background-size: 100% 100%, 320% 320%;
    padding: 0.85rem;
    margin: 0.2rem 0 0.75rem;
    box-shadow: 0 12px 30px rgba(66, 133, 244, 0.12);
    animation: deepAgentBorderFlow 5.4s linear infinite;
}

.deep-agent-card::before {
    content: "";
    position: absolute;
    inset: 0 0 auto 0;
    height: 2px;
    background: linear-gradient(90deg, #4285f4, #a142f4, #ea4335, #fbbc04, #34a853, #00acc1);
    background-size: 280% 100%;
    animation: deepAgentBorderFlow 3.8s linear infinite;
}

.deep-agent-card-title {
    color: var(--ink) !important;
    font-size: 0.9rem;
    font-weight: 780;
    line-height: 1.25;
}

.deep-agent-card-detail {
    color: var(--muted) !important;
    font-size: 0.76rem;
    line-height: 1.45;
    margin-top: 0.22rem;
}

.deep-agent-card-status {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    color: var(--green) !important;
    font-size: 0.72rem;
    font-weight: 760;
    margin-top: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

@keyframes deepAgentGlow {
    0%, 100% { opacity: 0.72; transform: scale(1); }
    50% { opacity: 1; transform: scale(1.18); }
}

@keyframes deepAgentBorderFlow {
    0% { background-position: 0% 50%, 0% 50%; }
    100% { background-position: 0% 50%, 300% 50%; }
}

.hero-panel {
    border: 1px solid var(--line);
    border-radius: var(--radius);
    background: var(--panel);
    box-shadow: var(--shadow);
    padding: clamp(1.2rem, 4vw, 2.2rem);
    margin-top: 1rem;
}

.hero-grid {
    display: grid;
    grid-template-columns: minmax(0, 1.3fr) minmax(240px, 0.7fr);
    gap: 1.2rem;
    align-items: stretch;
}

.hero-title {
    font-size: clamp(1.65rem, 4vw, 3rem);
    line-height: 1.02;
    max-width: 740px;
    font-weight: 820;
    letter-spacing: 0;
    color: var(--ink);
}

.hero-copy {
    color: var(--muted);
    margin-top: 0.85rem;
    font-size: clamp(0.95rem, 1.6vw, 1.05rem);
    line-height: 1.6;
    max-width: 620px;
}

.signal-panel {
    border: 1px solid var(--line);
    border-radius: var(--radius);
    background: var(--panel-soft);
    padding: 1rem;
    display: grid;
    align-content: space-between;
    gap: 1rem;
}

.signal-title {
    color: var(--ink);
    font-weight: 720;
    font-size: 0.92rem;
}

.signal-list {
    display: grid;
    gap: 0.6rem;
}

.signal-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
    color: var(--muted);
    font-size: 0.82rem;
}

.signal-dot {
    width: 0.58rem;
    height: 0.58rem;
    border-radius: 50%;
    background: var(--green);
    flex: 0 0 auto;
}

.signal-dot.teal { background: var(--teal); }
.signal-dot.amber { background: var(--amber); }
.signal-dot.coral { background: var(--coral); }

.suggestion-wrap {
    margin-top: 1rem;
}

.section-kicker {
    color: var(--muted);
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 0.4rem 0 0.7rem;
}

.sidebar-brand {
    display: grid;
    gap: 0.65rem;
    padding: 1rem 0 0.6rem;
}

.sidebar-mark {
    width: 2.4rem;
    height: 2.4rem;
    border-radius: var(--radius);
    display: grid;
    place-items: center;
    background: #ffffff;
    color: var(--text-on-light) !important;
    font-weight: 850;
    letter-spacing: 0;
}

.sidebar-title {
    color: #ffffff;
    font-weight: 760;
    font-size: 1rem;
}

.sidebar-note {
    color: var(--muted) !important;
    font-size: 0.78rem;
    line-height: 1.45;
}

.sidebar-section-title {
    color: var(--muted) !important;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 0.65rem 0 0.55rem;
}

.current-thread {
    border: 1px solid var(--sidebar-line);
    border-radius: var(--radius);
    background: var(--sidebar-panel);
    color: var(--muted) !important;
    font-size: 0.78rem;
    padding: 0.7rem 0.75rem;
    overflow-wrap: anywhere;
}

.tool-card {
    display: flex;
    align-items: center;
    gap: 0.72rem;
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: var(--radius);
    padding: 0.72rem 0.85rem;
    margin: 0.5rem 0;
    box-shadow: 0 8px 24px rgba(23, 25, 31, 0.05);
}

.tool-chip {
    width: 1.75rem;
    height: 1.75rem;
    border-radius: 999px;
    display: grid;
    place-items: center;
    background: var(--green);
    color: var(--text-on-light) !important;
    font-weight: 800;
    font-size: 0.72rem;
}

.tool-card.running .tool-chip {
    background: var(--amber);
    color: var(--text-on-light) !important;
}

.tool-label {
    color: var(--ink);
    font-weight: 680;
    font-size: 0.9rem;
}

.tool-state {
    margin-left: auto;
    color: var(--muted);
    font-size: 0.76rem;
}

.yt-card {
    display: grid;
    grid-template-columns: 136px minmax(0, 1fr);
    gap: 0.85rem;
    border: 1px solid var(--line);
    border-radius: var(--radius);
    background: var(--panel);
    padding: 0.65rem;
    margin: 0.55rem 0;
}

.yt-thumb {
    width: 136px;
    aspect-ratio: 16 / 9;
    object-fit: cover;
    border-radius: 6px;
    background: var(--panel-soft);
}

.yt-title {
    color: var(--ink);
    font-weight: 680;
    font-size: 0.92rem;
    line-height: 1.35;
}

.yt-link {
    display: inline-block;
    color: var(--teal);
    font-size: 0.82rem;
    margin-top: 0.45rem;
    text-decoration: none;
    font-weight: 680;
}

.image-frame {
    border: 1px solid var(--line);
    border-radius: var(--radius);
    background: var(--panel);
    padding: 0.35rem;
    margin: 0.65rem 0;
}

.agent-progress {
    display: flex;
    align-items: center;
    gap: 0.85rem;
    border: 1px solid var(--line);
    border-radius: var(--radius);
    background: rgba(13, 13, 15, 0.88);
    box-shadow: 0 10px 28px rgba(23, 25, 31, 0.06);
    padding: 0.85rem 0.95rem;
    margin: 0.65rem 0;
}

.agent-spinner {
    width: 1.45rem;
    height: 1.45rem;
    border-radius: 50%;
    border: 3px solid var(--line-strong);
    border-top-color: var(--indigo);
    border-right-color: var(--teal);
    animation: agentSpin 0.78s linear infinite;
    flex: 0 0 auto;
}

.agent-progress-copy {
    min-width: 0;
}

.agent-progress-phase {
    color: var(--ink);
    font-weight: 760;
    font-size: 0.92rem;
    line-height: 1.25;
}

.agent-progress-detail {
    color: var(--muted);
    font-size: 0.78rem;
    line-height: 1.35;
    margin-top: 0.12rem;
}

.phase-steps {
    display: flex;
    align-items: center;
    gap: 0.35rem;
    flex-wrap: wrap;
    margin-left: auto;
}

.phase-step {
    width: 0.45rem;
    height: 0.45rem;
    border-radius: 50%;
    background: var(--line-strong);
}

.phase-step.active {
    background: var(--indigo);
}

@keyframes agentSpin {
    to { transform: rotate(360deg); }
}

.notice-card {
    position: relative;
    overflow: hidden;
    display: flex;
    align-items: flex-start;
    gap: 0.85rem;
    border: 1px solid var(--line);
    border-radius: var(--radius);
    background: rgba(13, 13, 15, 0.92);
    box-shadow: 0 14px 34px rgba(23, 25, 31, 0.07);
    padding: 0.95rem 1rem;
    margin: 0.65rem 0;
}

.notice-card::before {
    content: "";
    position: absolute;
    inset: 0 auto 0 0;
    width: 4px;
    background: var(--indigo);
}

.notice-card::after {
    content: "";
    position: absolute;
    inset: -40% auto auto -12%;
    width: 9rem;
    height: 9rem;
    border-radius: 50%;
    background: rgba(0, 0, 0, 0.06);
    animation: noticeBreathe 2.4s ease-in-out infinite;
}

.notice-card.notice-success::before { background: var(--green); }
.notice-card.notice-success::after { background: rgba(0, 0, 0, 0.05); }
.notice-card.notice-warning::before { background: var(--amber); }
.notice-card.notice-warning::after { background: rgba(0, 0, 0, 0.07); }
.notice-card.notice-token::before { background: var(--coral); }
.notice-card.notice-token::after { background: rgba(0, 0, 0, 0.08); }
.notice-card.notice-error::before { background: var(--coral); }
.notice-card.notice-error::after { background: rgba(0, 0, 0, 0.08); }

.notice-orb {
    position: relative;
    z-index: 1;
    width: 2rem;
    height: 2rem;
    border-radius: 50%;
    display: grid;
    place-items: center;
    background: #ffffff;
    color: var(--text-on-light) !important;
    font-weight: 850;
    flex: 0 0 auto;
    animation: noticePulse 1.8s ease-in-out infinite;
}

.notice-copy {
    position: relative;
    z-index: 1;
    min-width: 0;
}

.notice-title {
    color: var(--ink);
    font-weight: 790;
    line-height: 1.25;
}

.notice-detail {
    color: var(--muted);
    font-size: 0.86rem;
    line-height: 1.55;
    margin-top: 0.24rem;
}

section[data-testid="stSidebar"] .notice-card {
    background: var(--sidebar-panel);
    border-color: var(--sidebar-line);
    box-shadow: none;
}

section[data-testid="stSidebar"] .notice-title {
    color: #f2f2f2;
}

section[data-testid="stSidebar"] .notice-detail {
    color: var(--muted);
}

@keyframes noticePulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.06); }
}

@keyframes noticeBreathe {
    0%, 100% { opacity: 0.55; transform: scale(1); }
    50% { opacity: 0.9; transform: scale(1.08); }
}

[data-testid="stChatMessage"] {
    border: 1px solid var(--line);
    border-radius: var(--radius);
    background: rgba(13, 13, 15, 0.88);
    box-shadow: 0 10px 28px rgba(23, 25, 31, 0.06);
    padding: 0.72rem;
}

[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p {
    line-height: 1.62;
}

[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3,
[data-testid="stMarkdownContainer"] h4,
[data-testid="stMarkdownContainer"] code,
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] p,
[data-testid="stText"] {
    color: var(--ink) !important;
}

[data-testid="stMarkdownContainer"] blockquote,
[data-testid="stMarkdownContainer"] blockquote p {
    color: var(--muted) !important;
    border-left-color: var(--indigo) !important;
}

[data-testid="stMarkdownContainer"] code,
[data-testid="stCodeBlock"] {
    background: #05060a !important;
    color: #fef3c7 !important;
    border-color: var(--line) !important;
}

.stJson,
[data-testid="stJson"] {
    color: var(--ink) !important;
}

.stJson pre,
[data-testid="stJson"] pre,
[data-testid="stJson"] span,
[data-testid="stJson"] div {
    color: var(--ink) !important;
}

[data-testid="stAlert"] {
    color: var(--ink) !important;
}

[data-testid="stAlert"] p,
[data-testid="stAlert"] span,
[data-testid="stAlert"] div {
    color: var(--ink) !important;
}

[data-testid="stExpander"] {
    background: var(--panel) !important;
    border-color: var(--line) !important;
}

[data-testid="stExpander"] summary,
[data-testid="stExpander"] p,
[data-testid="stExpander"] span {
    color: var(--ink) !important;
}

.stTextInput input,
.stTextArea textarea,
.stSelectbox div,
.stMultiSelect div,
.stNumberInput input {
    background: var(--panel) !important;
    color: var(--ink) !important;
    border-color: var(--line-strong) !important;
}

.stButton > button {
    border-radius: var(--radius) !important;
    border: 1px solid var(--line-strong) !important;
    background: var(--panel) !important;
    color: var(--ink) !important;
    min-height: 2.7rem;
    font-weight: 680 !important;
    transition: transform 120ms ease, border-color 120ms ease, box-shadow 120ms ease !important;
    white-space: normal !important;
}

.stButton > button:hover {
    border-color: var(--indigo) !important;
    box-shadow: 0 10px 26px rgba(255, 255, 255, 0.08) !important;
    transform: translateY(-1px);
}

section[data-testid="stSidebar"] .stButton > button {
    background: var(--sidebar-panel) !important;
    border-color: var(--sidebar-line) !important;
    color: #f2f2f2 !important;
}

section[data-testid="stSidebar"] .stButton > button *,
section[data-testid="stSidebar"] .stButton > button p,
section[data-testid="stSidebar"] .stButton > button span {
    color: inherit !important;
}

section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: #f2f2f2 !important;
    border-color: #f2f2f2 !important;
    color: var(--text-on-light) !important;
}

section[data-testid="stSidebar"] .stButton > button[kind="primary"] *,
section[data-testid="stSidebar"] .stButton > button[kind="primary"] p,
section[data-testid="stSidebar"] .stButton > button[kind="primary"] span {
    color: var(--text-on-light) !important;
}

[data-testid="stBottom"],
[data-testid="stBottom"] > div,
[data-testid="stBottom"] > div > div,
.stChatFloatingInputContainer,
.stChatFloatingInputContainer > div {
    background: transparent !important;
    border-top: none !important;
    box-shadow: none !important;
}

[data-testid="stChatInput"],
[data-testid="stChatInput"] > div {
    border-radius: var(--radius) !important;
}

[data-testid="stChatInput"] {
    position: relative !important;
    isolation: isolate !important;
    overflow: hidden !important;
    max-width: 900px !important;
    margin: 0 auto 0.85rem !important;
    padding: 2px !important;
    background: var(--panel) !important;
    border: none !important;
    box-shadow: 0 14px 36px rgba(0, 0, 0, 0.38) !important;
}

[data-testid="stChatInput"]::before,
[data-testid="stChatInput"]::after {
    content: "" !important;
    position: absolute !important;
    inset: -70% !important;
    z-index: 0 !important;
    background:
        conic-gradient(
            from 0deg,
            #4285f4,
            #a142f4,
            #ea4335,
            #fbbc04,
            #34a853,
            #00acc1,
            #4285f4
        ) !important;
    animation: chatInputAuraSpin 9s linear infinite !important;
}

[data-testid="stChatInput"]::after {
    filter: blur(16px) !important;
    opacity: 0.22 !important;
    animation-duration: 13s !important;
}

[data-testid="stChatInput"]:focus-within {
    box-shadow:
        0 14px 38px rgba(0, 0, 0, 0.48),
        0 0 0 3px rgba(167, 139, 250, 0.18) !important;
}

[data-testid="stChatInput"] > div {
    background: var(--panel) !important;
    border: none !important;
    border-radius: calc(var(--radius) - 2px) !important;
    box-shadow: none !important;
    position: relative !important;
    z-index: 1 !important;
}

@keyframes chatInputAuraSpin {
    to { transform: rotate(360deg); }
}

[data-testid="stChatInput"] textarea,
[data-testid="stChatInputTextArea"] {
    background: var(--panel) !important;
    color: var(--ink) !important;
    caret-color: var(--indigo) !important;
    font-size: 0.95rem !important;
}

[data-testid="stChatInputTextArea"]::placeholder {
    color: var(--muted) !important;
}

[data-testid="stChatInputSubmitButton"] > button {
    background: var(--ink) !important;
    border: none !important;
    border-radius: 7px !important;
}

[data-testid="stChatInputSubmitButton"] svg,
[data-testid="stChatInputSubmitButton"] svg path {
    color: var(--text-on-light) !important;
    fill: var(--text-on-light) !important;
    stroke: var(--text-on-light) !important;
}

@media (max-width: 860px) {
    .block-container {
        padding: 0.9rem 0.75rem 6rem !important;
    }

    .topbar {
        align-items: flex-start;
        flex-direction: column;
    }

    .status-row {
        justify-content: flex-start;
    }

    .hero-grid {
        grid-template-columns: 1fr;
    }

    .yt-card {
        grid-template-columns: 92px minmax(0, 1fr);
    }

    .yt-thumb {
        width: 92px;
    }

    .agent-progress {
        align-items: flex-start;
    }

    .phase-steps {
        display: none;
    }
}
</style>
""",
    unsafe_allow_html=True,
)


def init_state() -> None:
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())
    if "threads" not in st.session_state:
        st.session_state.threads = [st.session_state.thread_id]
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = {}
    if "news" not in st.session_state:
        st.session_state.news = []


init_state()

tid = st.session_state.thread_id
if tid not in st.session_state.chat_history:
    st.session_state.chat_history[tid] = []


TOOL_META = {
    "tavily_search_results_json": {"icon": "S", "label": "Tavily Search"},
    "tavilysearch": {"icon": "S", "label": "Tavily Search"},
    "search_youtube_videos": {"icon": "YT", "label": "YouTube Search"},
    "generate_stability_image": {"icon": "IM", "label": "Image Generator"},
    "serpapi_search": {"icon": "W", "label": "SerpAPI Search"},
    "calculator": {"icon": "C", "label": "Calculator"},
    "duckduckgosearch": {"icon": "W", "label": "DuckDuckGo"},
    "web_search": {"icon": "W", "label": "Web Search"},
    "stock": {"icon": "MK", "label": "Market Lookup"},
}

AGENT_PHASES = ["Thinking", "Reasoning", "Planning", "Executing", "Almost ready"]


def safe_html(value: object) -> str:
    return html.escape(str(value or ""), quote=True)


def safe_url(value: object) -> str:
    text = str(value or "").strip()
    if text.startswith(("http://", "https://")):
        return html.escape(text, quote=True)
    return ""


def compact_thread_id(thread_id: str, size: int = 8) -> str:
    return safe_html(thread_id[:size])


def get_tool_meta(name: str) -> dict:
    key_name = (name or "").lower()
    for key, val in TOOL_META.items():
        if key.lower() in key_name or key_name in key.lower():
            return val
    return {"icon": "T", "label": name or "Tool"}


def redact_debug_value(value: object) -> object:
    if isinstance(value, dict):
        redacted = {}
        for key, item in value.items():
            normalized_key = str(key).lower()
            if normalized_key in {"url", "base_url", "response_sample"}:
                redacted[key] = "[redacted]"
            else:
                redacted[key] = redact_debug_value(item)
        return redacted
    if isinstance(value, list):
        return [redact_debug_value(item) for item in value]
    return value


def render_tool_card(tool_name: str, state: str = "completed") -> None:
    meta = get_tool_meta(tool_name)
    state_text = "running" if state == "running" else "done"
    st.markdown(
        f"""
        <div class="tool-card {safe_html(state)}">
            <span class="tool-chip">{safe_html(meta["icon"])}</span>
            <span class="tool-label">{safe_html(meta["label"])}</span>
            <span class="tool-state">{state_text}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def phase_from_elapsed(started_at: float, has_tools: bool = False) -> str:
    if has_tools:
        return "Executing"

    elapsed = time.monotonic() - started_at
    if elapsed < 1.2:
        return "Thinking"
    if elapsed < 2.8:
        return "Reasoning"
    return "Planning"


def render_agent_progress(placeholder, phase: str, detail: str = "") -> None:
    phase = phase if phase in AGENT_PHASES else "Thinking"
    active_index = AGENT_PHASES.index(phase)
    detail = detail or "The agent is working through the request."
    steps = "".join(
        f'<span class="phase-step {"active" if index <= active_index else ""}"></span>'
        for index in range(len(AGENT_PHASES))
    )

    placeholder.markdown(
        f"""
        <div class="agent-progress" role="status" aria-live="polite">
            <div class="agent-spinner"></div>
            <div class="agent-progress-copy">
                <div class="agent-progress-phase">{safe_html(phase)}</div>
                <div class="agent-progress-detail">{safe_html(detail)}</div>
            </div>
            <div class="phase-steps">{steps}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


DEEP_STATUS_MARKER = "**Deep Research Progress:**"


def clean_progress_line(value: object) -> str:
    text = str(value or "")
    text = text.replace("\u2022", "-").replace("\u00e2\u20ac\u00a2", "-")
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.strip().lstrip("-*").strip()
    return " ".join(text.split())


def is_progress_line(value: object) -> bool:
    text = str(value or "").strip()
    if not text:
        return True
    return text.startswith(("-", "*", "\u2022", "\u00e2\u20ac\u00a2"))


def split_deep_research_status(content: str) -> tuple[str, str]:
    if DEEP_STATUS_MARKER not in content:
        return "", content

    before, after = content.split(DEEP_STATUS_MARKER, 1)
    status_lines = []
    remainder = []
    collecting_status = True

    for line in after.splitlines():
        if collecting_status and is_progress_line(line):
            cleaned_line = clean_progress_line(line)
            if cleaned_line:
                status_lines.append(cleaned_line)
            continue
        collecting_status = False
        remainder.append(line)

    detail = status_lines[-1] if status_lines else "Deep research agent is working through the request."
    answer_parts = [part.strip() for part in (before, "\n".join(remainder)) if part.strip()]
    return detail, "\n\n".join(answer_parts)


def make_notice(kind: str, title: str, detail: str) -> dict:
    return {"kind": kind, "title": title, "detail": detail}


def render_notice_card(title: str, detail: str, kind: str = "error", placeholder=None) -> None:
    kind = kind if kind in {"success", "warning", "token", "error"} else "error"
    orb_text = {"success": "OK", "warning": "!", "token": "TL", "error": "!"}[kind]
    markup = f"""
        <div class="notice-card notice-{safe_html(kind)}" role="status" aria-live="polite">
            <div class="notice-orb">{safe_html(orb_text)}</div>
            <div class="notice-copy">
                <div class="notice-title">{safe_html(title)}</div>
                <div class="notice-detail">{safe_html(detail)}</div>
            </div>
        </div>
    """

    if placeholder is None:
        st.markdown(markup, unsafe_allow_html=True)
    else:
        placeholder.markdown(markup, unsafe_allow_html=True)


def classify_failure_text(text: object) -> dict | None:
    raw_text = str(text or "").strip()
    normalized = raw_text.lower()
    if not normalized:
        return None

    token_markers = [
        "token limit",
        "tokens per minute",
        "tpm",
        "rate limit",
        "ratelimit",
        "quota",
        "insufficient_quota",
        "context length",
        "context_length_exceeded",
        "maximum context",
        "max_tokens",
        "too many tokens",
        "429",
    ]
    if any(marker in normalized for marker in token_markers):
        return make_notice(
            "token",
            "Token limit exceeded",
            "The model limit looks used up for now. Please come back tomorrow, or try again with a shorter question.",
        )

    endpoint_markers = [
        "deep agent service unavailable",
        "service unavailable",
        "could not be reached",
        "cannot reach",
        "connection failed",
        "connection refused",
        "endpoint returned",
        "endpoints tried",
        "all endpoints returned errors",
        "timeout",
        "timed out",
        "http 500",
        "http 502",
        "http 503",
        "http 504",
    ]
    if any(marker in normalized for marker in endpoint_markers):
        return make_notice(
            "warning",
            "Oops, the service did not finish",
            "The endpoint may be waking up, busy, or returned an incomplete response. Please wait a moment and try again.",
        )

    function_call_markers = [
        "failed_generation",
        "failed to call a function",
    ]
    if any(marker in normalized for marker in function_call_markers):
        return make_notice(
            "warning",
            "Oops, the tool response was not formatted",
            "The search or tool ran, but the model could not format the final response. Please try the request again with a little more detail.",
        )

    if normalized.startswith("error:") or normalized.startswith("exception:"):
        return make_notice(
            "error",
            "Oops, something went wrong",
            "The agent hit an unexpected issue. Please try again in a moment.",
        )

    return None


def classify_service_test(result: dict) -> dict:
    status = str(result.get("status", "")).lower()
    endpoints = result.get("working_endpoints", []) or []
    code = result.get("code")

    def is_http_okish(value: object) -> bool:
        try:
            return int(value) < 500
        except (TypeError, ValueError):
            return False

    base_reachable = status == "connected" or is_http_okish(code)
    endpoint_reachable = any(is_http_okish(endpoint.get("status")) for endpoint in endpoints)
    post_ready = any(
        str(endpoint.get("method", "")).upper() == "POST"
        and int(endpoint.get("status", 0)) in {200, 201, 202}
        for endpoint in endpoints
        if str(endpoint.get("status", "")).isdigit()
    )
    post_alive = any(
        str(endpoint.get("method", "")).upper() == "POST"
        and is_http_okish(endpoint.get("status"))
        for endpoint in endpoints
    )

    if post_ready:
        return make_notice(
            "success",
            "Deep agent is ready",
            f"The service responded and the deep task endpoint passed the quick check. {len(endpoints)} endpoint checks returned.",
        )
    if base_reachable and post_alive:
        return make_notice(
            "warning",
            "Deep agent is reachable",
            "The service is online, but the quick POST probe did not return a final success. Your real request can still work if the endpoint expects a richer payload.",
        )
    if base_reachable or endpoint_reachable:
        return make_notice(
            "success",
            "Deep agent service is reachable",
            "The base service responded. If a deep request takes a while, the service may still be warming up.",
        )
    if status == "timeout":
        return make_notice(
            "warning",
            "Deep agent is waking up",
            "The service took too long to answer. Render services can need a short warm-up before the first request completes.",
        )
    return make_notice(
        "error",
        "Oops, service is not reachable",
        "The UI could not connect to the deep agent right now. Please retry after a minute or check the service deployment.",
    )


def render_youtube_results(data: object) -> None:
    try:
        videos = json.loads(data) if isinstance(data, str) else data
    except Exception:
        st.text(str(data))
        return

    if not isinstance(videos, list):
        st.json(videos)
        return

    for video in videos:
        if not isinstance(video, dict):
            continue

        title = safe_html(video.get("title", "Untitled video"))
        link = safe_url(video.get("link", ""))
        thumbnail = safe_url(video.get("thumbnail", ""))
        image_markup = (
            f'<img class="yt-thumb" src="{thumbnail}" alt="">'
            if thumbnail
            else '<div class="yt-thumb"></div>'
        )
        link_markup = (
            f'<a class="yt-link" href="{link}" target="_blank" rel="noopener noreferrer">Open video</a>'
            if link
            else ""
        )

        st.markdown(
            f"""
            <div class="yt-card">
                {image_markup}
                <div>
                    <div class="yt-title">{title}</div>
                    {link_markup}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_image(data: object) -> None:
    try:
        payload = json.loads(data) if isinstance(data, str) else data
        if not isinstance(payload, dict):
            st.text(str(data))
            return

        if "image_data" in payload:
            img_bytes = base64.b64decode(payload["image_data"])
            image = Image.open(BytesIO(img_bytes))
            st.markdown('<div class="image-frame">', unsafe_allow_html=True)
            st.image(image, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        elif "error" in payload:
            st.error(f"Image generation failed: {payload['error']}")
        else:
            st.json(payload)
    except Exception:
        st.text(str(data))


def render_tool_result(tool_name: str, content: object) -> None:
    tool_key = (tool_name or "").lower()
    if "youtube" in tool_key:
        render_youtube_results(content)
    elif "image" in tool_key or "stability" in tool_key:
        render_image(content)
    else:
        try:
            parsed = json.loads(content) if isinstance(content, str) else content
            st.json(parsed)
        except Exception:
            st.text(str(content))


def render_chat_message(role: str, content: str, is_status: bool = False) -> None:
    avatar_role = "user" if role == "user" else "assistant"
    with st.chat_message(avatar_role):
        if is_status:
            st.caption("Deep research agent")
        st.markdown(content or "_No response was returned._")


def render_message(msg: dict) -> None:
    role = msg.get("role")
    content = msg.get("content", "")

    if role == "user":
        render_chat_message("user", content)
    elif role == "assistant":
        _, visible_content = split_deep_research_status(str(content))
        if visible_content:
            render_chat_message("assistant", visible_content)
    elif role == "notice":
        render_notice_card(
            msg.get("title", "Oops, something went wrong"),
            msg.get("detail", "Please try again in a moment."),
            msg.get("kind", "error"),
        )
    elif role == "tool_call":
        render_tool_card(msg.get("tool_name", "tool"), "completed")
        if msg.get("render_output"):
            render_tool_result(msg.get("tool_name", ""), msg.get("tool_output", ""))
    elif role == "tool_result_text":
        st.text(str(content))


def render_history() -> None:
    for message in st.session_state.chat_history.get(tid, []):
        render_message(message)


def render_assistant_stream(placeholder, content: str, is_status: bool = False) -> None:
    with placeholder.container():
        with st.chat_message("assistant"):
            if is_status:
                st.caption("Deep research agent")
            if content:
                st.markdown(content)
            st.caption("Thinking...")


def stream_chat(user_prompt: str) -> None:
    config = {"configurable": {"thread_id": tid}}
    input_msg = {"messages": [HumanMessage(content=user_prompt)]}

    st.session_state.chat_history[tid].append({"role": "user", "content": user_prompt})
    render_chat_message("user", user_prompt)

    status_placeholder = st.empty()
    tool_placeholder = st.empty()
    ai_placeholder = st.empty()

    full_text = ""
    is_deep_research_request = requires_deep_research(user_prompt)
    active_tool_calls = {}
    finished_tools = []
    tool_messages = []
    started_at = time.monotonic()
    current_phase = "Thinking"

    def update_agent_progress(phase: str | None = None, detail: str = "") -> None:
        nonlocal current_phase
        if phase is None:
            phase = phase_from_elapsed(started_at, has_tools=bool(active_tool_calls))
        if AGENT_PHASES.index(phase) < AGENT_PHASES.index(current_phase):
            phase = current_phase
        current_phase = phase
        render_agent_progress(status_placeholder, phase, detail)

    update_agent_progress("Thinking", "Reading your query and preparing the response path.")
    time.sleep(0.12)
    update_agent_progress("Reasoning", "Reviewing context and intent.")
    time.sleep(0.12)
    update_agent_progress("Planning", "Choosing the next action.")
    if is_deep_research_request:
        update_agent_progress("Executing", "Deep research agent is collecting and synthesizing results.")

    def render_active_tools() -> None:
        with tool_placeholder.container():
            if not active_tool_calls and not finished_tools:
                st.empty()
                return

            for finished_name in finished_tools:
                render_tool_card(finished_name, "completed")
            for tool_data in active_tool_calls.values():
                render_tool_card(tool_data.get("name", "Tool"), "running")

    try:
        stream_iterator = chatbot.stream(input_msg, config, stream_mode="messages")

        for chunk, metadata in stream_iterator:
            node = metadata.get("langgraph_node", "")
            update_agent_progress(detail="Reasoning over the conversation context.")

            tool_call_chunks = getattr(chunk, "tool_call_chunks", None) or getattr(chunk, "tool_calls", None)
            if tool_call_chunks:
                for tool_chunk in tool_call_chunks:
                    tool_id = tool_chunk.get("id")
                    tool_name = tool_chunk.get("name", "")
                    if tool_id and tool_id not in active_tool_calls:
                        active_tool_calls[tool_id] = {"name": tool_name or "Tool", "args": ""}
                    if tool_id and tool_name:
                        active_tool_calls[tool_id]["name"] = tool_name
                update_agent_progress("Planning", "Selecting the right tool or route for this step.")
                render_active_tools()

            if isinstance(chunk, ToolMessage):
                tool_name = chunk.name or "Tool"
                matched_id = None
                for tool_id, tool_data in active_tool_calls.items():
                    if tool_data.get("name", "").lower() == tool_name.lower():
                        matched_id = tool_id
                        break
                if matched_id is None and active_tool_calls:
                    matched_id = next(iter(active_tool_calls))
                if matched_id:
                    finished_tools.append(active_tool_calls.pop(matched_id).get("name", tool_name))
                else:
                    finished_tools.append(tool_name)
                tool_messages.append(chunk)
                update_agent_progress("Executing", f"Finished running {tool_name}.")
                render_active_tools()

            if node == "chat_node" and hasattr(chunk, "content") and chunk.content:
                if isinstance(chunk.content, str):
                    if tool_call_chunks:
                        continue

                    deep_status_detail, response_fragment = split_deep_research_status(chunk.content)
                    if deep_status_detail:
                        update_agent_progress("Executing", deep_status_detail)
                    if not response_fragment.strip():
                        continue

                    if not full_text:
                        update_agent_progress("Executing", "Running the response path.")
                    full_text += response_fragment
                    update_agent_progress("Almost ready", "Composing the final response.")
                    render_assistant_stream(ai_placeholder, full_text)

    except Exception as exc:
        status_placeholder.empty()
        debug_log(traceback.format_exc())
        error_text = str(exc)
        notice = classify_failure_text(error_text)
        if notice is None and (
            "api" in error_text.lower()
            or "key" in error_text.lower()
            or "401" in error_text
            or "403" in error_text
        ):
            notice = make_notice(
                "error",
                "Authentication needs attention",
                "One service could not authenticate. Please check the deployment environment variables.",
            )
        if notice is None:
            notice = make_notice(
                "error",
                "Oops, the agent stopped",
                "The request could not be completed right now. Please try again in a moment.",
            )
        render_notice_card(notice["title"], notice["detail"], notice["kind"], placeholder=ai_placeholder)
        st.session_state.chat_history.setdefault(tid, []).append({"role": "notice", **notice})
        return

    if full_text:
        ai_placeholder.empty()
        notice = classify_failure_text(full_text)
        if notice:
            render_notice_card(notice["title"], notice["detail"], notice["kind"])
        else:
            render_chat_message("assistant", full_text)
    else:
        notice = make_notice(
            "warning",
            "Oops, no response came back",
            "The agent finished without returning text. Please try again with a shorter or clearer query.",
        )
        render_notice_card(notice["title"], notice["detail"], notice["kind"])

    history = st.session_state.chat_history.setdefault(tid, [])
    for tool_msg in tool_messages:
        tool_name = tool_msg.name or "Tool"
        content = tool_msg.content or ""
        rich_tools = {"youtube", "stock", "image", "stability"}
        should_render = any(key in tool_name.lower() for key in rich_tools)
        history.append(
            {
                "role": "tool_call",
                "tool_name": tool_name,
                "tool_output": content,
                "render_output": should_render,
            }
        )
        if should_render:
            render_tool_result(tool_name, content)

    if full_text:
        notice = classify_failure_text(full_text)
        if notice:
            history.append({"role": "notice", **notice})
        else:
            history.append(
                {
                    "role": "assistant",
                    "content": full_text,
                    "is_status": False,
                }
            )
    else:
        history.append(
            {
                "role": "notice",
                **notice,
            }
        )

    tool_placeholder.empty()
    status_placeholder.empty()
    debug_log(f"stream completed with {len(tool_messages)} tool messages")


with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-mark">AI</div>
            <div>
                <div class="sidebar-title">Agentic AI</div>
                <div class="sidebar-note">LangGraph workspace</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sidebar-section-title">Conversation</div>', unsafe_allow_html=True)
    if st.button("New chat", use_container_width=True, type="primary"):
        new_tid = str(uuid.uuid4())
        st.session_state.threads.insert(0, new_tid)
        st.session_state.thread_id = new_tid
        st.session_state.chat_history[new_tid] = []
        st.rerun()

    st.markdown(
        f'<div class="current-thread">Thread {compact_thread_id(tid, 12)}</div>',
        unsafe_allow_html=True,
    )

    st.divider()
    message_count = len(st.session_state.chat_history.get(tid, []))
    thread_count = len(st.session_state.threads)
    metric_col_1, metric_col_2 = st.columns(2)
    metric_col_1.metric("Messages", message_count)
    metric_col_2.metric("Threads", thread_count)

    st.divider()
    st.markdown('<div class="sidebar-section-title">Deep agent</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="deep-agent-card">
            <div class="deep-agent-card-title">Deep agent enabled</div>
            <div class="deep-agent-card-detail">Research route is ready for detailed analysis.</div>
            <div class="deep-agent-card-status">
                <span class="deep-agent-spark"></span>
                Live
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Test service", use_container_width=True):
        try:
            result = test_deep_agent_connection()
        except Exception as exc:
            debug_log(traceback.format_exc())
            render_notice_card(
                "Oops, service check failed",
                "The check could not complete from this UI session. Please try again in a moment.",
                "error",
            )
            if APP_DEBUG:
                st.caption(f"{type(exc).__name__}: {exc}")
        else:
            notice = classify_service_test(result)
            render_notice_card(notice["title"], notice["detail"], notice["kind"])
            if APP_DEBUG:
                with st.expander("Debug details"):
                    st.json(redact_debug_value(result))


st.markdown(
    f"""
    <div class="app-shell">
        <div class="topbar">
            <div class="brand-lockup">
                <div class="brand-mark">AI</div>
                <div>
                    <div class="brand-title">Agentic Chat</div>
                    <div class="brand-subtitle">Thread {compact_thread_id(tid, 16)}</div>
                </div>
            </div>
            <div class="status-row">
                <div class="status-pill"><strong>Live</strong></div>
                <div class="deep-agent-pill"><span class="deep-agent-spark"></span><span>Deep agent live</span></div>
                <div class="thread-pill">{len(st.session_state.chat_history.get(tid, []))} messages</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

history = st.session_state.chat_history.get(tid, [])

if "quick_prompt" in st.session_state:
    quick_prompt = st.session_state.pop("quick_prompt")
    stream_chat(quick_prompt)
    st.rerun()

if not history:
    st.markdown(
        """
        <div class="hero-panel">
            <div class="hero-grid">
                <div>
                    <div class="section-kicker">Agent console</div>
                    <div class="hero-title">Agentic Chat</div>
                    <div class="hero-copy">New session ready.</div>
                </div>
                <div class="signal-panel">
                    <div class="signal-title">Active routes</div>
                    <div class="signal-list">
                        <div class="signal-item"><span><span class="signal-dot"></span> Search</span><span>ready</span></div>
                        <div class="signal-item"><span><span class="signal-dot teal"></span> Video</span><span>ready</span></div>
                        <div class="signal-item"><span><span class="signal-dot amber"></span> Image</span><span>ready</span></div>
                        <div class="signal-item"><span><span class="signal-dot coral"></span> Math</span><span>ready</span></div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="suggestion-wrap"><div class="section-kicker">Prompts</div></div>', unsafe_allow_html=True)
    suggestions = [
        "Search latest AI news",
        "Find Python tutorials on YouTube",
        "Calculate 1234 x 5678",
        "Search for LangGraph tutorials",
        "What is machine learning?",
        "Explain quantum computing",
    ]

    columns = st.columns(3)
    for index, label in enumerate(suggestions):
        with columns[index % 3]:
            if st.button(label, key=f"suggestion_{index}", use_container_width=True):
                st.session_state["quick_prompt"] = label
                st.rerun()
else:
    render_history()


prompt = st.chat_input("Message the agent")

if prompt:
    cleaned_prompt = prompt.strip()
    if cleaned_prompt:
        stream_chat(cleaned_prompt)
        st.rerun()
