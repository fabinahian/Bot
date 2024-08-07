import os
import logging.config
from logging.handlers import RotatingFileHandler
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
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": log_path,
            "formatter": "default",
            "maxBytes": 1024 * 1024 * 5,  # 5 MB
            "backupCount": 5,
        }
    },
    "loggers": {
        "": {  # root logger
            "level": "DEBUG" if os.getenv("DEBUG", "True") == "True" else "INFO",
            "handlers": ["console", "file"],
        }
    },
}

logging.config.dictConfig(LOGGING_CONFIG)

logger = logging.getLogger(__name__)
