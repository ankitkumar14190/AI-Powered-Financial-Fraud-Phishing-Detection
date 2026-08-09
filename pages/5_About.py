import streamlit as st

st.set_page_config(page_title="About | Fraud & Phishing Detection", page_icon="ℹ️")

st.title("ℹ️ About")

st.markdown("""
# AI-Powered Financial Fraud & Phishing Detection Platform

## Features

- AI fraud detection (Random Forest)
- Phishing URL detection (rule-based heuristics)
- Dashboard with scan history for both modules
- SQLite persistence

## Tech Stack

- Python, Streamlit
- Scikit-learn, Pandas, NumPy
- SQLite, Joblib

## Architecture

- `src/core/fraud/` — model training, preprocessing, and batch prediction
- `src/core/phishing/` — URL feature extraction, scoring rules, and the detector
- `src/database/` — SQLite persistence for both fraud and phishing scans
- `src/dashboard/` — shared data-shaping helpers for the Dashboard page
- `pages/` — thin Streamlit view layer that calls into `src/`

## Future Scope

- SHAP explainability for fraud predictions
- XGBoost as an alternative model
- Real-time phishing intelligence APIs
- Email alerts
- User authentication
""")
