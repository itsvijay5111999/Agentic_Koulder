"""
Agentic AI Chatbot — Streamlit Frontend
========================================
Place this file in the SAME directory as your backend file (backend.py).
Run with: streamlit run streamlit_app.py
"""

import streamlit as st
import json
import base64
import uuid
import time
from datetime import datetime
from io import BytesIO
from PIL import Image

# ─── LangChain / LangGraph imports ───────────────────────────────────────────
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, AIMessageChunk

# ─── Backend import ───────────────────────────────────────────────────────────
# Adjust the import path / module name if your backend file is named differently.
try:
    from backend import chatbot, retrieve_all_threads, get_latest_news
except ImportError as e:
    st.error(
        f"❌ Could not import backend: {e}\n\n"
        "Make sure **backend.py** is in the same directory as this file."
    )
    st.stop()

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG & GLOBAL CSS
# ═══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Agentic AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── Root Variables ── */
:root {
    --bg:        #0d0f14;
    --surface:   #161923;
    --border:    #242836;
    --accent:    #6c63ff;
    --accent2:   #00e5ff;
    --success:   #1db954;
    --warn:      #f59e0b;
    --danger:    #ef4444;
    --text:      #e8eaf6;
    --muted:     #6b7280;
    --user-bg:   #1e2235;
    --ai-bg:     #151923;
    --radius:    12px;
    --shadow:    0 4px 24px rgba(0,0,0,.5);
}

/* ── App Background ── */
.stApp { background: var(--bg); color: var(--text); font-family: 'DM Sans', sans-serif; }
section[data-testid="stSidebar"] { background: var(--surface) !important; border-right: 1px solid var(--border); }

/* ── Hide default streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1rem !important; padding-bottom: 5rem !important; }

/* ── Typography ── */
h1,h2,h3 { font-family: 'Space Mono', monospace; }

/* ── Chat message containers ── */
.msg-user {
    background: var(--user-bg);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    border-radius: var(--radius);
    padding: 14px 18px;
    margin: 10px 0;
    font-size: 0.95rem;
    line-height: 1.6;
}
.msg-ai {
    background: var(--ai-bg);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent2);
    border-radius: var(--radius);
    padding: 14px 18px;
    margin: 10px 0;
    font-size: 0.95rem;
    line-height: 1.6;
}
.msg-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 8px;
    opacity: 0.6;
}
.msg-user .msg-label  { color: var(--accent); }
.msg-ai   .msg-label  { color: var(--accent2); }

/* ── Tool indicator cards ── */
.tool-card {
    display: flex;
    align-items: center;
    gap: 10px;
    background: #1a1f2e;
    border: 1px solid var(--border);
    border-left: 3px solid var(--warn);
    border-radius: 8px;
    padding: 10px 14px;
    margin: 6px 0;
    font-family: 'Space Mono', monospace;
    font-size: 0.78rem;
    color: var(--warn);
    animation: pulse 1.5s ease-in-out infinite;
}
.tool-card.done {
    border-left-color: var(--success);
    color: var(--success);
    animation: none;
}
@keyframes pulse {
    0%,100% { opacity: 1; }
    50%      { opacity: 0.55; }
}

/* ── Spinner dot ── */
.dot-spin {
    width: 10px; height: 10px;
    border-radius: 50%;
    background: var(--warn);
    display: inline-block;
    animation: dotpulse .8s ease-in-out infinite;
}
.dot-done { background: var(--success) !important; animation: none !important; }
@keyframes dotpulse {
    0%,100% { transform: scale(1); opacity:1; }
    50%      { transform: scale(1.5); opacity:.6; }
}

/* ── Sidebar widgets ── */
.sidebar-section {
    background: #1a1f2e;
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 14px;
    margin-bottom: 14px;
}
.sidebar-title {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 10px;
}

/* ── Thread pill buttons ── */
.stButton > button {
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.85rem !important;
    transition: all .2s ease !important;
}

/* ── YouTube card ── */
.yt-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
    margin: 8px 0;
    display: flex;
    gap: 12px;
    padding: 10px;
    transition: border-color .2s;
}
.yt-card:hover { border-color: var(--accent2); }
.yt-thumb { border-radius: 6px; width: 120px; height: 68px; object-fit: cover; }
.yt-title { font-size: 0.85rem; color: var(--text); font-weight: 500; line-height: 1.4; }
.yt-link  { font-size: 0.75rem; color: var(--accent2); text-decoration: none; }

/* ── Stock card ── */
.stock-card {
    background: linear-gradient(135deg, #1a1f2e 0%, #12161f 100%);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 18px 22px;
    margin: 8px 0;
}
.stock-symbol { font-family: 'Space Mono', monospace; font-size: 1.4rem; color: var(--accent2); }
.stock-price  { font-family: 'Space Mono', monospace; font-size: 2rem; font-weight: 700; color: var(--text); }
.stock-change { font-size: 0.85rem; margin-top: 4px; }

/* ── News card ── */
.news-item {
    border-bottom: 1px solid var(--border);
    padding: 8px 0;
    font-size: 0.82rem;
    line-height: 1.4;
}
.news-item a { color: var(--accent2); text-decoration: none; }
.news-item a:hover { color: var(--accent); }

/* ── Chat input bottom bar — full dark override ── */
/* Outer fixed bar Streamlit wraps the input in */
[data-testid="stBottom"],
[data-testid="stBottom"] > div,
[data-testid="stBottom"] > div > div,
.stChatFloatingInputContainer,
.stChatFloatingInputContainer > div {
    background: #0d0f14 !important;
    border-top: 1px solid #242836 !important;
    box-shadow: none !important;
}
/* The input pill itself */
[data-testid="stChatInput"],
[data-testid="stChatInput"] > div {
    background: #161923 !important;
    border: 1px solid #242836 !important;
    border-radius: 12px !important;
    box-shadow: none !important;
}
/* The textarea */
[data-testid="stChatInput"] textarea,
[data-testid="stChatInputTextArea"] {
    background: #161923 !important;
    color: #e8eaf6 !important;
    caret-color: #6c63ff !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    border: none !important;
    box-shadow: none !important;
}
[data-testid="stChatInput"] textarea::placeholder,
[data-testid="stChatInputTextArea"]::placeholder {
    color: #4b5563 !important;
}
/* Send button */
[data-testid="stChatInputSubmitButton"] > button {
    background: #6c63ff !important;
    border: none !important;
    color: white !important;
    border-radius: 8px !important;
}
[data-testid="stChatInputSubmitButton"] > button:hover {
    background: #5a52e0 !important;
}
[data-testid="stChatInputSubmitButton"] > button svg path {
    fill: white !important;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 12px !important;
}

/* ── Image display ── */
.gen-image-wrap {
    border: 1px solid var(--border);
    border-radius: var(--radius);
    overflow: hidden;
    margin: 10px 0;
    background: var(--surface);
    padding: 4px;
}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE INIT
# ═══════════════════════════════════════════════════════════════════════════════
def init_state():
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = str(uuid.uuid4())
    if "threads" not in st.session_state:
        existing = [t[0] for t in retrieve_all_threads()]
        st.session_state.threads = existing if existing else [st.session_state.thread_id]
        if st.session_state.thread_id not in st.session_state.threads:
            st.session_state.threads.insert(0, st.session_state.thread_id)
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = {}          # {thread_id: [msg_dicts]}
    if "streaming" not in st.session_state:
        st.session_state.streaming = False
    if "news" not in st.session_state:
        st.session_state.news = []

init_state()

# ─── Ensure current thread has a history list ─────────────────────────────────
tid = st.session_state.thread_id
if tid not in st.session_state.chat_history:
    st.session_state.chat_history[tid] = []


# ═══════════════════════════════════════════════════════════════════════════════
# TOOL METADATA
# ═══════════════════════════════════════════════════════════════════════════════
TOOL_META = {
    "tavily_search_results_json": {"icon": "🔍", "label": "Tavily Search",    "color": "#6c63ff"},
    "TavilySearch":               {"icon": "🔍", "label": "Tavily Search",    "color": "#6c63ff"},
    "search_youtube_videos":      {"icon": "▶️",  "label": "YouTube Search",  "color": "#ff0000"},
    "generate_stability_image":   {"icon": "🎨",  "label": "Image Generator", "color": "#ec4899"},
    "SerpAPI_Search":             {"icon": "🌐",  "label": "SerpAPI Search",  "color": "#00e5ff"},
    "get_stock_price":            {"icon": "📈",  "label": "Stock Lookup",    "color": "#1db954"},
    "calculator":                 {"icon": "🧮",  "label": "Calculator",      "color": "#f59e0b"},
    "DuckDuckGoSearch":           {"icon": "🦆",  "label": "DuckDuckGo",      "color": "#de5833"},
    "web_search":                 {"icon": "🌐",  "label": "Web Search",      "color": "#00e5ff"},
}

def get_tool_meta(name: str) -> dict:
    for key, val in TOOL_META.items():
        if key.lower() in name.lower() or name.lower() in key.lower():
            return val
    return {"icon": "🔧", "label": name, "color": "#f59e0b"}


# ═══════════════════════════════════════════════════════════════════════════════
# RICH CONTENT RENDERERS
# ═══════════════════════════════════════════════════════════════════════════════
def render_youtube_results(data_str: str):
    """Render YouTube video cards."""
    try:
        videos = json.loads(data_str)
        if isinstance(videos, list):
            for v in videos:
                st.markdown(f"""
                <div class="yt-card">
                    <img class="yt-thumb" src="{v.get('thumbnail','')}">
                    <div>
                        <div class="yt-title">{v.get('title','')}</div>
                        <a class="yt-link" href="{v.get('link','')}" target="_blank">
                            ▶ Watch on YouTube
                        </a>
                    </div>
                </div>""", unsafe_allow_html=True)
    except Exception:
        st.text(data_str)


def render_stock_data(data_str: str):
    """Render stock price card."""
    try:
        d = json.loads(data_str) if isinstance(data_str, str) else data_str
        gq = d.get("Global Quote", {})
        if gq:
            symbol  = gq.get("01. symbol", "N/A")
            price   = gq.get("05. price", "0")
            change  = gq.get("09. change", "0")
            pct     = gq.get("10. change percent", "0%")
            volume  = gq.get("06. volume", "N/A")
            is_pos  = float(change) >= 0

            change_color = "#1db954" if is_pos else "#ef4444"
            arrow = "▲" if is_pos else "▼"
            st.markdown(f"""
            <div class="stock-card">
                <div class="stock-symbol">{symbol}</div>
                <div class="stock-price">${float(price):.2f}</div>
                <div class="stock-change" style="color:{change_color}">
                    {arrow} {change} ({pct}) &nbsp;·&nbsp; Vol: {int(volume):,}
                </div>
            </div>""", unsafe_allow_html=True)
        else:
            st.json(d)
    except Exception:
        st.text(str(data_str))


def render_image(data_str: str):
    """Render a base64 generated image."""
    try:
        d = json.loads(data_str) if isinstance(data_str, str) else data_str
        if "image_data" in d:
            img_bytes = base64.b64decode(d["image_data"])
            img = Image.open(BytesIO(img_bytes))
            st.markdown('<div class="gen-image-wrap">', unsafe_allow_html=True)
            st.image(img, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        elif "error" in d:
            st.error(f"Image generation failed: {d['error']}")
    except Exception as e:
        st.text(str(data_str))


def render_tool_result(tool_name: str, content: str):
    """Route tool output to the correct renderer or fallback to text."""
    tl = tool_name.lower()
    if "youtube" in tl:
        render_youtube_results(content)
    elif "stock" in tl:
        render_stock_data(content)
    elif "image" in tl or "stability" in tl:
        render_image(content)
    else:
        # Generic: try pretty JSON, else plain text
        try:
            parsed = json.loads(content)
            st.json(parsed)
        except Exception:
            st.markdown(content)


# ═══════════════════════════════════════════════════════════════════════════════
# RENDER EXISTING MESSAGES
# ═══════════════════════════════════════════════════════════════════════════════
def render_message(msg: dict):
    """Render a single stored message dict."""
    role    = msg["role"]
    content = msg.get("content", "")

    if role == "user":
        st.markdown(f"""
        <div class="msg-user">
            <div class="msg-label">You</div>
            {content}
        </div>""", unsafe_allow_html=True)

    elif role == "assistant":
        st.markdown(f"""
        <div class="msg-ai">
            <div class="msg-label">⚡ Agent</div>
            {content if content else '<em style="opacity:.4">Processing…</em>'}
        </div>""", unsafe_allow_html=True)

    elif role == "tool_call":
        meta = get_tool_meta(msg.get("tool_name", ""))
        st.markdown(f"""
        <div class="tool-card done">
            <span>✅</span>
            <span>{meta['icon']} {meta['label']}</span>
            <span style="color:#6b7280;margin-left:auto;font-size:.7rem">completed</span>
        </div>""", unsafe_allow_html=True)
        if msg.get("render_output"):
            render_tool_result(msg["tool_name"], msg["tool_output"])

    elif role == "tool_result_text":
        st.markdown(msg.get("content", ""))


def render_history():
    """Render all messages in the current thread."""
    history = st.session_state.chat_history.get(tid, [])
    for msg in history:
        render_message(msg)


# ═══════════════════════════════════════════════════════════════════════════════
# STREAMING CORE
# ═══════════════════════════════════════════════════════════════════════════════
def stream_chat(user_prompt: str):
    """
    Stream the agent response token-by-token.
    Show tool-call indicators as they fire.
    """
    config    = {"configurable": {"thread_id": tid}}
    input_msg = {"messages": [HumanMessage(content=user_prompt)]}

    # Append user message to history
    st.session_state.chat_history[tid].append({"role": "user", "content": user_prompt})
    st.markdown(f"""
    <div class="msg-user">
        <div class="msg-label">You</div>
        {user_prompt}
    </div>""", unsafe_allow_html=True)

    # Placeholders we'll update live
    tool_placeholder = st.empty()
    ai_placeholder   = st.empty()

    # Tracking state
    full_text         = ""
    active_tool_calls = {}   # id → {name, args_str}
    finished_tools    = []   # list of tool names already completed
    tool_messages     = []   # ToolMessage objects received

    def render_active_tools():
        if not active_tool_calls and not finished_tools:
            tool_placeholder.empty()
            return
        html = ""
        for tc in finished_tools:
            meta = get_tool_meta(tc)
            html += f"""
            <div class="tool-card done">
                <span class="dot-spin dot-done"></span>
                <span>{meta['icon']} {meta['label']}</span>
                <span style="color:#6b7280;margin-left:auto;font-size:.7rem">done</span>
            </div>"""
        for tc_id, tc_data in active_tool_calls.items():
            meta = get_tool_meta(tc_data["name"])
            html += f"""
            <div class="tool-card">
                <span class="dot-spin"></span>
                <span>{meta['icon']} {meta['label']}</span>
                <span style="color:#6b7280;margin-left:auto;font-size:.7rem">running…</span>
            </div>"""
        tool_placeholder.markdown(html, unsafe_allow_html=True)

    # ── Stream ──────────────────────────────────────────────────────────────
    try:
        for chunk, metadata in chatbot.stream(
            input_msg, config, stream_mode="messages"
        ):
            node = metadata.get("langgraph_node", "")

            # ── Tool call being assembled (AIMessageChunk) ─────────────────
            if hasattr(chunk, "tool_call_chunks") and chunk.tool_call_chunks:
                for tc_chunk in chunk.tool_call_chunks:
                    tc_id   = tc_chunk.get("id")
                    tc_name = tc_chunk.get("name", "")
                    if tc_id and tc_id not in active_tool_calls:
                        active_tool_calls[tc_id] = {"name": tc_name, "args": ""}
                    if tc_id and tc_name:
                        active_tool_calls[tc_id]["name"] = tc_name
                render_active_tools()

            # ── Tool result arrived (ToolMessage) ──────────────────────────
            if isinstance(chunk, ToolMessage):
                tool_name = chunk.name or "tool"
                # Mark corresponding tool call as finished
                for tc_id, tc_data in list(active_tool_calls.items()):
                    if tc_data["name"].lower() == tool_name.lower() or True:
                        finished_tools.append(tc_data["name"])
                        del active_tool_calls[tc_id]
                        break
                tool_messages.append(chunk)
                render_active_tools()

            # ── Streaming AI text (chat_node) ──────────────────────────────
            if node == "chat_node" and hasattr(chunk, "content") and chunk.content:
                if isinstance(chunk.content, str):
                    full_text += chunk.content
                    ai_placeholder.markdown(f"""
                    <div class="msg-ai">
                        <div class="msg-label">⚡ Agent</div>
                        {full_text}▌
                    </div>""", unsafe_allow_html=True)

    except Exception as e:
        ai_placeholder.error(f"Streaming error: {e}")
        return

    # ── Final AI message ─────────────────────────────────────────────────────
    if full_text:
        ai_placeholder.markdown(f"""
        <div class="msg-ai">
            <div class="msg-label">⚡ Agent</div>
            {full_text}
        </div>""", unsafe_allow_html=True)

    # ── Persist to history ───────────────────────────────────────────────────
    history = st.session_state.chat_history.setdefault(tid, [])

    # Store tool call records
    for tool_msg in tool_messages:
        tool_name = tool_msg.name or "tool"
        content   = tool_msg.content or ""
        # Decide if we want to render rich output
        rich_tools = {"youtube", "stock", "image", "stability"}
        should_render = any(r in tool_name.lower() for r in rich_tools)
        history.append({
            "role":         "tool_call",
            "tool_name":    tool_name,
            "tool_output":  content,
            "render_output": should_render,
        })
        # If rich tool, render inline now
        if should_render:
            render_tool_result(tool_name, content)

    # Store AI response
    if full_text:
        history.append({"role": "assistant", "content": full_text})

    tool_placeholder.empty()


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    # ── Logo / Header ─────────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center;padding:20px 0 14px">
        <div style="font-family:'Space Mono',monospace;font-size:1.3rem;
                    color:#6c63ff;letter-spacing:.05em">⚡ AGENTIC AI</div>
        <div style="font-size:.72rem;color:#6b7280;margin-top:4px;
                    letter-spacing:.1em;text-transform:uppercase">
            Multi-Tool Chat System
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ── Thread management ─────────────────────────────────────────────────────
    st.markdown('<div class="sidebar-title">💬 Conversations</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("＋ New Chat", use_container_width=True, type="primary"):
            new_tid = str(uuid.uuid4())
            st.session_state.threads.insert(0, new_tid)
            st.session_state.thread_id = new_tid
            st.session_state.chat_history[new_tid] = []
            st.rerun()
    with col2:
        if st.button("🗑", help="Clear current chat", use_container_width=True):
            st.session_state.chat_history[tid] = []
            st.rerun()

    st.markdown("<div style='height:6px'/>", unsafe_allow_html=True)

    # Show threads list
    all_threads = st.session_state.threads
    for t in all_threads[:15]:                        # cap at 15 for readability
        label     = f"💬 {t[:8]}…"
        is_active = t == tid
        btn_type  = "primary" if is_active else "secondary"
        if st.button(label, key=f"thread_{t}", use_container_width=True, type=btn_type):
            st.session_state.thread_id = t
            if t not in st.session_state.chat_history:
                st.session_state.chat_history[t] = []
            st.rerun()

    st.divider()

    # ── Tool Palette ──────────────────────────────────────────────────────────
    st.markdown('<div class="sidebar-title">🛠️ Available Tools</div>', unsafe_allow_html=True)
    tools_info = [
        ("🔍", "Tavily Search",    "AI-optimised deep search"),
        ("🌐", "SerpAPI Search",   "Real-time web results"),
        ("▶️", "YouTube Search",   "Video discovery"),
        ("🎨", "Image Generator",  "SDXL text-to-image"),
        ("📈", "Stock Lookup",     "Live market prices"),
        ("🧮", "Calculator",       "Basic arithmetic"),
    ]
    for icon, name, desc in tools_info:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:10px;
                    padding:7px 0;border-bottom:1px solid #242836;">
            <span style="font-size:1.1rem">{icon}</span>
            <div>
                <div style="font-size:.82rem;font-weight:500;color:#e8eaf6">{name}</div>
                <div style="font-size:.72rem;color:#6b7280">{desc}</div>
            </div>
        </div>""", unsafe_allow_html=True)

    st.divider()

    # ── Latest News ───────────────────────────────────────────────────────────
    st.markdown('<div class="sidebar-title">📰 Latest News</div>', unsafe_allow_html=True)
    if st.button("🔄 Refresh News", use_container_width=True):
        with st.spinner("Fetching headlines…"):
            st.session_state.news = get_latest_news()

    if not st.session_state.news:
        st.caption("Click 'Refresh News' to load top headlines.")
    else:
        for title, url in st.session_state.news[:8]:
            st.markdown(f"""
            <div class="news-item">
                <a href="{url}" target="_blank">{title}</a>
            </div>""", unsafe_allow_html=True)

    st.divider()

    # ── Stats ─────────────────────────────────────────────────────────────────
    msg_count = len(st.session_state.chat_history.get(tid, []))
    thread_count = len(st.session_state.threads)
    c1, c2 = st.columns(2)
    c1.metric("Messages", msg_count)
    c2.metric("Threads",  thread_count)

    st.markdown("""
    <div style="text-align:center;margin-top:16px;font-size:.7rem;color:#374151">
        Powered by LangGraph · Groq · SDXL
    </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN CHAT AREA
# ═══════════════════════════════════════════════════════════════════════════════

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;
            padding:4px 0 16px;border-bottom:1px solid #242836;margin-bottom:18px">
    <div>
        <h2 style="margin:0;font-family:'Space Mono',monospace;font-size:1.1rem;
                   color:#e8eaf6">⚡ Agentic Chat</h2>
        <div style="font-size:.75rem;color:#6b7280;margin-top:2px;
                    font-family:'Space Mono',monospace">
            Thread: {tid[:16]}…
        </div>
    </div>
    <div style="display:flex;gap:8px;">
        <div style="background:#1a1f2e;border:1px solid #242836;border-radius:6px;
                    padding:5px 10px;font-size:.75rem;color:#1db954">
            ● Live
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Empty state ───────────────────────────────────────────────────────────────
history = st.session_state.chat_history.get(tid, [])

# Quick-prompt trigger — set by suggestion buttons below
if "quick_prompt" in st.session_state:
    qp = st.session_state.pop("quick_prompt")
    stream_chat(qp)
    st.rerun()

if not history:
    # Hero text
    st.markdown("""
    <div style="text-align:center;padding:48px 20px 28px">
        <div style="font-size:2.8rem;margin-bottom:10px">⚡</div>
        <div style="font-family:'Space Mono',monospace;font-size:1.05rem;
                    color:#6b7280;margin-bottom:8px">
            Ready to assist
        </div>
        <div style="font-size:.875rem;color:#4b5563;max-width:420px;margin:0 auto;
                    line-height:1.6;">
            Ask me anything — I can search the web, find YouTube videos,
            generate images, look up stocks, and do maths.
        </div>
    </div>""", unsafe_allow_html=True)

    # Suggestion cards — 3 columns × 2 rows using real Streamlit buttons
    suggestions = [
        ("🔍", "Search latest AI news"),
        ("▶️", "Find Python tutorials on YouTube"),
        ("🎨", "Generate a futuristic city image"),
        ("📈", "What's Apple's stock price?"),
        ("🧮", "Calculate 1234 × 5678"),
        ("🌐", "Search for LangGraph tutorials"),
    ]

    # Inject button style override once
    st.markdown("""
    <style>
    div[data-testid="stHorizontalBlock"] button[kind="secondary"] {
        background: #161923 !important;
        border: 1px solid #242836 !important;
        border-radius: 10px !important;
        color: #9ca3af !important;
        font-size: .82rem !important;
        padding: 14px 10px !important;
        height: auto !important;
        white-space: normal !important;
        text-align: center !important;
        transition: border-color .2s, color .2s !important;
    }
    div[data-testid="stHorizontalBlock"] button[kind="secondary"]:hover {
        border-color: #6c63ff !important;
        color: #e8eaf6 !important;
    }
    </style>""", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    cols = [col1, col2, col3]
    for i, (icon, label) in enumerate(suggestions):
        with cols[i % 3]:
            if st.button(f"{icon}  {label}", key=f"sugg_{i}", use_container_width=True):
                st.session_state["quick_prompt"] = label
                st.rerun()

else:
    # ── Render existing messages ───────────────────────────────────────────────
    render_history()

# ── Chat input ────────────────────────────────────────────────────────────────────────────
# Re-inject CSS every render cycle so Streamlit late-mounted DOM nodes get styled.
_CHAT_BAR_CSS = (
    "<style>"
    "[data-testid='stBottom']{background:#0d0f14!important;"
    "border-top:1px solid #242836!important;}"
    "[data-testid='stBottom']>div,"
    "[data-testid='stBottom']>div>div{background:#0d0f14!important;}"
    "[data-testid='stChatInput']{background:#161923!important;"
    "border:1px solid #242836!important;border-radius:12px!important;}"
    "[data-testid='stChatInput']>div{background:#161923!important;"
    "border-radius:12px!important;}"
    "[data-testid='stChatInputTextArea']{background:#161923!important;"
    "color:#e8eaf6!important;caret-color:#6c63ff!important;}"
    "[data-testid='stChatInputTextArea']::placeholder{color:#4b5563!important;}"
    "[data-testid='stChatInputSubmitButton']>button{"
    "background:#6c63ff!important;border:none!important;border-radius:8px!important;}"
    ".stChatFloatingInputContainer,.stChatFloatingInputContainer>div{"
    "background:#0d0f14!important;box-shadow:none!important;}"
    "</style>"
)
st.markdown(_CHAT_BAR_CSS, unsafe_allow_html=True)

prompt = st.chat_input("Message the agent…  (search · image · stock · YouTube · maths)")

if prompt:
    stream_chat(prompt.strip())
    st.rerun()