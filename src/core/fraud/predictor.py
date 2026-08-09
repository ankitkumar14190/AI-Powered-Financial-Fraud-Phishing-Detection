import joblib
import pandas as pd

from src.config.config import MODEL_PATH
from src.utils.helpers import get_logger

logger = get_logger(__name__)


class FraudPredictor:
    """Loads the trained fraud model once and scores transaction batches."""

    def __init__(self):
        try:
            self.model = joblib.load(MODEL_PATH)
        except FileNotFoundError as exc:
            logger.error("Model file not found at %s", MODEL_PATH)
            raise FileNotFoundError(
                f"No trained model found at {MODEL_PATH}. "
                "Run `python -m src.core.fraud.train_model` first."
            ) from exc

        self.feature_names = list(self.model.feature_names_in_)
        logger.info("Fraud model loaded (%d features).", len(self.feature_names))

    def predict_batch(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Score every row of `dataframe` and return a copy with
        Prediction / Confidence / Risk columns appended.
        """
        df = dataframe.copy()

        if "Class" in df.columns:
            df = df.drop(columns=["Class"])

        missing = set(self.feature_names) - set(df.columns)
        extra = set(df.columns) - set(self.feature_names)

        if missing:
            logger.error("Uploaded CSV is missing required columns: %s", missing)
            raise ValueError(f"Missing columns: {sorted(missing)}")

        if extra:
            logger.error("Uploaded CSV has unexpected columns: %s", extra)
            raise ValueError(f"Unexpected columns: {sorted(extra)}")

        df = df[self.feature_names]

        predictions = self.model.predict(df)
        probabilities = self.model.predict_proba(df)
        confidence = probabilities.max(axis=1) * 100

        results = dataframe.copy()
        results["Prediction"] = predictions
        results["Confidence"] = confidence.round(2)
        results["Risk"] = results["Prediction"].map({
            0: "🟢 Legitimate",
            1: "🔴 Fraud",
        })

        logger.info(
            "Scored %d transactions (%d flagged as fraud).",
            len(results),
            int((results["Prediction"] == 1).sum()),
        )

        return results
