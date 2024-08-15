from bot.handlers.common import calculate_expression, get_user_info, handle_error_command
from telegram import Update
from telegram.ext import ContextTypes
from bot.logging_config import logger, logging
import requests
import hashlib
from datetime import datetime
from dotenv import load_dotenv
import os
import re

load_dotenv()

logger = logging.getLogger(__name__)


def parse_input(input_str: str):
    # Split the input string into parts
    parts = input_str.split()

    # Find where the msisdns end and the message begins
    msisdns = []
    message_parts = []
    masking = None
    messageType = None

    for part in parts:
        if re.match(r'^01\d{9}$', part):  # Assuming Bangladeshi numbers
            msisdns.append(part)
        elif part.startswith('[') and part.endswith(']'):
            # Extract options inside the brackets
            options = part.strip('[]').split(',')
            for option in options:
                key, value = option.split('=')
                if key.strip() == 'masking':
                    masking = int(value.strip())
                elif key.strip() == 'messageType':
                    messageType = int(value.strip())
        else:
            message_parts.append(part)

    # Join the remaining parts to form the message
    message = " ".join(message_parts)

    if masking is None:
        masking = 1
    if messageType is None:
        messageType = 3
        
    return {
        "msisdns": msisdns,
        "message": message,
        "masking": masking,
        "messageType": messageType
    }
    
def generate_token(channel: str) -> str:
    # Get the current date and format it as ddmmyyyy
    now = datetime.now()
    formatted_date = now.strftime("%d%m%Y")

    # Create the string to be hashed
    string_to_hash = f"{channel}:{formatted_date}"

    # Compute the MD5 hash
    hash_object = hashlib.md5(string_to_hash.encode())
    token = hash_object.hexdigest()
    
    return token

def send_sms(msisdn: list, message: str, masking: int, messageType: int, channel: str = "vts") -> dict:
    # Generate the token
    token = generate_token(channel)

    # Define the API URL
    url = os.getenv('CMP_URL')

    # Create the headers
    headers = {
        'channel': channel,
        'token': token,
        'Content-Type': 'application/json'
    }

    # Create the data payload
    payload = {
        "msisdn": msisdn,
        "message": message,
        "masking": masking,
        "messageType": messageType
    }

    # Make the POST request
    response = requests.post(url, json=payload, headers=headers)

    # Return the response as a dictionary
    return response.json()


async def calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_info = get_user_info(user_id=user_id)
    if len(context.args) == 0:
        text = "You have to give me something to calculate, {name}".format(name=user_info["username"])
        
    expression = ' '.join(context.args)
    result = calculate_expression(expression)
    if result is None:
        await handle_error_command(update, context)
        return
    
    text = "Ans = {result}".format(expression=expression, result = result)
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    

async def sms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_info = get_user_info(user_id=user_id)
    
    if user_info["user_id"] != 6250006519:
        text = "You are not authorized"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        return
    
    if len(context.args) < 2:
        text = "This is not a valid command"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        return
    
    command = ' '.join(context.args)
    
    parsed = parse_input(command)
    response = send_sms(msisdn=parsed["msisdns"], message=parsed["message"], masking=parsed["masking"], messageType=parsed["messageType"])
    
    if response["data"]["statusCode"] == 200:
        text = f"Successfully sent the message: '{parsed['message']}' to the number(s): {' '.join(parsed["msisdns"])}"
    else:
        text = "Failed to send SMS"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
