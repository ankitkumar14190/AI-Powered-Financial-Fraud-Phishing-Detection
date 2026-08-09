"""
Fraud Detection page.

Now has two tabs:
  * Batch CSV Upload (original functionality, unchanged behavior)
  * Single Transaction Check (new) -- a manual entry form for a live demo,
    with a SHAP explanation of *why* the model made its call.

Performance/error-handling notes carried over from the previous version:
  * FraudPredictor() and FraudExplainer() are both wrapped in
    st.cache_resource so the model (and the SHAP explainer, which is not
    cheap to build) load once per session, not on every click.
  * FileNotFoundError (no trained model) vs ValueError (bad columns) are
    handled separately so the user gets an actionable message either way.
"""

import random

import pandas as pd
import streamlit as st

from src.config.config import SAMPLE_TRANSACTIONS_PATH
from src.core.fraud.predictor import FraudPredictor
from src.explainability.shap_engine import FraudExplainer
from src.database.db import save_prediction
from src.utils.helpers import get_logger

logger = get_logger(__name__)

st.set_page_config(page_title="Fraud Detection | Fraud & Phishing Detection", page_icon="💳")

st.title("💳 AI Fraud Detection")


@st.cache_resource(show_spinner=False)
def load_predictor() -> FraudPredictor:
    return FraudPredictor()


@st.cache_resource(show_spinner=False)
def load_explainer(_predictor: FraudPredictor) -> FraudExplainer:
    return FraudExplainer(_predictor.model)


batch_tab, single_tab = st.tabs(["📁 Batch CSV Upload", "🔎 Single Transaction Check"])

# ---------------------------------------------------------------------------
# Batch CSV Upload (original functionality)
# ---------------------------------------------------------------------------
with batch_tab:
    st.caption("Upload a transaction CSV in the standard `creditcard.csv` schema to score it.")

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    if uploaded_file is not None:

        try:
            df = pd.read_csv(uploaded_file)
        except Exception:
            logger.exception("Failed to read uploaded CSV.")
            st.error("Could not read that file. Make sure it's a valid CSV.")
            st.stop()

        st.subheader("Dataset Preview")
        st.dataframe(df.head(), use_container_width=True)

        if st.button("Analyze Transactions", type="primary"):

            with st.spinner("Scoring transactions..."):
                try:
                    predictor = load_predictor()
                    results = predictor.predict_batch(df)

                    for _, row in results.iterrows():
                        save_prediction(
                            int(row["Prediction"]),
                            float(row["Confidence"]),
                            row["Risk"],
                        )

                except FileNotFoundError as e:
                    logger.error("Model not found: %s", e)
                    st.error(
                        "🚫 No trained model found. Run the training script "
                        "(`python -m src.core.fraud.train_model`) before using this page."
                    )
                    st.stop()

                except ValueError as e:
                    logger.warning("Invalid uploaded CSV: %s", e)
                    st.error(f"⚠️ {e}")
                    st.stop()

                except Exception:
                    logger.exception("Unexpected error during fraud analysis.")
                    st.error("An unexpected error occurred. Check logs/app.log for details.")
                    st.stop()

            st.success("Analysis complete.")

            frauds = int((results["Prediction"] == 1).sum())
            safe = int((results["Prediction"] == 0).sum())

            col1, col2, col3 = st.columns(3)
            col1.metric("Transactions", len(results))
            col2.metric("Frauds", frauds)
            col3.metric("Legitimate", safe)

            st.subheader("Prediction Results")
            st.dataframe(results, use_container_width=True)

            csv = results.to_csv(index=False).encode("utf-8")
            st.download_button("Download Results", csv, "fraud_results.csv", "text/csv")

# ---------------------------------------------------------------------------
# Single Transaction Check (new)
# ---------------------------------------------------------------------------
with single_tab:
    st.caption(
        "Manually enter a transaction for an instant check. The dataset's "
        "V1-V28 columns are anonymized PCA components, so they default to "
        "0 (dataset average) -- use 'Load Random Sample' for realistic demo values."
    )

    try:
        predictor = load_predictor()
    except FileNotFoundError as e:
        st.error(
            "🚫 No trained model found. Run the training script "
            "(`python -m src.core.fraud.train_model`) before using this page."
        )
        st.stop()

    feature_names = predictor.feature_names

    if "manual_txn_values" not in st.session_state:
        st.session_state.manual_txn_values = {name: 0.0 for name in feature_names}
        if "Amount" in feature_names:
            st.session_state.manual_txn_values["Amount"] = 100.0

    if st.button("🎲 Load Random Sample"):
        if SAMPLE_TRANSACTIONS_PATH.exists():
            sample_df = pd.read_csv(SAMPLE_TRANSACTIONS_PATH)
            row = sample_df.sample(1).iloc[0]
            for name in feature_names:
                if name in row:
                    st.session_state.manual_txn_values[name] = float(row[name])
            st.rerun()
        else:
            st.warning(
                "No sample file found at assets/sample_transactions.csv. "
                "Run `python -m src.core.fraud.create_sample` first."
            )

    main_col1, main_col2 = st.columns(2)
    with main_col1:
        if "Amount" in feature_names:
            st.session_state.manual_txn_values["Amount"] = st.number_input(
                "Transaction Amount ($)",
                min_value=0.0,
                value=float(st.session_state.manual_txn_values.get("Amount", 100.0)),
                step=1.0,
            )
    with main_col2:
        if "Time" in feature_names:
            st.session_state.manual_txn_values["Time"] = st.number_input(
                "Time (seconds since first transaction in dataset)",
                min_value=0.0,
                value=float(st.session_state.manual_txn_values.get("Time", 0.0)),
                step=1.0,
            )

    advanced_features = [f for f in feature_names if f not in ("Amount", "Time")]
    with st.expander(f"Advanced: {len(advanced_features)} anonymized PCA features (V1-V28)"):
        cols = st.columns(4)
        for i, name in enumerate(advanced_features):
            with cols[i % 4]:
                st.session_state.manual_txn_values[name] = st.number_input(
                    name,
                    value=float(st.session_state.manual_txn_values.get(name, 0.0)),
                    key=f"manual_{name}",
                    format="%.4f",
                )

    if st.button("Analyze Transaction", type="primary"):
        row_df = pd.DataFrame([st.session_state.manual_txn_values])[feature_names]

        try:
            result_df = predictor.predict_batch(row_df)
        except Exception:
            logger.exception("Unexpected error during single-transaction analysis.")
            st.error("An unexpected error occurred. Check logs/app.log for details.")
            st.stop()

        row_result = result_df.iloc[0]

        try:
            save_prediction(
                int(row_result["Prediction"]),
                float(row_result["Confidence"]),
                row_result["Risk"],
            )
        except Exception:
            logger.exception("Failed to save single-transaction prediction.")

        st.subheader(row_result["Risk"])
        st.metric("Confidence", f"{row_result['Confidence']}%")

        st.write("### Why did the model decide this?")
        with st.spinner("Computing SHAP explanation..."):
            explainer = load_explainer(predictor)
            top_features = explainer.explain_row(row_df, top_n=5)

        if not top_features:
            st.caption("Explanation unavailable for this prediction.")
        else:
            explain_df = pd.DataFrame(top_features, columns=["Feature", "Impact"])
            explain_df["Direction"] = explain_df["Impact"].apply(
                lambda v: "⬆️ Towards Fraud" if v > 0 else "⬇️ Towards Legitimate"
            )
            st.dataframe(explain_df, use_container_width=True)
            st.bar_chart(explain_df.set_index("Feature")["Impact"])
