from bot.main import start_bot
from bot.logging_config import logger, logging
from bot.database.database import init_db

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Initializing the database...")
    # Initialize the database and create tables if they don't exist
    init_db()
    
    logger.info("Database initialized successfully.")
    logger.info("Starting bot...")
    
    # Start the bot after the database is initialized
    start_bot()
