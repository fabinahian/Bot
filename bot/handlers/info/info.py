import os
from bot.handlers.common import get_user_info, COMMANDS
from bot.database.utils import create_user, update_username, get_usernames_by_usergroup
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


async def setname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_info = get_user_info(user_id=user_id)
    new_name = ' '.join(context.args)
    
    if len(context.args) == 0:
        logger.error("No arguments passed for name")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Oh come on {}! You gotta give me a name.".format(user_info["username"]))
        return
    
    logger.info(f"User changed their name from {user_info["username"]} to {new_name}")
    update_username(user_id=user_info["user_id"], new_username=new_name)
    
    text = "I'm so glad you changed your name {}, previous one sucked".format(new_name)
            
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    

async def showmembers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_info = get_user_info(user_id=user_id)
    users = get_usernames_by_usergroup(usergroup=user_info["usergroup"])
    if(len(users) == 0):
        logger.error("No users found")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Too bad, no one is in your group :(")
        return
    
    users = sorted(users, key=lambda x:x["balance"], reverse=True)
    logger.info(users)
    text = ""
    count = 1
    for user in users:
        text += "{}. {}".format(count, user['username'])
        count += 1
        if user["admin"] == 1:
            text += " (Admin)"
        text += "\n"

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    
    
async def help_command(update, context):
    help_message = "Available commands:\n"
    help_message += '\n'.join(COMMANDS)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=help_message)
    