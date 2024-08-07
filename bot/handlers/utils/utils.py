from bot.handlers.common import calculate_expression, get_user_info, handle_error_command
from telegram import Update
from telegram.ext import ContextTypes
from bot.logging_config import logger, logging

logger = logging.getLogger(__name__)

async def calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_info = get_user_info(user_id=user_id)
    if len(context.args) == 0:
        text = "You have give me something to calculate, {name}".format(name=user_info["username"])
        
    expression = ' '.join(context.args)
    result = calculate_expression(expression)
    if result is None:
        await handle_error_command(update, context)
        return
    
    text = "Ans = {result}".format(expression=expression, result = result)
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)