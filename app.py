import streamlit as st

st.set_page_config(
    page_title="AgriSync Agent",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #f0f7ee; }
[data-testid="stSidebar"] { background: #1a3a2a; }
[data-testid="stSidebar"] * { color: white !important; }
.metric-card {
    background: white; border-radius: 12px; padding: 20px;
    box-shadow: 0 2px 8px rgba(0,100,0,0.12); text-align: center;
}
.chat-user {
    background: #2e7d32; color: white;
    border-radius: 18px 18px 4px 18px;
    padding: 12px 16px; margin: 8px 0;
    max-width: 80%; margin-left: auto;
}
.chat-agent {
    background: white; border-left: 4px solid #2e7d32;
    border-radius: 4px 18px 18px 18px;
    padding: 12px 16px; margin: 8px 0; max-width: 88%;
}
.tool-badge {
    background: #e8f5e9; border: 1px solid #4caf50;
    border-radius: 20px; padding: 3px 12px;
    font-size: 0.8em; color: #2e7d32;
    display: inline-block; margin: 2px;
}
h1, h2, h3 { color: #1a3a2a !important; }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_mcp():
    import mcp_client
    return mcp_client


@st.cache_resource
def load_bq():
    import bigquery_helper
    return bigquery_helper


if "messages"   not in st.session_state: st.session_state.messages   = []
if "agent"      not in st.session_state: st.session_state.agent      = None
if "connectors" not in st.session_state: st.session_state.connectors = []

# ── Sidebar ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌾 AgriSync Agent")
    st.markdown("*AI Farm Co-Pilot for Nigerian Farmers*")
    st.divider()
    st.markdown("### System Status")

    try:
        from config import config
        config.validate()
        st.success("✅ Config loaded")
    except Exception as e:
        st.error(f"❌ Config: {e}")

    mcp = load_mcp()
    try:
        groups = mcp.list_groups()
        if "error" not in groups:
            st.success("✅ Fivetran connected")
        else:
            st.warning(f"⚠️ Fivetran: {groups['error'][:50]}")
    except Exception as e:
        st.error(f"❌ Fivetran: {str(e)[:50]}")

    bq = load_bq()
    try:
        sample = bq.get_crop_summary()
        if sample and "error" not in sample[0]:
            st.success("✅ BigQuery connected")
        else:
            st.warning("⚠️ BigQuery: no data yet")
    except Exception as e:
        st.warning(f"⚠️ BigQuery: {str(e)[:50]}")

    st.divider()
    st.markdown("### 🔧 MCP Tools")
    if st.button("🔍 Discover MCP Tools", use_container_width=True):
        for t in mcp.list_mcp_tools():
            st.markdown(
                f'<span class="tool-badge">⚡ {t["name"]}</span>',
                unsafe_allow_html=True
            )

    st.divider()
    st.markdown("### ⚡ Quick Actions")

    if st.button("📋 List Connectors", use_container_width=True):
        with st.spinner("Fetching connectors..."):
            result = mcp.list_connectors()
            items  = result.get("data", {}).get("items", [])
            st.session_state.connectors = items
            st.success(f"Found {len(items)} connector(s)")

    if st.button("🗄️ Setup Demo Data", use_container_width=True):
        with st.spinner("Inserting demo farm data..."):
            result = bq.setup_demo_tables()
            if result.get("status") == "ok":
                st.success(f"✅ {result.get('message', 'Demo data setup complete!')}")
            else:
                st.error(f"Error: {result.get('message', result)}")

    if st.button("🔄 Reset Chat", use_container_width=True):
        st.session_state.messages = []
        if st.session_state.agent:
            st.session_state.agent.reset()
        st.rerun()

    if st.session_state.connectors:
        st.divider()
        st.markdown("### 📡 Live Connectors")
        for c in st.session_state.connectors:
            name   = c.get("schema", c.get("id", "unknown"))
            paused = c.get("paused", False)
            icon   = "⏸️" if paused else "🟢"
            svc    = c.get("service", "")
            st.markdown(f"{icon} **{name}** `{svc}`")

    st.divider()
    st.caption("Gemini 2.0 Flash + Fivetran MCP\nGoogle Cloud Hackathon 2025")

# ── Main ──────────────────────────────────────────────────────────────────
st.markdown("# 🌾 AgriSync Agent")
st.markdown("**AI Farm Co-Pilot for Nigerian Farmers** — Gemini 2.0 Flash + Fivetran MCP + BigQuery")
st.divider()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(
        '<div class="metric-card"><h2>8</h2><p>Farms Tracked</p></div>',
        unsafe_allow_html=True)
with col2:
    st.markdown(
        '<div class="metric-card"><h2>3</h2><p>Nigerian States</p></div>',
        unsafe_allow_html=True)
with col3:
    n = len(st.session_state.connectors)
    st.markdown(
        f'<div class="metric-card"><h2>{n}</h2><p>Connectors</p></div>',
        unsafe_allow_html=True)
with col4:
    st.markdown(
        '<div class="metric-card"><h2>🟢</h2><p>System Live</p></div>',
        unsafe_allow_html=True)

st.divider()
st.markdown("### 💬 Chat with AgriSync")

cols = st.columns(3)
starters = [
    ("📡 Check pipelines", "List all my Fivetran connectors and their sync status"),
    ("🌽 Crop yields",     "What are the average crop yields across all farms?"),
    ("🗺️ Kano region",    "Show me agricultural data for Kano state farmers"),
]
for i, (label, prompt) in enumerate(starters):
    if cols[i].button(label, use_container_width=True):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()

st.divider()


def render_tool_calls(tool_calls):
    for tc in tool_calls:
        with st.expander(f"🔧 Tool: `{tc.get('tool', 'unknown')}`"):
            if tc.get("args"):
                st.markdown("**Input:**")
                st.json(tc["args"])
            st.markdown("**Result:**")
            st.json(tc.get("result", {}))


for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(
            f'<div class="chat-user">👤 {msg["content"]}</div>',
            unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="chat-agent">🌾 {msg["content"]}</div>',
            unsafe_allow_html=True)
        if msg.get("tool_calls"):
            render_tool_calls(msg["tool_calls"])


user_input = st.chat_input("Ask about your farms, pipelines, or crop data...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    if st.session_state.agent is None:
        with st.spinner("Loading AgriSync Agent..."):
            from agent import AgriSyncAgent
            st.session_state.agent = AgriSyncAgent()

    with st.spinner("🌾 AgriSync is thinking..."):
        result = st.session_state.agent.chat(user_input)

    st.session_state.messages.append({
        "role":       "assistant",
        "content":    result.get("response", "No response."),
        "tool_calls": result.get("tool_calls", []),
    })
    st.rerun()