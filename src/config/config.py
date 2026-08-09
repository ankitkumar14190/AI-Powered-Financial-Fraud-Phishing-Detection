from pathlib import Path

# ---------------------------------------------------------------------------
# Project root
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# Directories
# ---------------------------------------------------------------------------
DATA_DIR = PROJECT_ROOT / "data"
MODEL_DIR = PROJECT_ROOT / "models"
DATABASE_DIR = PROJECT_ROOT / "database"
LOG_DIR = PROJECT_ROOT / "logs"
ASSETS_DIR = PROJECT_ROOT / "assets"

for directory in (MODEL_DIR, DATABASE_DIR, LOG_DIR, ASSETS_DIR):
    directory.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Files
# ---------------------------------------------------------------------------
DATASET_PATH = DATA_DIR / "creditcard.csv"
MODEL_PATH = MODEL_DIR / "fraud_model.pkl"
SCALER_PATH = MODEL_DIR / "scaler.pkl"
DATABASE_PATH = DATABASE_DIR / "fraud.db"
LOG_FILE = LOG_DIR / "app.log"
SAMPLE_TRANSACTIONS_PATH = ASSETS_DIR / "sample_transactions.csv"

# ---------------------------------------------------------------------------
# Fraud model training parameters (single source of truth for train_model.py)
# ---------------------------------------------------------------------------
TEST_SIZE = 0.20
RANDOM_STATE = 42
N_ESTIMATORS = 200

# ---------------------------------------------------------------------------
# Phishing detector thresholds
# ---------------------------------------------------------------------------
PHISHING_SAFE_THRESHOLD = 30
PHISHING_SUSPICIOUS_THRESHOLD = 70
