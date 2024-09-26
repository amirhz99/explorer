import logging
from logging.handlers import RotatingFileHandler


def config_uvicorn_logger():
    logger = logging.getLogger("uvicorn")
    logger.setLevel(logging.DEBUG)

    file_handler = RotatingFileHandler("app.log")

    file_formatter = logging.Formatter('%(asctime)s -%(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)

    logger.addHandler(file_handler)

    return logger


uvicorn_logger = config_uvicorn_logger()


def config_logger(log_file_name: str | None = 'logs'):
    stream_handler = logging.StreamHandler()

    root_logger = logging.getLogger()
    root_logger.handlers = []  # Remove any existing handlers to avoid duplication
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(stream_handler)

    if log_file_name:
        if not log_file_name.endswith('.log'):
            log_file_name += '.log'

        file_handler = logging.FileHandler(log_file_name)

        file_formatter = logging.Formatter('%(asctime)s -%(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)

        root_logger.addHandler(file_handler)
