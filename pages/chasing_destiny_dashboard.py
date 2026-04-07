import streamlit as st
import pandas as pd
import gspread
import json
from google.oauth2.service_account import Credentials
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(
    page_title="Chasing Destiny Studios | Production Dashboard",
    layout="wide",
    page_icon="🎬"
)

# -------------------------
# CUSTOM CSS — Cinematic Dark Gold
# -------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Montserrat:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Montserrat', sans-serif;
    background-color: #0a0a0a;
    color: #f0ead6;
}
.stApp { background: #0d0c0a; }
h1, h2, h3 {
    font-family: 'Playfair Display', serif !important;
    color: #d4a843 !important;
}
.stSidebar { background-color: #0f0e0b !important; border-right: 1px solid #2a2018; }
.stSidebar .stMarkdown { color: #c8bea0 !important; }
.metric-card {
    background: linear-gradient(145deg, #181410, #1f1a0f);
    border: 1px solid #3a2e1a;
    border-radius: 6px;
    padding: 20px;
    text-align: center;
    transition: border-color 0.3s;
}
.metric-card:hover { border-color: #d4a843; }
.metric-label { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.18em; color: #8a7a5a; margin-bottom: 6px; }
.metric-value { font-family: 'Playfair Display', serif; font-size: 2.2rem; color: #d4a843; font-weight: 700; }
.metric-sub { font-size: 0.78rem; color: #6a5e42; margin-top: 4px; }
.studio-header {
    text-align: center;
    padding: 1.5rem 0 0.5rem 0;
    border-bottom: 1px solid #2a2018;
    margin-bottom: 1.5rem;
}
.section-label {
    font-size: 0.7rem; letter-spacing: 0.25em; text-transform: uppercase;
    color: #8a7a5a; border-bottom: 1px solid #2a2018; padding-bottom: 6px; margin-bottom: 12px;
}
.project-card {
    background: #111008;
    border: 1px solid #2a2018;
    border-left: 3px solid #d4a843;
    border-radius: 4px;
    padding: 14px 16px;
    margin-bottom: 10px;
}
.project-title { font-family: 'Playfair Display', serif; font-size: 1rem; color: #d4a843; }
.project-meta { font-size: 0.78rem; color: #8a7a5a; margin-top: 4px; }
.badge {
    display: inline-block; font-size: 0.68rem; padding: 2px 8px; border-radius: 2px;
    font-weight: 600; letter-spacing: 0.05em; margin-right: 4px;
}
.badge-feature { background: #1a2e1a; color: #6abf6a; border: 1px solid #2a4a2a; }
.badge-short { background: #1a1a2e; color: #6a8abf; border: 1px solid #2a2a4a; }
.badge-doc { background: #2e2a1a; color: #bfa06a; border: 1px solid #4a3a1a; }
.badge-tv { background: #2e1a2e; color: #bf6abf; border: 1px solid #4a1a4a; }
.badge-other { background: #1e1e1e; color: #888; border: 1px solid #333; }
</style>
""", unsafe_allow_html=True)

# -------------------------
# SIDEBAR AUTH
# -------------------------
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 1rem 0 0.5rem 0;'>
        <div style='font-size:1.8rem;'>🎬</div>
        <div style='font-family: Georgia, serif; font-size:1rem; color:#d4a843; letter-spacing:0.06em;'>Chasing Destiny Studios</div>
        <div style='font-size:0.65rem; color:#5a4e38; letter-spacing:0.2em; text-transform:uppercase; margin-top:2px;'>Production Dashboard</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("#### 🔑 Google Service Account")
    service_file = st.file_uploader("Upload JSON Key", type=["json"])

    if service_file:
        st.markdown("---")
        st.markdown("#### 🎛️ Filters")

# -------------------------
# MAIN CONTENT
# -------------------------
st.markdown("""
<div class='studio-header'>
    <h1 style='font-size:2.4rem; margin-bottom:0.2rem;'>🎬 Chasing Destiny Studios</h1>
    <p style='font-size:0.72rem; letter-spacing:0.28em; color:#5a4e38; text-transform:uppercase; margin:0;'>Production Bookings Dashboard</p>
</div>
""", unsafe_allow_html=True)

def badge_html(project_type):
    type_map = {
        "Feature Film": ("badge-feature", "Feature"),
        "Short Film": ("badge-short", "Short"),
        "Documentary": ("badge-doc", "Documentary"),
        "TV Series / Pilot": ("badge-tv", "TV / Pilot"),
    }
    cls, label = type_map.get(project_type, ("badge-other", project_type))
    return f"<span class='badge {cls}'>{label}</span>"

if service_file:
    try:
        service_info = json.load(service_file)
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.readonly"
        ]
        creds = Credentials.from_service_account_info(service_info, scopes=scopes)
        gc = gspread.authorize(creds)
        st.sidebar.success("✅ Authenticated")

        sheet_url = "https://docs.google.com/spreadsheets/d/YOUR_GOOGLE_SHEET_ID_HERE/edit"
        sh = gc.open_by_url(sheet_url)
        worksheet = sh.get_worksheet(0)
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)

        if df.empty:
            st.warning("No bookings found in the sheet yet.")
            st.stop()

        # Parse dates
        for col in ["shoot_start", "shoot_end", "submitted_at"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")

        # -------------------------
        # SIDEBAR FILTERS
        # -------------------------
        with st.sidebar:
            if "project_type" in df.columns:
                type_filter = st.multiselect("Project Type", df["project_type"].unique(), default=list(df["project_type"].unique()))
                df = df[df["project_type"].isin(type_filter)]

            if "budget_tier" in df.columns:
                budget_filter = st.multiselect("Budget Tier", df["budget_tier"].unique(), default=list(df["budget_tier"].unique()))
                df = df[df["budget_tier"].isin(budget_filter)]

            if "production_phase" in df.columns:
                phase_filter = st.multiselect("Production Phase", df["production_phase"].unique(), default=list(df["production_phase"].unique()))
                df = df[df["production_phase"].isin(phase_filter)]

        # -------------------------
        # KPI CARDS
        # -------------------------
        st.markdown('<div class="section-label">Overview</div>', unsafe_allow_html=True)
        c1, c2, c3, c4, c5 = st.columns(5)

        total_projects = len(df)
        total_shoot_days = int(df["total_shoot_days"].sum()) if "total_shoot_days" in df.columns else 0
        priority_count = int(df["priority_booking"].sum()) if "priority_booking" in df.columns else 0
        nda_count = int(df["nda_required"].astype(str).str.lower().isin(["true","yes","1"]).sum()) if "nda_required" in df.columns else 0
        avg_crew = df["crew_size"].value_counts().idxmax() if "crew_size" in df.columns and not df.empty else "N/A"

        with c1:
            st.markdown(f"""<div class='metric-card'>
                <div class='metric-label'>Total Bookings</div>
                <div class='metric-value'>{total_projects}</div>
                <div class='metric-sub'>Active Projects</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""<div class='metric-card'>
                <div class='metric-label'>Total Shoot Days</div>
                <div class='metric-value'>{total_shoot_days:,}</div>
                <div class='metric-sub'>Across All Projects</div>
            </div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""<div class='metric-card'>
                <div class='metric-label'>Priority Bookings</div>
                <div class='metric-value'>{priority_count}</div>
                <div class='metric-sub'>Rush Consultations</div>
            </div>""", unsafe_allow_html=True)
        with c4:
            st.markdown(f"""<div class='metric-card'>
                <div class='metric-label'>NDA Required</div>
                <div class='metric-value'>{nda_count}</div>
                <div class='metric-sub'>Confidential Projects</div>
            </div>""", unsafe_allow_html=True)
        with c5:
            st.markdown(f"""<div class='metric-card'>
                <div class='metric-label'>Top Crew Size</div>
                <div class='metric-value' style='font-size:1.1rem; padding-top:0.4rem;'>{avg_crew}</div>
                <div class='metric-sub'>Most Common</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # -------------------------
        # CHARTS — Row 1
        # -------------------------
        st.markdown('<div class="section-label">Analytics</div>', unsafe_allow_html=True)
        ch1, ch2 = st.columns(2)

        with ch1:
            if "project_type" in df.columns:
                type_counts = df["project_type"].value_counts().reset_index()
                type_counts.columns = ["Project Type", "Count"]
                fig = px.pie(
                    type_counts, names="Project Type", values="Count",
                    title="Bookings by Project Type",
                    color_discrete_sequence=["#d4a843","#b8861f","#8a6010","#5a4010","#3a2808","#e8c060"]
                )
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#c8bea0", title_font_color="#d4a843",
                    legend_font_color="#c8bea0"
                )
                st.plotly_chart(fig, use_container_width=True)

        with ch2:
            if "budget_tier" in df.columns:
                budget_counts = df["budget_tier"].value_counts().reset_index()
                budget_counts.columns = ["Budget Tier", "Count"]
                fig2 = px.bar(
                    budget_counts, x="Budget Tier", y="Count",
                    title="Bookings by Budget Tier",
                    color="Count",
                    color_continuous_scale=["#2a1a08","#d4a843"]
                )
                fig2.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#c8bea0", title_font_color="#d4a843",
                    xaxis=dict(gridcolor="#1a1a0a"), yaxis=dict(gridcolor="#1a1a0a"),
                    showlegend=False
                )
                st.plotly_chart(fig2, use_container_width=True)

        # -------------------------
        # CHARTS — Row 2
        # -------------------------
        ch3, ch4 = st.columns(2)

        with ch3:
            if "genre" in df.columns:
                genre_counts = df["genre"].value_counts().reset_index()
                genre_counts.columns = ["Genre", "Count"]
                fig3 = px.bar(
                    genre_counts, x="Count", y="Genre", orientation="h",
                    title="Bookings by Genre",
                    color="Count",
                    color_continuous_scale=["#1a0a00","#d4a843"]
                )
                fig3.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#c8bea0", title_font_color="#d4a843",
                    xaxis=dict(gridcolor="#1a1a0a"), yaxis=dict(gridcolor="#1a1a0a"),
                    showlegend=False
                )
                st.plotly_chart(fig3, use_container_width=True)

        with ch4:
            if "submitted_at" in df.columns and df["submitted_at"].notna().sum() > 0:
                df_time = df.dropna(subset=["submitted_at"]).copy()
                df_time["month"] = df_time["submitted_at"].dt.to_period("M").astype(str)
                monthly = df_time.groupby("month").size().reset_index(name="Bookings")
                fig4 = px.line(
                    monthly, x="month", y="Bookings",
                    title="Bookings Over Time (Monthly)",
                    markers=True
                )
                fig4.update_traces(line_color="#d4a843", marker_color="#d4a843")
                fig4.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    font_color="#c8bea0", title_font_color="#d4a843",
                    xaxis=dict(gridcolor="#1a1a0a"), yaxis=dict(gridcolor="#1a1a0a")
                )
                st.plotly_chart(fig4, use_container_width=True)

        # -------------------------
        # PROJECT CARDS
        # -------------------------
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Active Bookings</div>', unsafe_allow_html=True)

        for _, row in df.iterrows():
            title = row.get("project_title", "Untitled")
            company = row.get("company_name", "Unknown Company")
            pt = row.get("project_type", "")
            genre = row.get("genre", "")
            budget = row.get("budget_tier", "")
            contact = row.get("full_name", "")
            shoot_start = str(row.get("shoot_start", ""))[:10]
            shoot_end = str(row.get("shoot_end", ""))[:10]
            location = row.get("primary_location", "")
            phase = row.get("production_phase", "")
            crew = row.get("crew_size", "")
            badge = badge_html(pt)

            st.markdown(f"""
            <div class='project-card'>
                <div class='project-title'>{title} {badge}</div>
                <div class='project-meta'>
                    <strong style='color:#c8bea0;'>{company}</strong> &nbsp;·&nbsp; {contact}
                    &nbsp;|&nbsp; <span style='color:#d4a843;'>{genre}</span>
                    &nbsp;|&nbsp; {budget}
                </div>
                <div class='project-meta' style='margin-top:6px;'>
                    📅 {shoot_start} → {shoot_end}
                    &nbsp;·&nbsp; 📍 {location}
                    &nbsp;·&nbsp; 🎥 {phase}
                    &nbsp;·&nbsp; 👥 {crew}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # -------------------------
        # FULL DATA TABLE
        # -------------------------
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Full Data Table</div>', unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True)

        # -------------------------
        # DOWNLOAD
        # -------------------------
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️ Download Bookings CSV",
            data=csv,
            file_name=f"chasing_destiny_bookings_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"⚠️ Error loading dashboard: {e}")

else:
    st.markdown("""
    <div style='text-align:center; padding: 4rem 0; color: #5a4e38;'>
        <div style='font-size:3rem; margin-bottom:1rem;'>🔑</div>
        <div style='font-family: Georgia, serif; font-size:1.2rem; color:#8a7a5a; margin-bottom:0.5rem;'>
            Upload your Google Service Account JSON key
        </div>
        <div style='font-size:0.8rem; letter-spacing:0.15em; text-transform:uppercase;'>
            to access the production dashboard
        </div>
    </div>
    """, unsafe_allow_html=True)
