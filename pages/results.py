import streamlit as st
import pandas as pd
import gspread
import json
from google.oauth2.service_account import Credentials
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(
    page_title="Sheets Dashboard",
    page_icon="📊",
    layout="wide",
)

# ---------------------------
# Custom CSS
# ---------------------------
st.markdown("""
<style>
    /* Hide default streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* App background */
    .stApp {
        background-color: #F8F9FB;
    }

    /* Metric cards */
    [data-testid="metric-container"] {
        background: #FFFFFF;
        border: 1px solid #EAECF0;
        border-radius: 12px;
        padding: 20px 24px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    [data-testid="metric-container"]:hover {
        border-color: #D0D5DD;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
        transition: all 0.2s ease;
    }
    [data-testid="stMetricLabel"] {
        font-size: 13px !important;
        font-weight: 500 !important;
        color: #667085 !important;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    [data-testid="stMetricValue"] {
        font-size: 28px !important;
        font-weight: 700 !important;
        color: #101828 !important;
    }
    [data-testid="stMetricDelta"] {
        font-size: 13px !important;
        font-weight: 500 !important;
    }

    /* Section headers */
    .section-header {
        font-size: 11px;
        font-weight: 600;
        color: #98A2B3;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin: 28px 0 12px;
        padding-bottom: 8px;
        border-bottom: 1px solid #EAECF0;
    }

    /* Record cards */
    .record-card {
        background: #FFFFFF;
        border: 1px solid #EAECF0;
        border-radius: 12px;
        padding: 16px 18px;
        margin-bottom: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        transition: all 0.15s ease;
    }
    .record-card:hover {
        border-color: #D0D5DD;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        transform: translateY(-1px);
    }
    .record-card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 10px;
    }
    .record-name {
        font-size: 15px;
        font-weight: 600;
        color: #101828;
    }
    .record-category {
        font-size: 12px;
        color: #667085;
        margin-top: 1px;
    }
    .record-amount {
        font-size: 18px;
        font-weight: 700;
        color: #101828;
        text-align: right;
    }
    .record-divider {
        height: 1px;
        background: #F2F4F7;
        margin: 10px 0;
    }
    .record-meta {
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .record-date {
        font-size: 12px;
        color: #98A2B3;
    }

    /* Status pills */
    .pill {
        display: inline-block;
        font-size: 11px;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 99px;
    }
    .pill-completed { background: #ECFDF3; color: #027A48; }
    .pill-pending   { background: #FFFAEB; color: #B54708; }
    .pill-cancelled { background: #FEF3F2; color: #B42318; }
    .pill-default   { background: #F2F4F7; color: #344054; }

    /* Avatar circle */
    .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 13px;
        font-weight: 700;
        flex-shrink: 0;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #FFFFFF;
        border-right: 1px solid #EAECF0;
    }

    /* Dataframe */
    [data-testid="stDataFrame"] {
        border: 1px solid #EAECF0;
        border-radius: 12px;
        overflow: hidden;
    }

    /* Download button */
    .stDownloadButton > button {
        background: #101828;
        color: #FFFFFF;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        font-size: 13px;
        padding: 10px 20px;
        width: 100%;
        transition: background 0.15s ease;
    }
    .stDownloadButton > button:hover {
        background: #1D2939;
    }

    /* Upload area styling */
    [data-testid="stFileUploader"] {
        background: #FFFFFF;
        border: 1px dashed #D0D5DD;
        border-radius: 12px;
        padding: 12px;
    }

    /* Plotly charts */
    .js-plotly-plot {
        border-radius: 12px;
    }

    /* Top bar */
    .top-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 0 20px;
        border-bottom: 1px solid #EAECF0;
        margin-bottom: 24px;
    }
    .top-bar-title {
        font-size: 22px;
        font-weight: 700;
        color: #101828;
    }
    .top-bar-sub {
        font-size: 13px;
        color: #667085;
        margin-top: 2px;
    }
    .live-badge {
        background: #ECFDF3;
        color: #027A48;
        font-size: 12px;
        font-weight: 600;
        padding: 4px 12px;
        border-radius: 99px;
        border: 1px solid #ABEFC6;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------
# Helper: status pill HTML
# ---------------------------
def status_pill(status: str) -> str:
    s = str(status).lower()
    if s == "completed":
        cls = "pill-completed"
    elif s == "pending":
        cls = "pill-pending"
    elif s == "cancelled" or s == "canceled":
        cls = "pill-cancelled"
    else:
        cls = "pill-default"
    return f'<span class="pill {cls}">{status}</span>'


# ---------------------------
# Helper: avatar HTML
# ---------------------------
AVATAR_COLORS = [
    ("#EEF4FF", "#3538CD"), ("#FDF2FA", "#C11574"),
    ("#F0FDF9", "#107569"), ("#FFFAEB", "#B54708"),
    ("#EFF8FF", "#1849A9"), ("#FEF3F2", "#B42318"),
]

def avatar_html(name: str, idx: int) -> str:
    bg, fg = AVATAR_COLORS[idx % len(AVATAR_COLORS)]
    initials = "".join(w[0].upper() for w in str(name).split()[:2]) or "?"
    return (
        f'<div class="avatar" style="background:{bg};color:{fg};">'
        f"{initials}</div>"
    )


# ---------------------------
# Helper: record card HTML
# ---------------------------
def record_card_html(row: dict, idx: int) -> str:
    name = row.get("Name", f"Record {idx+1}")
    category = row.get("Category", "")
    amount = row.get("Amount", "")
    date = row.get("Date", "")
    status = row.get("Status", "")

    amount_str = f"${float(amount):,.2f}" if amount != "" else "—"
    pill = status_pill(status) if status else ""
    av = avatar_html(name, idx)

    other_fields = {
        k: v for k, v in row.items()
        if k not in ("Name", "Category", "Amount", "Date", "Status")
    }
    extras = "".join(
        f'<div style="display:flex;justify-content:space-between;font-size:12px;color:#667085;margin-top:4px;">'
        f'<span>{k}</span><span style="color:#344054;font-weight:500;">{v}</span></div>'
        for k, v in list(other_fields.items())[:3]
    )

    return f"""
<div class="record-card">
  <div class="record-card-header">
    <div style="display:flex;align-items:center;gap:10px;">
      {av}
      <div>
        <div class="record-name">{name}</div>
        <div class="record-category">{category}</div>
      </div>
    </div>
    <div>
      <div class="record-amount">{amount_str}</div>
    </div>
  </div>
  <div class="record-divider"></div>
  <div class="record-meta">
    <div class="record-date">{date}</div>
    {pill}
  </div>
  {extras}
</div>
"""


# ---------------------------
# Sidebar
# ---------------------------
with st.sidebar:
    st.markdown("### 🔑 Connect Google Sheet")
    service_file = st.file_uploader("Service Account JSON", type=["json"])

    st.markdown("---")
    st.markdown("### 📌 Filters")

    SHEET_URL = "https://docs.google.com/spreadsheets/d/1gFrgzaV9wA77AfWkhl3bsQk5bjN7NkrB2T1K9idZ3EE/edit#gid=368956829"
    sheet_url_input = st.text_input("Sheet URL", value=SHEET_URL)


# ---------------------------
# Auth + Load Data
# ---------------------------
df = None

if service_file:
    try:
        service_info = json.load(service_file)
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.readonly",
        ]
        creds = Credentials.from_service_account_info(service_info, scopes=scopes)
        gc = gspread.authorize(creds)
        st.sidebar.success("✅ Authenticated")
        sh = gc.open_by_url(sheet_url_input)
        worksheet = sh.get_worksheet(0)
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
    except Exception as e:
        st.sidebar.error(f"Error: {e}")
        df = None

# ---------------------------
# Sidebar filters (once data is loaded)
# ---------------------------
if df is not None:
    with st.sidebar:
        if "Status" in df.columns:
            all_statuses = df["Status"].dropna().unique().tolist()
            status_filter = st.multiselect(
                "Status", all_statuses, default=all_statuses
            )
            df = df[df["Status"].isin(status_filter)]

        if "Category" in df.columns:
            all_cats = df["Category"].dropna().unique().tolist()
            cat_filter = st.multiselect(
                "Category", all_cats, default=all_cats
            )
            df = df[df["Category"].isin(cat_filter)]

        st.markdown("---")
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇ Download CSV", data=csv_bytes,
            file_name="dashboard_data.csv", mime="text/csv"
        )


# ---------------------------
# Main content
# ---------------------------
if df is None:
    # Landing state
    st.markdown("""
    <div style="max-width:520px;margin:80px auto;text-align:center;">
      <div style="font-size:48px;margin-bottom:16px;">📊</div>
      <h2 style="color:#101828;font-weight:700;margin-bottom:8px;">Google Sheets Dashboard</h2>
      <p style="color:#667085;font-size:15px;line-height:1.6;">
        Upload your Google Service Account JSON in the sidebar to connect your spreadsheet
        and explore your data with beautiful cards, charts, and filters.
      </p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ---------------------------
# Top bar
# ---------------------------
col_title, col_badge = st.columns([6, 1])
with col_title:
    st.markdown("""
    <div class="top-bar-title">📊 Live Dashboard</div>
    <div class="top-bar-sub">Connected to Google Sheets · Auto-refreshes on reload</div>
    """, unsafe_allow_html=True)
with col_badge:
    st.markdown('<div style="padding-top:8px;"><span class="live-badge">● Live</span></div>', unsafe_allow_html=True)

st.markdown('<div style="height:20px;"></div>', unsafe_allow_html=True)


# ---------------------------
# Metric Cards
# ---------------------------
st.markdown('<div class="section-header">Overview</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

total_rows = len(df)
with c1:
    st.metric("Total Records", total_rows)

if "Amount" in df.columns:
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
    total_amount = df["Amount"].sum()
    avg_amount = df["Amount"].mean()
    with c2:
        st.metric("Total Amount", f"${total_amount:,.0f}")
    with c4:
        st.metric("Avg Amount", f"${avg_amount:,.0f}")
else:
    with c2:
        st.metric("Total Amount", "N/A")
    with c4:
        st.metric("Avg Amount", "N/A")

if "Status" in df.columns:
    completed_count = df[df["Status"].str.lower() == "completed"].shape[0]
    pct = round(completed_count / total_rows * 100) if total_rows else 0
    with c3:
        st.metric("Completed", completed_count, delta=f"{pct}% of total")
else:
    with c3:
        st.metric("Completed", "N/A")


# ---------------------------
# Charts
# ---------------------------
st.markdown('<div class="section-header">Analytics</div>', unsafe_allow_html=True)

chart_col1, chart_col2 = st.columns([3, 2])

# Bar chart
with chart_col1:
    if "Amount" in df.columns and "Category" in df.columns and "Status" in df.columns:
        fig_bar = px.bar(
            df, x="Category", y="Amount", color="Status",
            barmode="group",
            color_discrete_map={
                "Completed": "#17B26A",
                "Pending":   "#F79009",
                "Cancelled": "#F04438",
            },
            template="plotly_white",
        )
        fig_bar.update_layout(
            title=dict(text="Amount by Category & Status", font=dict(size=14, color="#101828"), x=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=12)),
            margin=dict(l=0, r=0, t=40, b=0),
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(family="sans-serif", color="#667085"),
            bargap=0.25,
            bargroupgap=0.1,
            xaxis=dict(showgrid=False, linecolor="#EAECF0"),
            yaxis=dict(gridcolor="#F2F4F7", linecolor="#EAECF0"),
        )
        fig_bar.update_traces(marker_line_width=0)
        st.plotly_chart(fig_bar, use_container_width=True)

# Donut chart
with chart_col2:
    if "Status" in df.columns:
        status_counts = df["Status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        fig_pie = px.pie(
            status_counts, names="Status", values="Count",
            hole=0.6,
            color="Status",
            color_discrete_map={
                "Completed": "#17B26A",
                "Pending":   "#F79009",
                "Cancelled": "#F04438",
            },
            template="plotly_white",
        )
        fig_pie.update_traces(
            textposition="outside",
            textinfo="label+percent",
            textfont_size=12,
            marker=dict(line=dict(color="#FFFFFF", width=2)),
        )
        fig_pie.update_layout(
            title=dict(text="Status Breakdown", font=dict(size=14, color="#101828"), x=0),
            showlegend=False,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor="white",
        )
        st.plotly_chart(fig_pie, use_container_width=True)

# Line chart
if "Amount" in df.columns and "Date" in df.columns:
    df_copy = df.copy()
    df_copy["Date"] = pd.to_datetime(df_copy["Date"], errors="coerce")
    df_date = df_copy.dropna(subset=["Date"]).groupby("Date")["Amount"].sum().reset_index()
    if not df_date.empty:
        fig_line = px.line(
            df_date, x="Date", y="Amount",
            template="plotly_white",
            color_discrete_sequence=["#2E90FA"],
        )
        fig_line.update_traces(line=dict(width=2.5), mode="lines+markers", marker=dict(size=5))
        fig_line.update_layout(
            title=dict(text="Amount Over Time", font=dict(size=14, color="#101828"), x=0),
            margin=dict(l=0, r=0, t=40, b=0),
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(family="sans-serif", color="#667085"),
            xaxis=dict(showgrid=False, linecolor="#EAECF0"),
            yaxis=dict(gridcolor="#F2F4F7", linecolor="#EAECF0"),
        )
        st.plotly_chart(fig_line, use_container_width=True)


# ---------------------------
# Record Cards
# ---------------------------
st.markdown('<div class="section-header">Records</div>', unsafe_allow_html=True)

records = df.to_dict("records")
cols_per_row = 3
for i in range(0, len(records), cols_per_row):
    row_slice = records[i: i + cols_per_row]
    cols = st.columns(cols_per_row)
    for j, (col, record) in enumerate(zip(cols, row_slice)):
        with col:
            st.markdown(record_card_html(record, i + j), unsafe_allow_html=True)


# ---------------------------
# Full Data Table
# ---------------------------
st.markdown('<div class="section-header">Data Table</div>', unsafe_allow_html=True)
st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
    height=min(400, 80 + len(df) * 35),
)
