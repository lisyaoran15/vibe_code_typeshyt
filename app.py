"""
Model Risk Management Dashboard — BIDV Theme
"""

import streamlit as st
import base64, os
from config import DATA_PATH, load_data

st.set_page_config(page_title="BIDV Model Risk Management", layout="wide", page_icon="📊")

# ── BIDV CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    :root {
        --bidv-green: #00804D;
        --bidv-green-light: #33996E;
        --bidv-yellow: #FFC62F;
        --bg: #ede4d4;
        --bg-alt: #e2d8c6;
        --text: #1a1a1a;
        --text-muted: #555;
        --border: #cfc5b3;
    }

    /* Nền — ép tất cả */
    html, body, .stApp, .main, .block-container,
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewBlockContainer"],
    [data-testid="stMainBlockContainer"],
    [data-testid="stVerticalBlock"],
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stBottomBlockContainer"],
    [data-testid="stMain"],
    .appview-container, .main .block-container,
    div.stTabs, div[data-testid="stTabs"],
    div[data-testid="stTabContent"],
    div.element-container,
    div[data-testid="column"],
    .stMarkdown, .stAlert,
    div[data-testid="stExpander"],
    div[data-testid="stExpanderDetails"] {
        background-color: var(--bg) !important;
    }
    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] > div,
    section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        background-color: var(--bg-alt) !important;
    }

    /* Text toàn bộ đen */
    .stApp *, h1, h2, h3, h4, h5, h6, p, span, label, div, li, td, th,
    button[data-baseweb="tab"], [data-testid="stExpanderToggleDetails"] p,
    .stCaption * { color: var(--text) !important; }

    /* Logo header */
    .bidv-header {
        display: flex; align-items: center; gap: 15px;
        padding: 10px 0 5px 0;
    }
    .bidv-header img { height: 45px; }
    .bidv-header h1 { margin: 0; font-size: 1.6rem; color: var(--bidv-green) !important; }

    /* Metric cards */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, var(--bidv-green) 0%, var(--bidv-green-light) 100%) !important;
        padding: 15px 20px; border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,128,77,0.15);
    }
    div[data-testid="stMetric"] *, div[data-testid="stMetric"] label,
    div[data-testid="stMetric"] div[data-testid="stMetricValue"],
    div[data-testid="stMetric"] div[data-testid="stMetricDelta"] { color: white !important; }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        font-size: 1.8rem !important; font-weight: 700 !important;
    }

    /* Active tab = BIDV green */
    button[data-baseweb="tab"] { font-size: 1rem !important; font-weight: 600 !important; }
    button[data-baseweb="tab"][aria-selected="true"] {
        border-bottom-color: var(--bidv-green) !important;
        color: var(--bidv-green) !important;
    }

    /* DataFrames — nền sáng, text đen */
    [data-testid="stDataFrame"] iframe { background-color: var(--bg) !important; }
    .stDataFrame { border-radius: 8px; overflow: hidden; }

    /* Inputs */
    .stTextInput input, [data-baseweb="select"] > div, [data-baseweb="input"] > div {
        background-color: white !important;
        color: var(--text) !important;
        border-color: var(--border) !important;
    }

    /* Plotly text */
    .js-plotly-plot .plotly .gtitle, .js-plotly-plot .plotly .xtitle,
    .js-plotly-plot .plotly .ytitle { fill: var(--text) !important; }
    .js-plotly-plot .plotly .xtick text,
    .js-plotly-plot .plotly .ytick text { fill: var(--text) !important; }
    .js-plotly-plot .plotly .legendtext { fill: var(--text) !important; }

    /* Misc */
    hr { border-color: var(--border) !important; }
    [data-testid="stExpanderToggleDetails"] svg { color: var(--text) !important; }
    div[data-testid="stExpander"], div[data-testid="stExpanderDetails"] {
        background-color: var(--bg) !important;
    }
    .stAlert > div { background-color: var(--bg-alt) !important; color: var(--text) !important; }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────
logo_path = r"D:\streamlit\BIDV-logo-pay2s.png"
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        logo_b64 = base64.b64encode(f.read()).decode()
    st.markdown(f"""
    <div class="bidv-header">
        <img src="data:image/png;base64,{logo_b64}" alt="BIDV">
        <h1>Model Risk Management Dashboard</h1>
    </div>
    """, unsafe_allow_html=True)
else:
    st.title("📊 Model Risk Management Dashboard")

# ── Load data ─────────────────────────────────────────────────────────────
try:
    models_list, log_details, last_qual, last_quan = load_data(DATA_PATH)
except FileNotFoundError:
    st.error(f"❌ Không tìm thấy file: `{DATA_PATH}`")
    st.stop()
except Exception as e:
    st.error(f"❌ Lỗi đọc file: {e}")
    st.stop()

# ── Tabs ──────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(
    ["📋 Dashboard", "🔎 Chi tiết mô hình", "📚 Thư viện tài liệu"]
)

from tabs import tab_dashboard, tab_model_detail, tab_knowledge

with tab1:
    tab_dashboard.render(models_list, log_details, last_qual, last_quan)

with tab2:
    tab_model_detail.render(models_list, last_qual, last_quan)

with tab3:
    tab_knowledge.render()