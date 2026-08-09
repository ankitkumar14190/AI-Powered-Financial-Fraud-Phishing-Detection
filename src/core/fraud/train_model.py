"""
Trains the Random Forest fraud detection model and saves it + the scaler
to disk.

Change vs original: n_estimators=200 was hardcoded with a stray typo
("model =RandomForestClassifier"); hyperparameters now come from config.py,
and print() statements were replaced with proper logging so training runs
show up in logs/app.log alongside the rest of the app.
"""

import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

from src.core.fraud.preprocess import load_data, preprocess_data
from src.config.config import DATASET_PATH, MODEL_PATH, SCALER_PATH, N_ESTIMATORS, RANDOM_STATE
from src.utils.helpers import get_logger

logger = get_logger(__name__)


def train() -> None:
    logger.info("Loading dataset from %s", DATASET_PATH)
    df = load_data(DATASET_PATH)

    X_train, X_test, y_train, y_test, scaler = preprocess_data(df)

    logger.info("Training RandomForestClassifier (n_estimators=%d)...", N_ESTIMATORS)
    model = RandomForestClassifier(
        n_estimators=N_ESTIMATORS,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        class_weight="balanced",
    )
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    logger.info("Accuracy: %.4f", accuracy_score(y_test, predictions))
    logger.info("Classification report:\n%s", classification_report(y_test, predictions))
    logger.info("Confusion matrix:\n%s", confusion_matrix(y_test, predictions))

    joblib.dump(model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)

    logger.info("Model saved to %s", MODEL_PATH)
    logger.info("Scaler saved to %s", SCALER_PATH)


if __name__ == "__main__":
    train()
