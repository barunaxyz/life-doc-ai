import streamlit as st
import json
import os
import time
from agent.documentary_agent import DocumentaryAgent
from utils.formatter import format_timeline, format_chapters, format_story, format_insights
from config import NOTION_TOKEN
from mcp.mcp_server import start_mcp_server, is_server_running

# ── Start MCP Server on app load ─────────────────────────────
if NOTION_TOKEN and "your_" not in NOTION_TOKEN:
    start_mcp_server(NOTION_TOKEN, port=3100)

# ── Page Config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Life Doc AI — Your Story, Reimagined",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ───────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Playfair+Display:ital,wght@0,400;0,700;1,400&display=swap');

/* ── Root variables ── */
:root {
    --accent-1: #7C3AED;
    --accent-2: #EC4899;
    --accent-3: #06B6D4;
    --surface: #0F0F1A;
    --surface-light: #1A1A2E;
    --surface-card: #16162A;
    --text-primary: #F1F5F9;
    --text-secondary: #94A3B8;
    --glass-bg: rgba(22, 22, 42, 0.6);
    --glass-border: rgba(124, 58, 237, 0.15);
    --gradient-main: linear-gradient(135deg, #7C3AED 0%, #EC4899 50%, #06B6D4 100%);
    --gradient-soft: linear-gradient(135deg, rgba(124,58,237,0.15) 0%, rgba(236,72,153,0.10) 50%, rgba(6,182,212,0.08) 100%);
}

/* ── Global overrides ── */
.stApp {
    background: var(--surface) !important;
    font-family: 'Inter', sans-serif !important;
}

.block-container {
    max-width: 1100px !important;
    padding-top: 2rem !important;
}

/* ── Hide Streamlit header/footer ── */
header[data-testid="stHeader"] { background: transparent !important; }
#MainMenu, footer { visibility: hidden; }

/* ── Hero section ── */
.hero-container {
    text-align: center;
    padding: 3rem 1rem 2rem;
    position: relative;
}

.hero-badge {
    display: inline-block;
    background: var(--gradient-soft);
    border: 1px solid var(--glass-border);
    padding: 6px 18px;
    border-radius: 50px;
    font-size: 0.78rem;
    color: var(--accent-1);
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 1.2rem;
}

.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 3.4rem;
    font-weight: 700;
    background: var(--gradient-main);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.15;
    margin-bottom: 1rem;
}

.hero-subtitle {
    font-size: 1.15rem;
    color: var(--text-secondary);
    font-weight: 300;
    max-width: 600px;
    margin: 0 auto 2rem;
    line-height: 1.7;
}

/* ── Glow orbs background ── */
.glow-orb {
    position: fixed;
    border-radius: 50%;
    filter: blur(120px);
    opacity: 0.12;
    pointer-events: none;
    z-index: 0;
}
.orb-1 { width: 500px; height: 500px; background: var(--accent-1); top: -100px; left: -100px; }
.orb-2 { width: 400px; height: 400px; background: var(--accent-2); bottom: 50px; right: -80px; }
.orb-3 { width: 350px; height: 350px; background: var(--accent-3); top: 40%; left: 50%; }

/* ── Generate button ── */
.stButton > button {
    background: var(--gradient-main) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 0.85rem 2.8rem !important;
    font-size: 1.05rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 4px 25px rgba(124, 58, 237, 0.35) !important;
}
.stButton > button:hover {
    transform: translateY(-2px) scale(1.02) !important;
    box-shadow: 0 8px 35px rgba(124, 58, 237, 0.5) !important;
}
.stButton > button:active {
    transform: translateY(0) scale(0.98) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    background: var(--surface-card);
    border-radius: 16px;
    padding: 6px;
    border: 1px solid var(--glass-border);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 12px !important;
    color: var(--text-secondary) !important;
    font-weight: 500 !important;
    padding: 10px 24px !important;
    font-size: 0.92rem !important;
    transition: all 0.25s ease !important;
}
.stTabs [aria-selected="true"] {
    background: var(--gradient-main) !important;
    color: white !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 15px rgba(124, 58, 237, 0.3) !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }
.stTabs [data-baseweb="tab-border"] { display: none !important; }

/* ── Content cards ── */
.glass-card {
    background: var(--glass-bg);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid var(--glass-border);
    border-radius: 20px;
    padding: 2rem 2.2rem;
    margin-bottom: 1.5rem;
    transition: border-color 0.3s ease;
}
.glass-card:hover {
    border-color: rgba(124, 58, 237, 0.35);
}

.card-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 1.2rem;
}
.card-icon {
    width: 44px;
    height: 44px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.3rem;
    flex-shrink: 0;
}
.icon-purple { background: linear-gradient(135deg, rgba(124,58,237,0.2), rgba(124,58,237,0.05)); }
.icon-pink { background: linear-gradient(135deg, rgba(236,72,153,0.2), rgba(236,72,153,0.05)); }
.icon-cyan { background: linear-gradient(135deg, rgba(6,182,212,0.2), rgba(6,182,212,0.05)); }
.icon-amber { background: linear-gradient(135deg, rgba(245,158,11,0.2), rgba(245,158,11,0.05)); }

.card-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.35rem;
    font-weight: 700;
    color: var(--text-primary);
}

.card-body {
    color: var(--text-secondary);
    font-size: 0.95rem;
    line-height: 1.85;
}
.card-body strong, .card-body b {
    color: var(--text-primary);
    font-weight: 600;
}
.card-body h1, .card-body h2, .card-body h3, .card-body h4 {
    color: var(--text-primary);
    font-family: 'Playfair Display', serif;
    margin-top: 1.5rem;
    margin-bottom: 0.6rem;
}
.card-body ul, .card-body ol {
    padding-left: 1.2rem;
}
.card-body li {
    margin-bottom: 0.5rem;
}
.card-body li::marker {
    color: var(--accent-1);
}

/* ── Metric cards row ── */
.metrics-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin-bottom: 2rem;
}
.metric-card {
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    border-radius: 16px;
    padding: 1.4rem;
    text-align: center;
    transition: transform 0.25s ease, border-color 0.25s ease;
}
.metric-card:hover {
    transform: translateY(-3px);
    border-color: rgba(124,58,237,0.35);
}
.metric-value {
    font-family: 'Inter', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    background: var(--gradient-main);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.metric-label {
    font-size: 0.8rem;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 4px;
    font-weight: 500;
}

/* ── Divider ── */
.fancy-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--glass-border), var(--accent-1), var(--glass-border), transparent);
    margin: 2rem 0;
    border: none;
}

/* ── Footer ── */
.app-footer {
    text-align: center;
    color: var(--text-secondary);
    font-size: 0.78rem;
    padding: 2rem 0 1rem;
    opacity: 0.6;
}
.app-footer a { color: var(--accent-1); text-decoration: none; }

/* ── Success alert override ── */
.stAlert [data-testid="stAlertContentSuccess"] {
    background: linear-gradient(135deg, rgba(16,185,129,0.1), rgba(6,182,212,0.05)) !important;
    border: 1px solid rgba(16,185,129,0.2) !important;
    border-radius: 14px !important;
    color: #6EE7B7 !important;
}

/* ── Spinner overlay ── */
.stSpinner > div { color: var(--accent-1) !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--surface); }
::-webkit-scrollbar-thumb { background: var(--accent-1); border-radius: 8px; }

/* ── Animate entrance ── */
@keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(20px); }
    to   { opacity: 1; transform: translateY(0); }
}
.animate-in {
    animation: fadeSlideUp 0.6s ease forwards;
}
.delay-1 { animation-delay: 0.1s; opacity: 0; }
.delay-2 { animation-delay: 0.2s; opacity: 0; }
.delay-3 { animation-delay: 0.3s; opacity: 0; }
.delay-4 { animation-delay: 0.4s; opacity: 0; }
</style>
""", unsafe_allow_html=True)


# ── Glow orbs ────────────────────────────────────────────────
st.markdown("""
<div class="glow-orb orb-1"></div>
<div class="glow-orb orb-2"></div>
<div class="glow-orb orb-3"></div>
""", unsafe_allow_html=True)


# ── Hero Section ─────────────────────────────────────────────
st.markdown("""
<div class="hero-container">
    <div class="hero-badge">✦ Powered by AI + Notion MCP</div>
    <div class="hero-title">Life Doc AI</div>
    <div class="hero-subtitle">
        Transform your Notion journals and life events into a cinematic, 
        AI-crafted documentary of your personal journey.
    </div>
</div>
""", unsafe_allow_html=True)


# ── Generate Button (centered) ───────────────────────────────
col_l, col_c, col_r = st.columns([1, 2, 1])
with col_c:
    generate_clicked = st.button("🎬  Generate My Life Documentary", type="primary", use_container_width=True)


# ── Main Logic ───────────────────────────────────────────────
if generate_clicked:
    # Progress animation
    progress_bar = st.progress(0)
    status_text = st.empty()

    steps = [
        ("🔌  Connecting to Notion MCP Server...", 15),
        ("📖  Calling MCP tools to read databases...", 35),
        ("🧠  AI is analyzing your journey...", 55),
        ("✍️  Crafting your narrative...", 75),
        ("🎬  Rendering final documentary...", 90),
    ]

    for msg, pct in steps:
        status_text.markdown(f"<p style='text-align:center; color:#94A3B8; font-size:0.95rem;'>{msg}</p>", unsafe_allow_html=True)
        progress_bar.progress(pct)
        time.sleep(0.4)

    agent = DocumentaryAgent()
    result = agent.generate_documentary()

    progress_bar.progress(100)
    status_text.empty()
    progress_bar.empty()

    # ── Success banner ──
    st.success("✨ Your Life Documentary is Ready!")

    # ── Metrics row ──
    events = result.get("timeline", [])
    chapters = result.get("chapters", [])
    insights = result.get("insights", [])

    st.markdown(f"""
    <div class="metrics-row animate-in">
        <div class="metric-card">
            <div class="metric-value">{len(events)}</div>
            <div class="metric-label">Life Events</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{len(chapters)}</div>
            <div class="metric-label">Chapters</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{len(insights)}</div>
            <div class="metric-label">Insights</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tabs ──
    tab1, tab2, tab3, tab4 = st.tabs(["📜  Story", "⏳  Timeline", "📚  Chapters", "💡  Insights"])

    with tab1:
        story_content = format_story(result.get("story", ""))
        st.markdown(f"""
        <div class="glass-card animate-in delay-1">
            <div class="card-header">
                <div class="card-icon icon-purple">📜</div>
                <div class="card-title">The Story of You</div>
            </div>
            <div class="card-body">{story_content}</div>
        </div>
        """, unsafe_allow_html=True)

    with tab2:
        ai_timeline = result.get("ai_timeline", "")
        base_timeline = format_timeline(result.get("timeline", []))
        st.markdown(f"""
        <div class="glass-card animate-in delay-1">
            <div class="card-header">
                <div class="card-icon icon-cyan">🤖</div>
                <div class="card-title">AI-Generated Timeline</div>
            </div>
            <div class="card-body">{ai_timeline}</div>
        </div>
        <div class="fancy-divider"></div>
        <div class="glass-card animate-in delay-2">
            <div class="card-header">
                <div class="card-icon icon-cyan">⏳</div>
                <div class="card-title">Structured Timeline</div>
            </div>
            <div class="card-body">{base_timeline}</div>
        </div>
        """, unsafe_allow_html=True)

    with tab3:
        ai_chapters = result.get("ai_chapters", "")
        base_chapters = format_chapters(result.get("chapters", []))
        st.markdown(f"""
        <div class="glass-card animate-in delay-1">
            <div class="card-header">
                <div class="card-icon icon-pink">🤖</div>
                <div class="card-title">AI-Generated Chapters</div>
            </div>
            <div class="card-body">{ai_chapters}</div>
        </div>
        <div class="fancy-divider"></div>
        <div class="glass-card animate-in delay-2">
            <div class="card-header">
                <div class="card-icon icon-pink">📚</div>
                <div class="card-title">Structured Chapters</div>
            </div>
            <div class="card-body">{base_chapters}</div>
        </div>
        """, unsafe_allow_html=True)

    with tab4:
        ai_insights = result.get("ai_insights", "")
        base_insights = format_insights(result.get("insights", []))
        st.markdown(f"""
        <div class="glass-card animate-in delay-1">
            <div class="card-header">
                <div class="card-icon icon-amber">🤖</div>
                <div class="card-title">Psychological & Life Insights</div>
            </div>
            <div class="card-body">{ai_insights}</div>
        </div>
        <div class="fancy-divider"></div>
        <div class="glass-card animate-in delay-2">
            <div class="card-header">
                <div class="card-icon icon-amber">💡</div>
                <div class="card-title">Key Findings</div>
            </div>
            <div class="card-body">{base_insights}</div>
        </div>
        """, unsafe_allow_html=True)


# ── MCP Status ───────────────────────────────────────────────
mcp_status = "🟢 MCP Server Active" if is_server_running() else "🔴 MCP Server Offline"
st.markdown(f"""
<div style="text-align:center;margin-bottom:1rem;">
    <span style="font-size:0.8rem;background:rgba(124,58,237,0.1);border:1px solid rgba(124,58,237,0.2);
    padding:5px 14px;border-radius:20px;color:#A78BFA;font-weight:500;">{mcp_status}</span>
</div>
""", unsafe_allow_html=True)

# ── Footer ───────────────────────────────────────────────────
st.markdown("""
<div class="fancy-divider"></div>
<div class="app-footer">
    Built with ❤️ for the <a href="https://dev.to/challenges/notion-2026-03-04">Notion MCP Challenge</a> &nbsp;·&nbsp; 
    Life Doc AI © 2025 &nbsp;·&nbsp; Powered by Notion MCP + Python
</div>
""", unsafe_allow_html=True)
