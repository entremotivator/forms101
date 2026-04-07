import streamlit as st
import pandas as pd
import gspread
import json
from google.oauth2.service_account import Credentials
from streamlit_card import card
import plotly.express as px

# ---------------------------
# Sidebar: Google Service Account Login
# ---------------------------
st.sidebar.header("🔑 Google Service Account Login")
service_file = st.sidebar.file_uploader("Upload JSON Key", type=["json"])

if service_file:
    try:
        # Load JSON from uploaded file
        service_info = json.load(service_file)

        # Add correct Google API scopes
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive.readonly"  # optional if only reading
        ]

        # Create credentials with scopes
        creds = Credentials.from_service_account_info(service_info, scopes=scopes)
        gc = gspread.authorize(creds)
        st.sidebar.success("✅ Authenticated successfully!")

        # ---------------------------
        # Load Google Sheet
        # ---------------------------
        sheet_url = "https://docs.google.com/spreadsheets/d/1gFrgzaV9wA77AfWkhl3bsQk5bjN7NkrB2T1K9idZ3EE/edit#gid=368956829"
        sh = gc.open_by_url(sheet_url)
        worksheet = sh.get_worksheet(0)  # First sheet
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)

        # ---------------------------
        # Sidebar Filters
        # ---------------------------
        st.sidebar.header("📌 Filters")
        if "Status" in df.columns:
            status_filter = st.sidebar.multiselect(
                "Filter by Status", df["Status"].unique(), default=df["Status"].unique()
            )
            df = df[df["Status"].isin(status_filter)]

        if "Category" in df.columns:
            category_filter = st.sidebar.multiselect(
                "Filter by Category", df["Category"].unique(), default=df["Category"].unique()
            )
            df = df[df["Category"].isin(category_filter)]

        # ---------------------------
        # Dashboard Title
        # ---------------------------
        st.title("📊 Live Google Sheets Dashboard")

        # ---------------------------
        # Overview Cards
        # ---------------------------
        st.subheader("✨ Overview Cards")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            card(title="Total Rows", text=f"{len(df)}", width=250)

        with col2:
            if "Amount" in df.columns:
                total_amount = df["Amount"].sum()
                card(title="Total Amount", text=f"${total_amount:,.2f}", width=250)
            else:
                card(title="Total Amount", text="N/A", width=250)

        with col3:
            if "Status" in df.columns:
                completed = df[df["Status"].str.lower() == "completed"].shape[0]
                card(title="Completed", text=f"{completed}", width=250)
            else:
                card(title="Completed", text="N/A", width=250)

        with col4:
            if "Amount" in df.columns:
                avg_amount = df["Amount"].mean()
                card(title="Average Amount", text=f"${avg_amount:,.2f}", width=250)
            else:
                card(title="Average Amount", text="N/A", width=250)

        # ---------------------------
        # Dynamic Row Cards
        # ---------------------------
        st.subheader("📇 Records")
        for index, row in df.iterrows():
            card(
                title=f"Record {index+1}: {row.get('Name', 'No Name')}",
                text="\n".join([f"{k}: {v}" for k, v in row.items()]),
                width=400
            )

        # ---------------------------
        # Charts
        # ---------------------------
        st.subheader("📈 Charts & Insights")

        if "Amount" in df.columns and "Category" in df.columns and "Status" in df.columns:
            fig = px.bar(
                df, x="Category", y="Amount", color="Status",
                barmode="group", title="Amount by Category and Status"
            )
            st.plotly_chart(fig, use_container_width=True)

        if "Amount" in df.columns and "Date" in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            df_date = df.groupby('Date')['Amount'].sum().reset_index()
            fig2 = px.line(df_date, x='Date', y='Amount', title="Amount Over Time")
            st.plotly_chart(fig2, use_container_width=True)

        # ---------------------------
        # Full Data Table
        # ---------------------------
        st.subheader("📋 Full Data Table")
        st.dataframe(df)

        # ---------------------------
        # Download CSV
        # ---------------------------
        st.subheader("💾 Download Data")
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name='dashboard_data.csv',
            mime='text/csv'
        )

    except Exception as e:
        st.error(f"⚠️ Error: {e}")

else:
    st.info("Please upload a Google Service Account JSON file to access the dashboard.")
