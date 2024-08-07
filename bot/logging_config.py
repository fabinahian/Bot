import os
import logging.config
from dotenv import load_dotenv

load_dotenv()

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

log_directory = os.path.join(project_root, "logs")
log_path = os.path.join(log_directory, "bot.log")

# Create the log directory if it doesn't exist
os.makedirs(log_directory, exist_ok=True)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,  # This ensures that existing loggers are not disabled
    "formatters": {
        "default": {
            "format": "[%(asctime)s] [%(levelname)s | %(name)s] (%(module)s) %(message)s",
        },
        "uvicorn": {
            "format": "[%(asctime)s] [%(levelname)s | %(name)s] %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": log_path,
            "formatter": "default",
        },
        "uvicorn_file": {
            "class": "logging.FileHandler",
            "filename": log_path,
            "formatter": "uvicorn",
        },
    },
    "loggers": {
        "": {  # root logger
            "level": "DEBUG" if os.getenv("DEBUG", "True") == "True" else "INFO",
            "handlers": ["console", "file"],
        },
        "uvicorn": {
            "level": "DEBUG" if os.getenv("DEBUG", "True") == "True" else "INFO",
            "handlers": ["console", "uvicorn_file"],
            "propagate": False,
        },
        "uvicorn.access": {
            "level": "DEBUG" if os.getenv("DEBUG", "True") == "True" else "INFO",
            "handlers": ["console", "uvicorn_file"],
            "propagate": False,
        },
    },
}

logging.config.dictConfig(LOGGING_CONFIG)

logger = logging.getLogger(__name__)
