import logging
import os


def get_logger(name: str, level=logging.INFO):
    """
    Create a logger with both file and console output.
    Log files are stored in the root/logs directory.
    """
    # Resolve logs directory (2 levels up from current file)
    logs_dir = os.path.join(os.path.dirname(__file__), "../logs")
    os.makedirs(logs_dir, exist_ok=True)

    log_file = os.path.join(logs_dir, f"{name}.log")

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False  # prevent double logging

    # If handlers already exist, don't add duplicates
    if not logger.handlers:
        # File handler
        fh = logging.FileHandler(log_file)
        fh.setLevel(level)

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(level)

        formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        logger.addHandler(fh)
        logger.addHandler(ch)

    return logger
