from telegram.ext import ContextTypes
from telegram import Update, constants
from bot.logging_config import logger, logging
from bot.response.response import generate_response
from bot.handlers.common import get_user_info
from bot.response.system_settings import GPT_Settings

logger = logging.getLogger(__name__)


async def mention(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_info = get_user_info(user_id=user_id)
    chat_text = update.message.text
    settings = GPT_Settings()
    settings.system["content"] = """You are TabaqBillBot. You are sarcastic and funny and like to make dark jokes.
                                    If someone sends you a message, you reply accordilngly. Keep it interesting"""

    if update.message.chat.type == constants.ChatType.GROUP and f"@{context.bot.username}" in chat_text:
        prompt = chat_text
        response = generate_response(prompt, settings=settings)
        await update.message.reply_text(response)
    elif update.message.chat.type == constants.ChatType.PRIVATE:
        prompt = chat_text
        response = generate_response(prompt, settings=settings)
        await context.bot.send_message(chat_id = update.effective_chat.id, text = response)