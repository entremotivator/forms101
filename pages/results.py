import streamlit as st
import pandas as pd
import gspread
import json
from google.oauth2.service_account import Credentials
import plotly.express as px
import plotly.graph_objects as go

# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Sheets Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Syne:wght@700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0F1117;
    color: #E8E8E8;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #161B27 !important;
    border-right: 1px solid #1E2535;
}
section[data-testid="stSidebar"] * {
    color: #C0C8D8 !important;
}
section[data-testid="stSidebar"] .stFileUploader label {
    color: #8899AA !important;
}

/* Main background */
.main .block-container {
    background: #0F1117;
    padding: 2rem 3rem !important;
}

/* Metric cards */
div[data-testid="metric-container"] {
    background: #161B27;
    border: 1px solid #1E2535;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
}
div[data-testid="metric-container"] label {
    color: #6B7A99 !important;
    font-size: 0.75rem !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
div[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #FFFFFF !important;
    font-size: 1.8rem !important;
    font-weight: 600;
}
div[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-size: 0.8rem !important;
}

/* Dataframe */
.dataframe-container {
    border: 1px solid #1E2535;
    border-radius: 12px;
    overflow: hidden;
}

/* Download button */
.stDownloadButton button {
    background: #2563EB !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    padding: 0.6rem 1.5rem !important;
    transition: background 0.2s;
}
.stDownloadButton button:hover {
    background: #1D4ED8 !important;
}

/* Section headers */
h2 {
    font-family: 'Syne', sans-serif !important;
    font-size: 1.1rem !important;
    color: #FFFFFF !important;
    letter-spacing: 0.03em;
    margin-top: 2rem !important;
    margin-bottom: 1rem !important;
}
h1 {
    font-family: 'Syne', sans-serif !important;
    color: #FFFFFF !important;
    font-size: 1.8rem !important;
}

/* Divider */
hr {
    border-color: #1E2535 !important;
}

/* Multiselect */
.stMultiSelect [data-baseweb="tag"] {
    background: #1E3A5F !important;
    color: #93C5FD !important;
}

/* Upload area */
.stFileUploader [data-testid="stFileUploadDropzone"] {
    background: #161B27 !important;
    border: 1.5px dashed #2D3A50 !important;
    border-radius: 10px !important;
}

/* Info box */
.stInfo {
    background: #0C1A2E !important;
    border-left: 4px solid #2563EB !important;
    color: #93C5FD !important;
    border-radius: 8px !important;
}

/* Success */
.stSuccess {
    background: #0A1F14 !important;
    border-left: 4px solid #22C55E !important;
    border-radius: 8px !important;
}

/* Table styling */
.stDataFrame {
    border-radius: 12px !important;
    overflow: hidden;
}

/* Plotly charts */
.js-plotly-plot {
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📡 Data Source")
    service_file = st.file_uploader("Upload Service Account JSON", type=["json"])
    st.markdown("---")
    st.markdown(
        "<small style='color:#4B5A72;'>Connect your Google Service Account to pull live Sheets data.</small>",
        unsafe_allow_html=True
    )

SHEET_URL = "https://docs.google.com/spreadsheets/d/1gFrgzaV9wA77AfWkhl3bsQk5bjN7NkrB2T1K9idZ3EE/edit#gid=368956829"

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#161B27",
    font=dict(family="Inter", color="#C0C8D8", size=12),
    margin=dict(l=0, r=0, t=30, b=0),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#C0C8D8")),
    xaxis=dict(gridcolor="#1E2535", linecolor="#1E2535", tickfont=dict(color="#6B7A99")),
    yaxis=dict(gridcolor="#1E2535", linecolor="#1E2535", tickfont=dict(color="#6B7A99")),
)

COLORS = ["#3B82F6", "#22C55E", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899", "#14B8A6"]

# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
st.title("Live Sheets Dashboard")

if not service_file:
    st.info("Upload a Google Service Account JSON in the sidebar to load your data.")
    st.stop()

# ── AUTH ──────────────────────────────────
try:
    service_info = json.load(service_file)
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.readonly"
    ]
    creds = Credentials.from_service_account_info(service_info, scopes=scopes)
    gc = gspread.authorize(creds)
except Exception as e:
    st.error(f"Authentication failed: {e}")
    st.stop()

# ── LOAD DATA ─────────────────────────────
try:
    sh = gc.open_by_url(SHEET_URL)
    worksheet = sh.get_worksheet(0)
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    st.sidebar.success("Connected")
except Exception as e:
    st.error(f"Could not load sheet: {e}")
    st.stop()

if df.empty:
    st.warning("Sheet is empty or has no records.")
    st.stop()

# ── SIDEBAR FILTERS ───────────────────────
with st.sidebar:
    st.markdown("### Filters")
    if "Status" in df.columns:
        status_opts = df["Status"].dropna().unique().tolist()
        status_filter = st.multiselect("Status", status_opts, default=status_opts)
        df = df[df["Status"].isin(status_filter)]

    if "Category" in df.columns:
        cat_opts = df["Category"].dropna().unique().tolist()
        cat_filter = st.multiselect("Category", cat_opts, default=cat_opts)
        df = df[df["Category"].isin(cat_filter)]

# ── KPI CARDS ─────────────────────────────
st.markdown("## Overview")
cols = st.columns(4)

with cols[0]:
    st.metric("Total Records", f"{len(df):,}")

with cols[1]:
    if "Amount" in df.columns:
        total = pd.to_numeric(df["Amount"], errors="coerce").sum()
        st.metric("Total Amount", f"${total:,.2f}")
    else:
        st.metric("Columns", len(df.columns))

with cols[2]:
    if "Status" in df.columns:
        completed = df[df["Status"].str.lower() == "completed"].shape[0]
        pct = (completed / len(df) * 100) if len(df) > 0 else 0
        st.metric("Completed", f"{completed}", delta=f"{pct:.1f}% of total")
    else:
        st.metric("Rows", len(df))

with cols[3]:
    if "Amount" in df.columns:
        avg = pd.to_numeric(df["Amount"], errors="coerce").mean()
        st.metric("Avg Amount", f"${avg:,.2f}")
    else:
        st.metric("Data Source", "Google Sheets")

# ── CHARTS ────────────────────────────────
has_amount = "Amount" in df.columns
has_category = "Category" in df.columns
has_status = "Status" in df.columns
has_date = "Date" in df.columns

if has_amount or has_category or has_status:
    st.markdown("## Insights")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    if has_amount and has_category:
        df["Amount_num"] = pd.to_numeric(df["Amount"], errors="coerce")
        grouped = df.groupby("Category")["Amount_num"].sum().reset_index()
        fig = px.bar(
            grouped, x="Category", y="Amount_num",
            color="Category", color_discrete_sequence=COLORS,
            title="Amount by Category",
        )
        fig.update_layout(**PLOTLY_LAYOUT, showlegend=False)
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(fig, use_container_width=True)

    elif has_status:
        status_counts = df["Status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        fig = px.pie(
            status_counts, values="Count", names="Status",
            color_discrete_sequence=COLORS,
            title="Status Distribution",
            hole=0.55
        )
        fig.update_layout(**PLOTLY_LAYOUT)
        st.plotly_chart(fig, use_container_width=True)

with chart_col2:
    if has_amount and has_date:
        df_time = df.copy()
        df_time["Date"] = pd.to_datetime(df_time["Date"], errors="coerce")
        df_time = df_time.dropna(subset=["Date"])
        df_time["Amount_num"] = pd.to_numeric(df_time["Amount"], errors="coerce")
        df_agg = df_time.groupby("Date")["Amount_num"].sum().reset_index()
        fig2 = px.area(
            df_agg, x="Date", y="Amount_num",
            title="Amount Over Time",
            color_discrete_sequence=["#3B82F6"]
        )
        fig2.update_traces(line_color="#3B82F6", fillcolor="rgba(59,130,246,0.15)")
        fig2.update_layout(**PLOTLY_LAYOUT)
        st.plotly_chart(fig2, use_container_width=True)

    elif has_amount and has_status:
        df["Amount_num"] = pd.to_numeric(df["Amount"], errors="coerce")
        fig2 = px.box(
            df, x="Status", y="Amount_num",
            color="Status", color_discrete_sequence=COLORS,
            title="Amount Distribution by Status"
        )
        fig2.update_layout(**PLOTLY_LAYOUT, showlegend=False)
        st.plotly_chart(fig2, use_container_width=True)

# ── FULL TABLE ────────────────────────────
st.markdown("## Records")

search = st.text_input("Search records", placeholder="Type to filter any column...")
display_df = df.copy()
if search:
    mask = display_df.apply(
        lambda col: col.astype(str).str.contains(search, case=False, na=False)
    ).any(axis=1)
    display_df = display_df[mask]

st.caption(f"Showing {len(display_df):,} of {len(df):,} records")
st.dataframe(display_df, use_container_width=True, height=420)

# ── DOWNLOAD ──────────────────────────────
st.markdown("## Export")
csv = display_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download CSV",
    data=csv,
    file_name="dashboard_export.csv",
    mime="text/csv"
)
