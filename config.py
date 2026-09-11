"""
Shared config, data loading, helper functions.
Import bởi app.py và các tab.
"""

import streamlit as st
import pandas as pd

# =============================================================================
# CONFIG
# =============================================================================

DATA_PATH = r"D:\streamlit\database - Copy.xlsx"

PLOTLY_CONFIG = {
    "displayModeBar": True,
    "displaylogo": False,
    "modeBarButtonsToRemove": ["lasso2d", "select2d"],
}

CHART_TEMPLATE = "plotly_white"
COLOR_MAIN = "#00804D"
COLOR_SEQUENCE = ["#00804D", "#FFC62F", "#009960", "#FFD65C", "#006640", "#66CC99"]
FLAG_COLOR_MAP = {"green": "#00804D", "yellow": "#FFC62F", "red": "#CC3333"}


# =============================================================================
# DATA LOADING
# =============================================================================

@st.cache_data
def load_data(path: str):
    ml = pd.read_excel(path, sheet_name="models_list")
    ld = pd.read_excel(path, sheet_name="log_details")
    lqual = pd.read_excel(path, sheet_name="last_qual_validate_results")
    lquan = pd.read_excel(path, sheet_name="last_quan_validate_results")

    for df in [ml, ld, lqual, lquan]:
        df.columns = df.columns.str.strip().str.lower()

    if "val_date" in lqual.columns:
        lqual["val_date"] = pd.to_datetime(lqual["val_date"], errors="coerce")
    if "val_date" in lquan.columns:
        lquan["val_date"] = pd.to_datetime(lquan["val_date"], errors="coerce")

    def quarter_to_date(q):
        if pd.isna(q) or not isinstance(q, str):
            return pd.NaT
        try:
            parts = q.strip().split("/")
            quarter = int(parts[0].replace("Q", "").replace("q", ""))
            year = int(parts[1])
            month = quarter * 3
            last_day = {3: 31, 6: 30, 9: 30, 12: 31}
            return pd.Timestamp(year, month, last_day[month])
        except Exception:
            return pd.NaT

    if "schedule_date" in ld.columns:
        ld["schedule_dt"] = ld["schedule_date"].apply(quarter_to_date)
    if "actual_date" in ld.columns:
        ld["actual_dt"] = ld["actual_date"].apply(quarter_to_date)

    for col in ["status", "type", "flag_owner", "dev_department"]:
        if col in ml.columns:
            ml[col] = ml[col].astype(str).str.strip().str.lower()

    for col in ["stage", "status"]:
        if col in ld.columns:
            ld[col] = ld[col].astype(str).str.strip().str.lower()

    if "flag" in lqual.columns:
        lqual["flag"] = lqual["flag"].astype(str).str.strip().str.lower()
    if "flag" in lquan.columns:
        lquan["flag"] = lquan["flag"].astype(str).str.strip().str.lower()
    if "fix_status" in lqual.columns:
        lqual["fix_status"] = lqual["fix_status"].astype(str).str.strip().str.lower()

    return ml, ld, lqual, lquan


# =============================================================================
# HELPERS
# =============================================================================

def clean_layout(fig, height=350):
    bg_color = "#f5f0e8"
    font_color = "#1a1a1a"
    grid_color = "rgba(0,0,0,0.06)"

    fig.update_layout(
        template=CHART_TEMPLATE,
        height=height,
        margin=dict(l=20, r=20, t=45, b=20),
        font=dict(family="Segoe UI, sans-serif", size=12, color=font_color),
        hoverlabel=dict(bgcolor="white", font_size=13, font_family="Segoe UI", font_color="#1a1a1a"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5,
                    font=dict(color=font_color)),
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
    )
    fig.update_xaxes(gridcolor=grid_color, linecolor=grid_color)
    fig.update_yaxes(gridcolor=grid_color, linecolor=grid_color)
    fig.update_traces(
        textfont=dict(color=font_color),
        insidetextfont=dict(color="white"),
        outsidetextfont=dict(color=font_color),
        selector=dict(type="pie"),
    )
    return fig


def color_flag(val):
    colors = {
        "green": "background-color: #00804D; color: white; font-weight: 600",
        "yellow": "background-color: #FFC62F; color: #1a1a1a; font-weight: 600",
        "red": "background-color: #CC3333; color: white; font-weight: 600",
    }
    return colors.get(str(val).strip().lower(), "")


def color_fix(val):
    colors = {
        "fixed": "background-color: #00804D; color: white; font-weight: 600",
        "in progress": "background-color: #FFC62F; color: #1a1a1a; font-weight: 600",
        "not started": "background-color: #CC3333; color: white; font-weight: 600",
    }
    return colors.get(str(val).strip().lower(), "")