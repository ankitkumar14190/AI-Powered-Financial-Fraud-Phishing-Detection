import pandas as pd

from src.config.config import DATASET_PATH, SAMPLE_TRANSACTIONS_PATH
from src.utils.helpers import get_logger

logger = get_logger(__name__)


def create_sample(n: int = 20, random_state: int = 42) -> None:
    df = pd.read_csv(DATASET_PATH)
    sample = df.drop(columns=["Class"]).sample(n, random_state=random_state)
    sample.to_csv(SAMPLE_TRANSACTIONS_PATH, index=False)
    logger.info("Sample CSV created at %s (%d rows).", SAMPLE_TRANSACTIONS_PATH, n)


if __name__ == "__main__":
    create_sample()
