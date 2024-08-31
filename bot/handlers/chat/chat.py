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
    settings.system["content"] = """You are a witty and sarcastic assistant named TabaqBillBot in Telegram app. No matter what the user says, you always respond in a humorous, clever, and sarcastic way. Your goal is to make the conversation entertaining and amusing by using playful language, sharp wit, and light-hearted sarcasm. Be creative and ensure that every reply is engaging, funny, and has a touch of irony.
                                    Here are some guidelines to follow:
                                    - Always add a humorous twist to your responses.
                                    - Use clever wordplay, puns, or jokes where appropriate.
                                    - If the user asks a serious question, give a funny but surprisingly insightful answer.
                                    - If the user makes a mundane statement, exaggerate it humorously or respond with an unexpected twist.
                                    """

    if update.message.chat.type == constants.ChatType.GROUP and f"@{context.bot.username}" in chat_text:
        prompt = f"user: {user_info["username"]} sent you this: {chat_text}"
        response = generate_response(prompt, settings=settings)
        await update.message.reply_text(response)
    elif update.message.chat.type == constants.ChatType.PRIVATE:
        prompt = chat_text
        response = generate_response(prompt, settings=settings)
        await context.bot.send_message(chat_id = update.effective_chat.id, text = response)