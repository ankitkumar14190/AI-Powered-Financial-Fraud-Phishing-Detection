"""
Data loading and preprocessing for the fraud detection model.

Change vs original: test_size / random_state were magic numbers hardcoded
here; they now come from src/config/config.py so train_model.py and any
future retraining script/notebook share one source of truth.
"""

from pathlib import Path
from typing import Tuple

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

from src.config.config import TEST_SIZE, RANDOM_STATE


def load_data(file_path: Path) -> pd.DataFrame:
    """Load the credit card fraud dataset from disk."""
    return pd.read_csv(file_path)


def preprocess_data(
    df: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, StandardScaler]:
    """
    Split the dataset into stratified train/test sets and scale the
    'Amount' column (all other columns are already PCA-scaled in this
    dataset).
    """
    X = df.drop("Class", axis=1)
    y = df["Class"]

    scaler = StandardScaler()
    X = X.copy()
    X["Amount"] = scaler.fit_transform(X[["Amount"]])

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    return X_train, X_test, y_train, y_test, scaler
