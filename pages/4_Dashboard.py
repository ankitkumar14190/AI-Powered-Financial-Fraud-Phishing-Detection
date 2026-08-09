import streamlit as st

from src.database.db import get_all_predictions, get_all_phishing_scans
from src.dashboard.dashboard import (
    build_fraud_dataframe,
    build_phishing_dataframe,
    fraud_summary,
    phishing_summary,
    fraud_daily_trend,
    phishing_daily_trend,
    unified_risk_score,
)
from src.reporting.report_generator import build_dashboard_pdf

st.set_page_config(page_title="Dashboard | Fraud & Phishing Detection", page_icon="📊")

st.title("📊 Dashboard")

fraud_rows = get_all_predictions()
phishing_rows = get_all_phishing_scans()

fraud_df = build_fraud_dataframe(fraud_rows) if fraud_rows else build_fraud_dataframe([])
phishing_df = build_phishing_dataframe(phishing_rows) if phishing_rows else build_phishing_dataframe([])

if fraud_rows or phishing_rows:
    f_summary = fraud_summary(fraud_df)
    p_summary = phishing_summary(phishing_df)
    unified = unified_risk_score(fraud_df, phishing_df)

    pdf_bytes = build_dashboard_pdf(f_summary, p_summary, unified)
    st.download_button(
        "📄 Download PDF Report",
        data=pdf_bytes,
        file_name="fraud_phishing_summary_report.pdf",
        mime="application/pdf",
    )

fraud_tab, phishing_tab = st.tabs(["💳 Fraud History", "🌐 Phishing History"])

with fraud_tab:
    if not fraud_rows:
        st.info("No transactions scanned yet. Try the Fraud Detection page.")
    else:
        summary = fraud_summary(fraud_df)

        col1, col2, col3 = st.columns(3)
        col1.metric("Transactions", summary["total"])
        col2.metric("Frauds", summary["frauds"])
        col3.metric("Legitimate", summary["legitimate"])

        st.subheader("Recent Predictions")
        st.dataframe(fraud_df, use_container_width=True)
        st.download_button(
            "Download Fraud History (CSV)",
            fraud_df.to_csv(index=False).encode("utf-8"),
            "fraud_history.csv",
            "text/csv",
        )

        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.caption("Prediction Distribution")
            st.bar_chart(fraud_df["Prediction"].value_counts())
        with chart_col2:
            st.caption("Confidence Over Time")
            st.line_chart(fraud_df["Confidence"])

        st.caption("Daily Volume Trend")
        st.area_chart(fraud_daily_trend(fraud_df))

with phishing_tab:
    if not phishing_rows:
        st.info("No URLs scanned yet. Try the Phishing Detection page.")
    else:
        summary = phishing_summary(phishing_df)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Scans", summary["total"])
        col2.metric("🔴 Dangerous", summary["dangerous"])
        col3.metric("🟡 Suspicious", summary["suspicious"])
        col4.metric("🟢 Safe", summary["safe"])

        st.subheader("Recent Scans")
        st.dataframe(phishing_df, use_container_width=True)
        st.download_button(
            "Download Phishing History (CSV)",
            phishing_df.to_csv(index=False).encode("utf-8"),
            "phishing_history.csv",
            "text/csv",
        )

        st.caption("Risk Distribution")
        st.bar_chart(phishing_df["Risk"].value_counts())

        st.caption("Daily Volume Trend")
        st.area_chart(phishing_daily_trend(phishing_df))
