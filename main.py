"""
main.py
Streamlit UI for Chat with SQL Database.
Imports agent and database modules — handles only UI logic here.
"""

import os
import streamlit as st
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler 
from dotenv import load_dotenv

from database import get_sqlite_db, get_mysql_db, get_db_info, build_sqlite_from_file
from agent import get_agent

load_dotenv()

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SQL Mind",
    page_icon="🗄️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&family=Inter:wght@300;400;500;600&display=swap');

/* ── Root tokens ── */
:root {
    --bg:        #0D0F14;
    --surface:   #141720;
    --surface2:  #1C2030;
    --border:    #252A3A;
    --accent:    #7C6AF7;
    --accent2:   #5DCAA5;
    --text:      #E2E4EE;
    --muted:     #6B7190;
    --danger:    #E24B4A;
    --radius:    12px;
    --mono:      'JetBrains Mono', monospace;
    --sans:      'Inter', sans-serif;
}

/* ── Global resets ── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--sans) !important;
}

[data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}

/* ── Hide default Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* ── Top bar ── */
.topbar {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 20px 0 28px 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 28px;
}
.topbar-icon {
    width: 44px; height: 44px;
    background: linear-gradient(135deg, var(--accent), #9B6AF7);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px;
    flex-shrink: 0;
}
.topbar-title {
    font-family: var(--mono);
    font-size: 22px;
    font-weight: 500;
    color: var(--text);
    letter-spacing: -0.5px;
}
.topbar-sub {
    font-size: 13px;
    color: var(--muted);
    margin-top: 2px;
}

/* ── Sidebar headings ── */
.sidebar-section {
    font-family: var(--mono);
    font-size: 11px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    color: var(--muted);
    padding: 18px 0 8px 0;
}

/* ── Status pill ── */
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 500;
    font-family: var(--mono);
}
.status-connected {
    background: rgba(93,202,165,0.12);
    color: var(--accent2);
    border: 1px solid rgba(93,202,165,0.25);
}
.status-disconnected {
    background: rgba(107,113,144,0.12);
    color: var(--muted);
    border: 1px solid var(--border);
}

/* ── Schema card ── */
.schema-card {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 12px 14px;
    margin: 6px 0;
    font-family: var(--mono);
    font-size: 12px;
    color: var(--muted);
    white-space: pre-wrap;
    line-height: 1.6;
}

/* ── Chat messages ── */
.msg-row {
    display: flex;
    gap: 12px;
    margin: 16px 0;
    align-items: flex-start;
}
.msg-avatar {
    width: 34px; height: 34px;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px;
    flex-shrink: 0;
}
.msg-avatar-user  { background: rgba(124,106,247,0.18); border: 1px solid rgba(124,106,247,0.3); }
.msg-avatar-ai    { background: rgba(93,202,165,0.12);  border: 1px solid rgba(93,202,165,0.25); }
.msg-bubble {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 0 var(--radius) var(--radius) var(--radius);
    padding: 14px 16px;
    max-width: 820px;
    font-size: 14px;
    line-height: 1.7;
    color: var(--text);
}
.msg-bubble-user {
    background: rgba(124,106,247,0.08);
    border-color: rgba(124,106,247,0.2);
    border-radius: var(--radius) 0 var(--radius) var(--radius);
    font-family: var(--sans);
}
.msg-label {
    font-family: var(--mono);
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.msg-label-user { color: var(--accent); }
.msg-label-ai   { color: var(--accent2); }

/* ── Suggestion chips ── */
.chips-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin: 24px 0 8px 0;
}
.chip {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 7px 14px;
    font-size: 13px;
    color: var(--muted);
    cursor: pointer;
    transition: border-color 0.15s, color 0.15s;
    font-family: var(--sans);
}
.chip:hover { border-color: var(--accent); color: var(--text); }

/* ── Input bar ── */
[data-testid="stChatInput"] {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--text) !important;
    font-family: var(--sans) !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(124,106,247,0.12) !important;
}

/* ── Streamlit widget overrides ── */
.stTextInput input, .stSelectbox div[data-baseweb="select"] {
    background: var(--surface2) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
    font-family: var(--sans) !important;
}
.stButton > button {
    background: var(--accent) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: var(--mono) !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 10px 20px !important;
    transition: opacity 0.15s !important;
}
.stButton > button:hover { opacity: 0.88 !important; }

/* Expander dark style */
[data-testid="stExpander"] {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}

/* Dataframe dark */
[data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; }

/* Divider */
hr { border-color: var(--border) !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)


# ── Session state defaults ─────────────────────────────────────────────────────
def init_state():
    defaults = {
        "messages": [],
        "db": None,
        "agent": None,
        "db_connected": False,
        "db_label": "",
        "schema_info": {},
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


init_state()


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:20px 0 4px 0'>
      <div style='font-family:var(--mono);font-size:18px;font-weight:500;color:#E2E4EE;letter-spacing:-0.3px'>
        🗄️ SQL Mind
      </div>
      <div style='font-size:12px;color:#6B7190;margin-top:4px'>
        Natural language → SQL
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── API Key ──
    st.markdown('<div class="sidebar-section">Groq API Key</div>', unsafe_allow_html=True)
    api_key = st.text_input(
        "API Key",
        value=os.getenv("GROQ_API_KEY", ""),
        type="password",
        placeholder="gsk_...",
        label_visibility="collapsed",
    )

    # ── Model picker ──
    st.markdown('<div class="sidebar-section">Model</div>', unsafe_allow_html=True)
    model = st.selectbox(
        "Model",
        ["llama-3.1-8b-instant", "llama-3.3-70b-versatile", "openai/gpt-oss-120b"],
        label_visibility="collapsed",
    )

    # ── DB Mode ──
    st.markdown('<div class="sidebar-section">Database</div>', unsafe_allow_html=True)
    db_mode = st.radio(
        "Database type",
        ["SQLite (demo)", "Upload CSV/Excel", "MySQL"],
        label_visibility="collapsed",
    )

    if db_mode == "SQLite (demo)":
        db_path = st.text_input(
            "DB file path",
            value="student.db",
            placeholder="student.db",
        )
        connect_clicked = st.button("Connect", use_container_width=True)

        if connect_clicked:
            if not api_key:
                st.error("Enter a Groq API key first.")
            else:
                try:
                    with st.spinner("Connecting…"):
                        db = get_sqlite_db(db_path)
                        agent = get_agent(db, api_key, model)
                        st.session_state.db = db
                        st.session_state.agent = agent
                        st.session_state.db_connected = True
                        st.session_state.db_label = f"SQLite · {db_path}"
                        st.session_state.schema_info = get_db_info(db)
                    st.success("Connected!")
                except Exception as e:
                    st.error(f"Connection failed: {e}")

    elif db_mode == "Upload CSV/Excel":
        uploaded_file = st.file_uploader(
            "Upload your data",
            type=["csv", "xlsx", "xls"],
            label_visibility="collapsed",
        )
        table_name = st.text_input(
            "Table name",
            value="data",
            placeholder="data",
        )
        connect_clicked = st.button("Connect", use_container_width=True, key="upload_connect")

        if connect_clicked:
            if not api_key:
                st.error("Enter a Groq API key first.")
            elif not uploaded_file:
                st.error("Upload a CSV or Excel file first.")
            else:
                try:
                    with st.spinner("Loading file into database…"):
                        db = build_sqlite_from_file(uploaded_file, db_path="uploaded.db", table_name=table_name)
                        agent = get_agent(db, api_key, model)
                        st.session_state.db = db
                        st.session_state.agent = agent
                        st.session_state.db_connected = True
                        st.session_state.db_label = f"Uploaded · {uploaded_file.name}"
                        st.session_state.schema_info = get_db_info(db)
                    st.success("Connected!")
                except Exception as e:
                    st.error(f"Connection failed: {e}")

    else:  # MySQL
        mysql_host = st.text_input("Host", placeholder="localhost")
        mysql_user = st.text_input("Username", placeholder="root")
        mysql_pass = st.text_input("Password", type="password")
        mysql_db   = st.text_input("Database name", placeholder="school")
        mysql_port = st.number_input("Port", value=3306, step=1)

        connect_clicked = st.button("Connect", use_container_width=True)

        if connect_clicked:
            if not api_key:
                st.error("Enter a Groq API key first.")
            elif not all([mysql_host, mysql_user, mysql_db]):
                st.error("Fill in host, username, and database name.")
            else:
                try:
                    with st.spinner("Connecting…"):
                        db = get_mysql_db(
                            host=mysql_host,
                            user=mysql_user,
                            password=mysql_pass,
                            database=mysql_db,
                            port=int(mysql_port),
                        )
                        agent = get_agent(db, api_key, model)
                        st.session_state.db = db
                        st.session_state.agent = agent
                        st.session_state.db_connected = True
                        st.session_state.db_label = f"MySQL · {mysql_host}/{mysql_db}"
                        st.session_state.schema_info = get_db_info(db)
                    st.success("Connected!")
                except Exception as e:
                    st.error(f"Connection failed: {e}")

    # ── Connection status ──
    st.markdown("---")
    if st.session_state.db_connected:
        st.markdown(
            f'<div class="status-pill status-connected">● Connected — {st.session_state.db_label}</div>',
            unsafe_allow_html=True,
        )

        # Schema explorer
        if st.session_state.schema_info:
            st.markdown('<div class="sidebar-section">Schema</div>', unsafe_allow_html=True)
            for table, info in st.session_state.schema_info.items():
                with st.expander(f"📋 {table}"):
                    st.markdown(
                        f'<div class="schema-card">{info}</div>',
                        unsafe_allow_html=True,
                    )
    else:
        st.markdown(
            '<div class="status-pill status-disconnected">○ Not connected</div>',
            unsafe_allow_html=True,
        )

    # ── Clear chat ──
    st.markdown("---")
    if st.button("Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# ── Main content ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="topbar">
  <div class="topbar-icon">🗄️</div>
  <div>
    <div class="topbar-title">SQL Mind</div>
    <div class="topbar-sub">Ask anything about your database in plain English</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ── Empty state / suggestions ──
SUGGESTIONS = [
    "Show all students with marks above 80",
    "Who scored the highest marks?",
    "How many students are in Data Science?",
    "List students in DEVOPS section A",
    "What is the average marks per class?",
    "Show the top 3 scorers",
]

if not st.session_state.messages:
    if not st.session_state.db_connected:
        st.markdown("""
        <div style='
            text-align:center;
            padding: 60px 20px;
            color: #6B7190;
        '>
            <div style='font-size:48px;margin-bottom:16px'>🗄️</div>
            <div style='font-family:var(--mono);font-size:16px;color:#E2E4EE;margin-bottom:8px'>
                Connect a database to start
            </div>
            <div style='font-size:13px;line-height:1.7'>
                Choose SQLite (demo) or MySQL in the sidebar,<br>
                add your Groq API key, and hit Connect.
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='
            text-align:center;
            padding: 40px 20px 20px 20px;
            color: #6B7190;
        '>
            <div style='font-size:40px;margin-bottom:12px'>💬</div>
            <div style='font-family:var(--mono);font-size:15px;color:#E2E4EE;margin-bottom:6px'>
                Database connected — ask your first question
            </div>
            <div style='font-size:13px'>Try one of these:</div>
        </div>
        """, unsafe_allow_html=True)

        cols = st.columns(3)
        for i, suggestion in enumerate(SUGGESTIONS):
            with cols[i % 3]:
                if st.button(suggestion, key=f"chip_{i}", use_container_width=True):
                    st.session_state.messages.append({
                        "role": "user",
                        "content": suggestion,
                    })
                    st.rerun()


# ── Render chat history ────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="msg-row" style="justify-content:flex-end;flex-direction:row-reverse">
          <div class="msg-avatar msg-avatar-user">👤</div>
          <div>
            <div class="msg-label msg-label-user">You</div>
            <div class="msg-bubble msg-bubble-user">{msg["content"]}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="msg-row">
          <div class="msg-avatar msg-avatar-ai">🤖</div>
          <div>
            <div class="msg-label msg-label-ai">SQL Mind</div>
            <div class="msg-bubble">{msg["content"]}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)


# ── Chat input ─────────────────────────────────────────────────────────────────
user_input = st.chat_input(
    "Ask anything about your database…",
    disabled=not st.session_state.db_connected,
)

if user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.markdown(f"""
    <div class="msg-row" style="justify-content:flex-end;flex-direction:row-reverse">
      <div class="msg-avatar msg-avatar-user">👤</div>
      <div>
        <div class="msg-label msg-label-user">You</div>
        <div class="msg-bubble msg-bubble-user">{user_input}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Run agent
    with st.container():
        with st.expander("🔍 Agent reasoning", expanded=False):
            callback = StreamlitCallbackHandler(st.container(), expand_new_thoughts=True)

        try:
            with st.spinner("Thinking…"):
                response = st.session_state.agent.run(
                    user_input,
                    callbacks=[callback],
                )
        except Exception as e:
            response = f"Something went wrong: {e}"

    # Render AI response
    st.markdown(f"""
    <div class="msg-row">
      <div class="msg-avatar msg-avatar-ai">🤖</div>
      <div>
        <div class="msg-label msg-label-ai">SQL Mind</div>
        <div class="msg-bubble">{response}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.session_state.messages.append({"role": "assistant", "content": response})