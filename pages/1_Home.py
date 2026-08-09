import streamlit as st

st.set_page_config(page_title="Home | Fraud & Phishing Detection", page_icon="🏠")

st.title("🛡️ AI-Powered Financial Fraud & Phishing Detection")

st.markdown("""
## Welcome

This platform helps identify:

- 💳 Fraudulent financial transactions
- 🌐 Phishing URLs
- 📊 Security analytics

---

### Modules

**💳 Fraud Detection** — Upload a transaction dataset and let a trained
Random Forest model flag likely-fraudulent transactions.

**🌐 Phishing Detection** — Analyze suspicious URLs against a set of
cybersecurity heuristics (HTTPS usage, IP-based hosts, suspicious
keywords, and more).

**📊 Dashboard** — Review the history of every fraud and phishing scan,
with summary metrics and charts.

**ℹ️ About** — Learn about the technologies used in this project.
""")
