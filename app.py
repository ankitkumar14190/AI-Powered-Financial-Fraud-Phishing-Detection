"""
Streamlit multipage app entrypoint.

Change vs original: wraps create_tables() in error handling so a locked or
corrupted database file surfaces a friendly message instead of crashing
the whole app before it can even render, and initializes logging so every
page's log calls land in the same file from the very first run.
"""

import streamlit as st

from src.database.db import create_tables
from src.utils.helpers import get_logger

logger = get_logger(__name__)

st.set_page_config(
    page_title="AI Financial Fraud & Phishing Detection",
    page_icon="🛡️",
    layout="wide",
)

try:
    create_tables()
except Exception:
    logger.exception("Failed to initialize the database.")
    st.error(
        "⚠️ Could not initialize the local database. "
        "Check logs/app.log for details."
    )

st.title("🛡️ AI-Powered Financial Fraud & Phishing Detection")

st.markdown(
    "An end-to-end demo platform combining a **Random Forest** fraud "
    "classifier with a **rule-based phishing URL scanner**, both backed "
    "by a local SQLite history and analytics dashboard."
)

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("💳 Fraud Detection")
    st.write("Upload a transaction CSV and flag likely-fraudulent rows.")

with col2:
    st.subheader("🌐 Phishing Detection")
    st.write("Paste a URL and get an instant heuristic risk score.")

with col3:
    st.subheader("📊 Dashboard")
    st.write("Review scan history and trends across both modules.")

st.info("Use the sidebar to navigate between pages.")
