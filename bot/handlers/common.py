import ast
import re
import os
from datetime import datetime, timedelta
from bot.database.utils import get_user_by_username, get_user_by_user_id, get_user_by_tx_id
from telegram import Update
from telegram.ext import ContextTypes
from bot.logging_config import logger, logging


logger = logging.getLogger(__name__)

COMMANDS = [
    "/start: Add yourself to the database (if not already added)",
    "/addfund [amount]: Add funds to your balance",
    "/pay [item] [payment]: Make a payment and subtract the bill from your balance",
    "/balance: Show your current balance",
    "/history [N]: Show the last N statements of your account. If nothing is passed then last 10 statements is shown",
    "/session [h]: Show the transaction summary of last N hour. If nothing is passed then shows last 1 hour",
    "/setname [name]: Set what the bot will call you",
    "/editamount [txId] [correct_amount]: Change the amount for txId",
    "/edititem [txId] [correct_item]: Change the item for txId",
    "/showmembers: List all the members",
    "/allbalance: List balance for all members",
    "/tabaqmenu: Show Tabaq Coffe Menu",
    "/calc: Calculate an expression",
    "/help: Show this message"
]

def calculate_expression(expression):
    try:
        # Parse the expression safely
        parsed_expression = ast.parse(expression, mode='eval')
        
        # Evaluate the parsed expression
        result = eval(compile(parsed_expression, filename='<string>', mode='eval'))
        
        return result
    except Exception as e:
        logging.error(e)
        return None
    
def get_time_category(current_time:datetime)->str:

    current_time = current_time.time()
    if current_time < datetime.strptime("04:00", "%H:%M").time():
        return "Late Night"
    elif current_time < datetime.strptime("09:00", "%H:%M").time():
        return "Early Morning"
    elif current_time < datetime.strptime("12:00", "%H:%M").time():
        return "Morning"
    elif current_time < datetime.strptime("13:00", "%H:%M").time():
        return "Noon"
    elif current_time < datetime.strptime("17:00", "%H:%M").time():
        return "Afternoon"
    elif current_time < datetime.strptime("20:00", "%H:%M").time():
        return "Evening"
    else:
        return "Night"
    
def convert_units(input_str):
    # Define a regular expression pattern to identify units
    pattern = r'(\d+\.?\d*)([kKmM])'

    # Find all matches in the input string
    matches = re.findall(pattern, input_str)

    # Define a dictionary to map unit suffixes to their multipliers
    unit_multipliers = {'k': 1e3, 'K': 1e3, 'm': 1e6, 'M': 1e6}

    # Process each match and perform the conversion
    for match in matches:
        value, unit = match
        multiplier = unit_multipliers.get(unit, 1)
        converted_value = float(value) * multiplier
        input_str = input_str.replace(''.join(match), str(converted_value))

    return input_str

def get_GMT6_time(time:datetime):
    return time + timedelta(hours=6)

def find_matching_string(strings, target_substring):
    for string in strings:
        s = string.replace(".jpg", "")
        if target_substring in s or s in target_substring:
            return string
    return None

def getStringAndNumber(args:list):
    item = ""
    for x in args:
        if x[0] >= '0' and x[0] <= '9':
            bill = float(convert_units(x))
        else:
            item += x + " "
    return item[:-1], bill

def rename_file(old_filename, new_filename):
    try:
        os.rename(old_filename, new_filename)
        logging.info(f"File '{old_filename}' has been successfully renamed to '{new_filename}'.")
    except FileNotFoundError:
        logging.error(f"File '{old_filename}' not found.")
    except FileExistsError:
        logging.error(f"File '{new_filename}' already exists.")

def get_user_info(user_id = None, user_name = None, tx_id = None):
    if user_id is not None:
        logger.debug(f"User ID {user_id}")
        user_info = get_user_by_user_id(user_id=user_id)
        logger.debug(f"User Info: {user_info}")
        return user_info
    if user_name is not None:
        logger.debug(f"User Name(s) {user_id}")
        multiple_usernames = True
        if not isinstance(user_name, list):
            multiple_usernames = False
            user_name = [user_name]
        user_info = get_user_by_username(usernames=user_name)
        logger.debug(f"User Info: {user_info}")
        if multiple_usernames:
            return user_info
        return user_info[0]
    
    if tx_id is not None:
        logger.debug(f"Transaction ID {user_id}")
        user_info = get_user_by_tx_id(tx_id=tx_id)
        logger.debug(f"User Info: {user_info}")
        return user_info
    
    return None
    
    
async def handle_error_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_info = get_user_info(user_id=user_id)
    name = user_info["username"]
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Oops! That's not a valid command {}".format(name))