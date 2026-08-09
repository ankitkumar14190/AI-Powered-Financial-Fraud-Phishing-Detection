"""
SHAP-based explainability for the fraud Random Forest model.

Why this exists: a bare "Fraud / Not Fraud" label with a confidence number
doesn't tell an analyst (or a hackathon judge) *why* the model decided that.
This wraps shap.TreeExplainer (native, fast support for tree ensembles like
RandomForestClassifier) and returns the top contributing features for a
single transaction, in plain, human-readable form.

Note on shap's output shape: depending on the installed shap version,
`TreeExplainer(...).shap_values(X)` can return either:
  * a list of two (n_samples, n_features) arrays, one per class, or
  * a single (n_samples, n_features, n_classes) array.
Both are handled explicitly below instead of assuming one shape and
crashing on the other.
"""

from typing import List, Tuple

import pandas as pd
import shap

from src.utils.helpers import get_logger

logger = get_logger(__name__)

FRAUD_CLASS_INDEX = 1  # index of the "fraud" class in predict_proba/shap output


class FraudExplainer:
    """Explains individual fraud predictions using SHAP values."""

    def __init__(self, model):
        self.model = model
        self.explainer = shap.TreeExplainer(model)

    def explain_row(self, row: pd.DataFrame, top_n: int = 5) -> List[Tuple[str, float]]:
        """
        Return the `top_n` features that most influenced the fraud-class
        prediction for a single-row DataFrame, ranked by |impact|.

        Each item is (feature_name, shap_value) where a positive value
        pushed the prediction *towards* fraud and a negative value pushed
        it *away* from fraud.
        """
        try:
            shap_values = self.explainer.shap_values(row)
            values = self._extract_fraud_class_values(shap_values)

            contributions = list(zip(row.columns, values))
            contributions.sort(key=lambda item: abs(item[1]), reverse=True)
            return contributions[:top_n]

        except Exception:
            logger.exception("SHAP explanation failed.")
            return []

    @staticmethod
    def _extract_fraud_class_values(shap_values) -> List[float]:
        """Normalize the two possible shap_values output shapes into a flat list."""
        if isinstance(shap_values, list):
            # List of per-class arrays: [class0_array, class1_array]
            return list(shap_values[FRAUD_CLASS_INDEX][0])

        # Single ndarray: (n_samples, n_features, n_classes)
        if shap_values.ndim == 3:
            return list(shap_values[0, :, FRAUD_CLASS_INDEX])

        # Single ndarray: (n_samples, n_features) -- already the fraud class
        return list(shap_values[0])
