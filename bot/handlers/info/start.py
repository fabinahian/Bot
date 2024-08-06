from bot.handlers.common import get_user_info
from bot.database.utils import create_user
from telegram import Update
from telegram.ext import ContextTypes
from bot.logging_config import logger, logging


logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_info = get_user_info(user_id=user_id)
    logger.info(f"User info from user id {user_id}:{user_info}")
    if(user_info is not None):
        logger.info("User is found, sending confirmation message")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello again {}! You're already a member, so no need to \"start\"".format(user_info["username"]))
        return
    
    user_group = update.message.chat.title
    name = update.message.from_user.first_name
    admin_status = 0
    
    if name is None:
        name = update.message.from_user.last_name
    if name is None:
        name = update.message.from_user.username
    if user_group is None:
        user_group = user_id
        admin_status = 1

    logger.info(f"New user info:\nusername:{name},\nusergroup:{user_group},\nadmin:{admin_status}")
    try:
        create_user(user_id=user_id,
                    username=name,
                    usergroup=user_group,
                    admin=admin_status,
                    balance=0)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome {}! You're now a member".format(name))
    except Exception as e:
        logger.error(f"Exception occured trying to create user. {e}")