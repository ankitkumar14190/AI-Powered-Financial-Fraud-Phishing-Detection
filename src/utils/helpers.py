import logging

from src.config.config import LOG_FILE

_CONFIGURED_LOGGERS = set()


def get_logger(name: str) -> logging.Logger:
    """
    Return a module-level logger that writes to console + logs/app.log.

    Safe to call multiple times with the same name (e.g. across Streamlit
    reruns) -- handlers are only attached once per logger name.
    """

    logger = logging.getLogger(name)

    if name in _CONFIGURED_LOGGERS:
        return logger

    logger.setLevel(logging.INFO)
    logger.propagate = False

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    _CONFIGURED_LOGGERS.add(name)

    return logger
