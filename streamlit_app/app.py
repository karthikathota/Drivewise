import streamlit as st
import requests
import uuid

API_URL = "http://127.0.0.1:8000/recommend"

st.set_page_config(
    page_title="DriveWise — AI Vehicle Command",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════
# DESIGN SYSTEM
# Aesthetic: High-tech automotive command centre
# Palette:   Deep charcoal + electric teal + amber data readouts
# Fonts:     Orbitron (display) · Rajdhani (body) · JetBrains Mono (data)
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Rajdhani:wght@300;400;500;600&family=JetBrains+Mono:wght@300;400;500&display=swap');

/* ── Variables ── */
:root {
    --bg-deep:       #080c10;
    --bg-panel:      #0d1117;
    --bg-card:       #111820;
    --bg-elevated:   #161e28;
    --teal:          #00d4c8;
    --teal-dim:      rgba(0,212,200,0.12);
    --teal-glow:     rgba(0,212,200,0.30);
    --amber:         #f59e0b;
    --amber-dim:     rgba(245,158,11,0.10);
    --green:         #34d399;
    --blue:          #60a5fa;
    --red:           #ef4444;
    --text-primary:  #e2eaf4;
    --text-secondary:#7a8fa6;
    --text-muted:    #3d5068;
    --border:        rgba(0,212,200,0.13);
    --border-bright: rgba(0,212,200,0.38);
    --grid:          rgba(0,212,200,0.035);
}

/* ── Base ── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg-deep) !important;
    color: var(--text-primary) !important;
}

/* Dot-grid background */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(var(--grid) 1px, transparent 1px),
        linear-gradient(90deg, var(--grid) 1px, transparent 1px);
    background-size: 48px 48px;
    pointer-events: none;
    z-index: 0;
}

/* Corner glow */
[data-testid="stAppViewContainer"]::after {
    content: '';
    position: fixed;
    top: -180px; left: -180px;
    width: 560px; height: 560px;
    background: radial-gradient(circle, rgba(0,212,200,0.045) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
}

[data-testid="stSidebar"] {
    background: var(--bg-panel) !important;
    border-right: 1px solid var(--border) !important;
}

/* Hide chrome */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"], [data-testid="stToolbar"] { display: none; }

/* Global font */
*, p, span, div, label, li { font-family: 'Rajdhani', sans-serif !important; }

/* ── Keyframes ── */
@keyframes scanline {
    0%   { transform: translateX(-100%); opacity: 0; }
    10%  { opacity: 1; }
    90%  { opacity: 1; }
    100% { transform: translateX(100%); opacity: 0; }
}
@keyframes pulse-dot {
    0%, 100% { box-shadow: 0 0 0 0 var(--teal-glow); }
    50%       { box-shadow: 0 0 0 5px transparent; }
}
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes blink-cursor {
    0%, 100% { opacity: 1; }
    50%       { opacity: 0; }
}

/* ═══════════════════════════════
   HEADER
═══════════════════════════════ */
.dw-header {
    position: relative;
    border-bottom: 1px solid var(--border);
    padding: 22px 0 18px 0;
    margin-bottom: 20px;
    overflow: hidden;
}
/* Animated scan line across header bottom */
.dw-header::after {
    content: '';
    position: absolute;
    bottom: -1px; left: 0;
    width: 40%;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--teal), transparent);
    animation: scanline 3.5s ease-in-out infinite;
}
.dw-header-inner {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
}
.dw-logo {
    font-family: 'Orbitron', monospace !important;
    font-size: 2rem;
    font-weight: 900;
    letter-spacing: 0.14em;
    color: #ffffff;
    line-height: 1;
    text-shadow: 0 0 28px rgba(0,212,200,0.25);
}
.dw-logo span { color: var(--teal); }
.dw-version {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.6rem;
    color: var(--text-muted);
    letter-spacing: 0.2em;
    margin-top: 6px;
}
.dw-status-cluster {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 8px;
}
.dw-online {
    display: flex;
    align-items: center;
    gap: 8px;
}
.dw-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--teal);
    animation: pulse-dot 2s ease-in-out infinite;
}
.dw-online-label {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.62rem;
    color: var(--teal);
    letter-spacing: 0.16em;
    text-transform: uppercase;
}
.dw-tag-row { display: flex; gap: 5px; }
.dw-tag {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.55rem;
    padding: 2px 9px;
    border: 1px solid;
    letter-spacing: 0.08em;
    border-radius: 1px;
}
.dw-tag.t  { color: var(--teal);  border-color: rgba(0,212,200,0.35);  background: var(--teal-dim); }
.dw-tag.g  { color: var(--green); border-color: rgba(52,211,153,0.35); background: rgba(52,211,153,0.08); }
.dw-tag.b  { color: var(--blue);  border-color: rgba(96,165,250,0.35); background: rgba(96,165,250,0.08); }
.dw-tag.a  { color: var(--amber); border-color: rgba(245,158,11,0.35); background: var(--amber-dim); }

/* ═══════════════════════════════
   METRICS STRIP
═══════════════════════════════ */
.dw-metrics {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 2px;
    margin-bottom: 20px;
}
.dw-metric {
    background: var(--bg-card);
    border: 1px solid var(--border);
    padding: 11px 15px;
    position: relative;
    overflow: hidden;
}
.dw-metric::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
}
.dw-metric.c-teal::before  { background: var(--teal); }
.dw-metric.c-amber::before { background: var(--amber); }
.dw-metric.c-blue::before  { background: var(--blue); }
.dw-metric.c-green::before { background: var(--green); }
.dw-metric-lbl {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.56rem;
    color: var(--text-muted);
    letter-spacing: 0.16em;
    text-transform: uppercase;
    margin-bottom: 5px;
}
.dw-metric-val {
    font-family: 'Orbitron', monospace !important;
    font-weight: 700;
    font-size: 1.05rem;
    line-height: 1;
}
.dw-metric-val.c-teal  { color: var(--teal); }
.dw-metric-val.c-amber { color: var(--amber); }
.dw-metric-val.c-blue  { color: var(--blue); font-size: 0.68rem; margin-top: 4px; }
.dw-metric-val.c-green { color: var(--green); font-size: 0.68rem; margin-top: 4px; }

/* ═══════════════════════════════
   CHAT BUBBLES
═══════════════════════════════ */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    animation: fadeUp 0.28s ease forwards;
}
/* User */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) .stMarkdown {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border-bright) !important;
    border-left: 3px solid var(--teal) !important;
    border-radius: 0 3px 3px 0 !important;
    padding: 13px 18px 13px 16px !important;
    color: var(--text-primary) !important;
    font-size: 0.97rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.02em !important;
}
/* Assistant */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) .stMarkdown {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-left: 3px solid var(--amber) !important;
    border-radius: 0 3px 3px 0 !important;
    padding: 17px 22px 17px 18px !important;
    color: #c5d5e8 !important;
    font-size: 0.93rem !important;
    line-height: 1.78 !important;
}
/* Bold = teal orbitron in assistant */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) strong {
    color: var(--teal) !important;
    font-family: 'Orbitron', monospace !important;
    font-size: 0.76em !important;
    font-weight: 600 !important;
    letter-spacing: 0.07em !important;
}
/* Avatars */
[data-testid="stChatMessageAvatarUser"] {
    background: linear-gradient(135deg, var(--teal), #0099a8) !important;
    border-radius: 2px !important;
    border: 1px solid var(--teal) !important;
}
[data-testid="stChatMessageAvatarAssistant"] {
    background: var(--bg-elevated) !important;
    border-radius: 2px !important;
    border: 1px solid var(--amber) !important;
}

/* ═══════════════════════════════
   CHAT INPUT
═══════════════════════════════ */
[data-testid="stChatInputContainer"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-bright) !important;
    border-radius: 2px !important;
    margin-top: 10px !important;
}
[data-testid="stChatInput"] {
    background: transparent !important;
    border: none !important;
    color: var(--text-primary) !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 500 !important;
}
[data-testid="stChatInput"]::placeholder {
    color: var(--text-muted) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.08em !important;
}

/* ═══════════════════════════════
   EMPTY STATE
═══════════════════════════════ */
.dw-empty {
    text-align: center;
    padding: 52px 20px 36px;
    animation: fadeUp 0.4s ease forwards;
}
.dw-empty-icon { font-size: 2.8rem; display: block; margin-bottom: 14px;
    filter: drop-shadow(0 0 14px rgba(0,212,200,0.45)); }
.dw-empty-title {
    font-family: 'Orbitron', monospace !important;
    font-size: 1.2rem; font-weight: 700;
    color: #fff; letter-spacing: 0.1em; margin-bottom: 8px;
}
.dw-empty-sub {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.68rem; color: var(--text-secondary);
    letter-spacing: 0.06em; line-height: 1.9;
    max-width: 460px; margin: 0 auto 28px;
}
.dw-cards {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    max-width: 560px;
    margin: 0 auto;
}
.dw-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-left: 3px solid var(--teal);
    padding: 10px 14px;
    text-align: left;
}
.dw-card.a { border-left-color: var(--amber); }
.dw-card.g { border-left-color: var(--green); }
.dw-card.b { border-left-color: var(--blue);  }
.dw-card-lbl {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.58rem; color: var(--teal);
    letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 4px;
}
.dw-card.a .dw-card-lbl { color: var(--amber); }
.dw-card.g .dw-card-lbl { color: var(--green); }
.dw-card.b .dw-card-lbl { color: var(--blue);  }
.dw-card-txt { font-size: 0.83rem; color: var(--text-secondary); font-weight: 500; }

/* ═══════════════════════════════
   SIDEBAR
═══════════════════════════════ */
.sb-head {
    font-family: 'Orbitron', monospace !important;
    font-size: 0.62rem; font-weight: 600;
    color: var(--teal); letter-spacing: 0.2em;
    text-transform: uppercase;
    padding: 10px 0 7px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 10px;
}
.sb-agent {
    display: flex; align-items: center; gap: 9px;
    padding: 8px 10px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    margin-bottom: 4px;
}
.sb-agent-info { flex: 1; }
.sb-agent-name { font-size: 0.86rem; font-weight: 600; color: var(--text-primary); }
.sb-agent-desc {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.56rem; color: var(--text-muted); letter-spacing: 0.06em;
}
.sb-live { width: 6px; height: 6px; border-radius: 50%; background: var(--green); flex-shrink: 0; }
.sb-qitem {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.63rem; color: var(--text-secondary);
    padding: 6px 0; border-bottom: 1px solid rgba(0,212,200,0.05);
    letter-spacing: 0.03em; line-height: 1.5;
}
.sb-qitem::before { content: '›'; color: var(--teal); margin-right: 7px; font-weight: bold; }
.sb-info {
    background: var(--bg-card);
    border: 1px solid var(--border);
    padding: 10px 12px; margin-top: 12px;
}
.sb-info-lbl {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.56rem; color: var(--text-muted);
    letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 3px;
}
.sb-info-val {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.7rem; color: var(--teal);
}
.sb-qcount {
    font-family: 'Orbitron', monospace !important;
    font-size: 1.1rem; font-weight: 700; color: var(--amber);
}

/* Sidebar clear button */
[data-testid="stSidebar"] button {
    background: var(--bg-card) !important;
    border: 1px solid rgba(239,68,68,0.3) !important;
    color: var(--red) !important;
    border-radius: 2px !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.1em !important;
    width: 100% !important;
    transition: all 0.18s !important;
}
[data-testid="stSidebar"] button:hover {
    background: rgba(239,68,68,0.07) !important;
    border-color: var(--red) !important;
}

/* Misc */
hr { border: none !important; border-top: 1px solid var(--border) !important; margin: 12px 0 !important; }
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg-deep); }
::-webkit-scrollbar-thumb { background: var(--border-bright); }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════
if "messages"   not in st.session_state: st.session_state.messages   = []
if "session_id" not in st.session_state: st.session_state.session_id = str(uuid.uuid4())


# ═══════════════════════════════════════════════════════════════
# BACKEND
# ═══════════════════════════════════════════════════════════════
def call_backend(query: str) -> str:
    try:
        r = requests.post(
            API_URL,
            json={"question": query, "session_id": st.session_state.session_id},
            timeout=60
        )
        if r.status_code == 200:
            return r.json().get("answer", "No answer returned.")
        return f"⚠️ Backend error {r.status_code} — please retry."
    except requests.exceptions.ConnectionError:
        return "❌ LINK FAILURE — Backend offline. Run:\n```\nuvicorn agent_api.main:app --reload --port 8000\n```"
    except requests.exceptions.Timeout:
        return "⏱️ TIMEOUT — Agent pipeline exceeded 60s. Please retry."
    except Exception as e:
        return f"❌ SYSTEM ERROR — {e}"


# ═══════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="sb-head">◈ Agent Network</div>', unsafe_allow_html=True)

    for icon, name, desc in [
        ("💰", "Budget Agent",  "PRICE · RANGE · AFFORDABILITY"),
        ("👨‍👩‍👧", "Family Agent",  "SUV · CROSSOVER · MINIVAN"),
        ("⚡", "Eco Agent",     "EV · HYBRID · EMISSIONS"),
        ("💎", "Luxury Agent",  "PREMIUM · PRESTIGE · BRANDS"),
    ]:
        st.markdown(f"""
        <div class="sb-agent">
            <span style="font-size:1rem">{icon}</span>
            <div class="sb-agent-info">
                <div class="sb-agent-name">{name}</div>
                <div class="sb-agent-desc">{desc}</div>
            </div>
            <div class="sb-live"></div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sb-head" style="margin-top:16px">◈ Sample Queries</div>', unsafe_allow_html=True)
    for q in [
        "Family SUV around $50,000",
        "Luxury EV under $90k",
        "Eco crossover between $35k–$55k",
        "Premium BMW or Audi under $70k",
        "Hybrid SUV for a family under $55k",
        "Affordable crossover for daily use",
    ]:
        st.markdown(f'<div class="sb-qitem">{q}</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="sb-info">
        <div class="sb-info-lbl">Session ID</div>
        <div class="sb-info-val">{st.session_state.session_id[:16]}…</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    if st.button("⬛  CLEAR SESSION"):
        st.session_state.messages   = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()


# ═══════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<div class="dw-header">
  <div class="dw-header-inner">
    <div>
      <div class="dw-logo">DRIVE<span>WISE</span></div>
      <div class="dw-version">// MULTI-AGENT VEHICLE INTELLIGENCE SYSTEM &nbsp;·&nbsp; v2.0</div>
    </div>
    <div class="dw-status-cluster">
      <div class="dw-online">
        <div class="dw-dot"></div>
        <span class="dw-online-label">ALL AGENTS ONLINE</span>
      </div>
      <div class="dw-tag-row">
        <span class="dw-tag t">BUDGET</span>
        <span class="dw-tag g">FAMILY</span>
        <span class="dw-tag b">ECO</span>
        <span class="dw-tag a">LUXURY</span>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# METRICS STRIP
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<div class="dw-metrics">
  <div class="dw-metric c-teal">
    <div class="dw-metric-lbl">Active Agents</div>
    <div class="dw-metric-val c-teal">04</div>
  </div>
  <div class="dw-metric c-green">
    <div class="dw-metric-lbl">Response Standard</div>
    <div class="dw-metric-val c-green">350+ WORD ADVISORY</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# EMPTY STATE
# ═══════════════════════════════════════════════════════════════
if not st.session_state.messages:
    st.markdown("""
    <div class="dw-empty">
      <span class="dw-empty-icon">🚘</span>
      <div class="dw-empty-title">AWAITING QUERY INPUT</div>
      <div class="dw-empty-sub">
        Initialise the advisory sequence by describing your vehicle requirements.<br>
        Budget · Vehicle Type · Eco Preference · Luxury Tier — or any combination.
      </div>
      <div class="dw-cards">
        <div class="dw-card">
          <div class="dw-card-lbl">💰 Budget</div>
          <div class="dw-card-txt">Family SUV around $50,000</div>
        </div>
        <div class="dw-card a">
          <div class="dw-card-lbl">💎 Luxury</div>
          <div class="dw-card-txt">Premium EV under $90k</div>
        </div>
        <div class="dw-card g">
          <div class="dw-card-lbl">⚡ Eco</div>
          <div class="dw-card-txt">Hybrid crossover under $45k</div>
        </div>
        <div class="dw-card b">
          <div class="dw-card-lbl">🔀 Multi-Intent</div>
          <div class="dw-card-txt">Luxury hybrid family SUV ~$75k</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# CHAT HISTORY
# ═══════════════════════════════════════════════════════════════
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# ═══════════════════════════════════════════════════════════════
# CHAT INPUT
# ═══════════════════════════════════════════════════════════════
user_input = st.chat_input("// ENTER QUERY — budget · type · eco · luxury · any combination...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Dispatching agents — analysing query..."):
            response = call_backend(user_input)
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
    # No st.rerun() — causes double-render loop