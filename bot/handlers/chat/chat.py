from telegram.ext import ContextTypes
from telegram import Update
from bot.logging_config import logger, logging
from bot.response.response import generate_response
from bot.handlers.common import get_user_info

logger = logging.getLogger(__name__)


async def mention(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_info = get_user_info(user_id=user_id)
    chat_text = update.message.text
    if "@TabaqBillBot" in chat_text:
        prompt = f"{user_info["username"]} who has a balance of {user_info["balance"]} Tk. sent you this message: {chat_text}. Reply accordingly"
        response = generate_response(prompt)
        await update.message.reply_text(response)