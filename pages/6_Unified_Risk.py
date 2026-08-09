"""
Unified Risk Score page.

New page: combines Fraud and Phishing history into a single blended
"organizational risk" score (60% fraud rate / 40% phishing rate), so a
judge/analyst gets one headline number instead of having to mentally
combine two separate dashboards.
"""

import streamlit as st

from src.database.db import get_all_predictions, get_all_phishing_scans
from src.dashboard.dashboard import (
    build_fraud_dataframe,
    build_phishing_dataframe,
    unified_risk_score,
)

st.set_page_config(page_title="Unified Risk | Fraud & Phishing Detection", page_icon="🧭")

st.title("🧭 Unified Risk Score")
st.caption(
    "A single blended risk indicator combining fraud transaction history "
    "(60% weight) and phishing scan history (40% weight)."
)

fraud_rows = get_all_predictions()
phishing_rows = get_all_phishing_scans()

if not fraud_rows and not phishing_rows:
    st.info("No scans yet. Try the Fraud Detection or Phishing Detection pages first.")
    st.stop()

fraud_df = build_fraud_dataframe(fraud_rows) if fraud_rows else build_fraud_dataframe([])
phishing_df = build_phishing_dataframe(phishing_rows) if phishing_rows else build_phishing_dataframe([])

result = unified_risk_score(fraud_df, phishing_df)
score = result["combined_score"]

if score < 30:
    label, color = "🟢 Low Risk", "green"
elif score < 70:
    label, color = "🟡 Elevated Risk", "orange"
else:
    label, color = "🔴 High Risk", "red"

st.markdown(f"## {label}")
st.progress(min(int(score), 100) / 100)

col1, col2, col3 = st.columns(3)
col1.metric("Combined Risk Score", f"{score}/100")
col2.metric("Fraud Rate", f"{result['fraud_rate']}%")
col3.metric("Phishing Risk Rate", f"{result['phishing_rate']}%")

st.markdown("""
**How this is calculated:**
`Combined Score = 0.6 x Fraud Rate + 0.4 x Phishing Risk Rate`

- **Fraud Rate** = % of scanned transactions flagged as fraud
- **Phishing Risk Rate** = weighted % of scanned URLs that were Dangerous (full weight) or Suspicious (half weight)
""")
