"""
Dashboard data-shaping helpers.

Previously this file was empty and pages/4_Dashboard.py built its DataFrame
and metrics inline. Moving that logic here means:
  * pages/4_Dashboard.py becomes a thin view layer (as it should be)
  * the same helpers can be reused if a phishing history tab, an API,
    or a future export feature needs the same data shape
"""

from typing import List, Tuple

import pandas as pd


def build_fraud_dataframe(rows: List[Tuple]) -> pd.DataFrame:
    """Convert raw `transactions` table rows into a display-ready DataFrame."""
    return pd.DataFrame(
        rows,
        columns=["ID", "Prediction", "Confidence", "Risk", "Created At"],
    )


def build_phishing_dataframe(rows: List[Tuple]) -> pd.DataFrame:
    """Convert raw `phishing_scans` table rows into a display-ready DataFrame."""
    return pd.DataFrame(
        rows,
        columns=["ID", "URL", "Score", "Risk", "Reasons", "Created At"],
    )


def fraud_summary(df: pd.DataFrame) -> dict:
    """Return headline counts for the fraud metrics row."""
    return {
        "total": len(df),
        "frauds": int((df["Prediction"] == 1).sum()),
        "legitimate": int((df["Prediction"] == 0).sum()),
    }


def phishing_summary(df: pd.DataFrame) -> dict:
    """Return headline counts for the phishing metrics row."""
    return {
        "total": len(df),
        "dangerous": int((df["Risk"] == "🔴 Dangerous").sum()),
        "suspicious": int((df["Risk"] == "🟡 Suspicious").sum()),
        "safe": int((df["Risk"] == "🟢 Safe").sum()),
    }


def _with_date_column(df: pd.DataFrame, timestamp_col: str = "Created At") -> pd.DataFrame:
    df = df.copy()
    df["Date"] = pd.to_datetime(df[timestamp_col]).dt.date
    return df


def fraud_daily_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Daily count of Fraud vs Legitimate predictions, for a trend chart."""
    df = _with_date_column(df)
    trend = df.groupby(["Date", "Prediction"]).size().unstack(fill_value=0)
    return trend.rename(columns={0: "Legitimate", 1: "Fraud"})


def phishing_daily_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Daily count of scans per risk label, for a trend chart."""
    df = _with_date_column(df)
    return df.groupby(["Date", "Risk"]).size().unstack(fill_value=0)


def unified_risk_score(fraud_df: pd.DataFrame, phishing_df: pd.DataFrame) -> dict:
    """
    Combine fraud and phishing history into a single 0-100 "organizational
    risk" score, weighted 60/40 towards fraud (financial loss is typically
    more severe than a single phishing click).

    Returns the blended score plus each module's own rate, so the UI can
    show the breakdown alongside the headline number.
    """
    fraud_total = len(fraud_df)
    fraud_rate = (fraud_df["Prediction"] == 1).mean() * 100 if fraud_total else 0.0

    phishing_total = len(phishing_df)
    if phishing_total:
        dangerous = (phishing_df["Risk"] == "🔴 Dangerous").sum()
        suspicious = (phishing_df["Risk"] == "🟡 Suspicious").sum()
        phishing_rate = ((dangerous * 1.0 + suspicious * 0.5) / phishing_total) * 100
    else:
        phishing_rate = 0.0

    combined = round(min((0.6 * fraud_rate) + (0.4 * phishing_rate), 100), 1)

    return {
        "combined_score": combined,
        "fraud_rate": round(fraud_rate, 1),
        "phishing_rate": round(phishing_rate, 1),
    }
