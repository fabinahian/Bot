from bot.main import start_bot
from bot.logging_config import logger, logging

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Starting bot")
    start_bot()