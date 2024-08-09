from bot.handlers.common import get_user_info, handle_error_command, get_GMT6_time
from bot.handlers.common import getStringAndNumber
from bot.database.utils import get_usernames_by_usergroup, get_last_n_transactions, get_session_summary
from bot.response.response import generate_response
from telegram import Update
from telegram.ext import ContextTypes
from bot.logging_config import logger, logging
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)



async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_info = get_user_info(user_id=user_id)
    
    prompt = f"{user_info["username"]} asked to see their balance. Their balance is {user_info["balance"]} Tk."
    response = generate_response(prompt)
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response)
    
async def allbalance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_info = get_user_info(user_id=user_id)
    users = get_usernames_by_usergroup(usergroup=user_info["usergroup"])
    if(len(users) == 0):
        logger.error("No users found")
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Too bad, no one is in your group :(")
        return

    users = sorted(users, key=lambda x:x["balance"], reverse=True)
    text = ""
    count = 1
    fund = 0
    total = len(users)
    for user in users:
        fund += user["balance"]
        text += "{}. {}".format(count, user["username"])
        if count == 1:
            text += " 👑 "
        if count == total and count != 1:
            text += " 😞 "
        count += 1
        if user["admin"] == 1:
            text += " (Admin)"
        text += ":{} Tk.".format(user["balance"])
        text += "\n"
    text += "\nTotal amount in the fund: {} Tk.".format(fund)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    

async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.message.from_user.id
        user_info = get_user_info(user_id=user_id)
        if len(context.args) == 1 and context.args[0].isnumeric():
            n = int(context.args[0])
        else:
            n = 10
        history = get_last_n_transactions(user_id=user_id, n=n)
        
        text = "Good day {}! Here's your transaction history:\n\n".format(user_info["username"])
        
        for h in history:
            if h["transaction_type"] == "pay":
                text += "- On {}, you paid {} Tk. for {}. TxID: {}\n".format(h["timestamp"], h["amount"], h["item"], h["tx_id"])
            elif h["transaction_type"] == "pay":
                text += "- On {}, you added {} Tk. to your fund. TxID: {}\n".format(h["timestamp"], h["amount"], h["tx_id"])
            elif h["transaction_type"] == "credit":
                text += "- On {}, {} Tk. was transferred to your fund from {}. TxID: {}\n".format(h["timestamp"], h["amount"], h["item"], h["tx_id"])
            elif h["transaction_type"] == "debit":
                text += "- On {}, you transferred {} Tk. to {}. TxID: {}\n".format(h["timestamp"], h["amount"], h["item"], h["tx_id"])
                
        
        text += "\nYour current balance is {} Tk.".format(user_info["balance"])
       

        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        
    except Exception as e:
        logging.error(e)
        await handle_error_command(update, context)
        
        
async def session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.message.from_user.id
        user_info = get_user_info(user_id=user_id)
        if len(context.args) == 0:
            hour = 1
            end_timestamp = datetime.now()
            start_timestamp = end_timestamp - timedelta(hours=hour)
        elif len(context.args) == 1:
            hour = float(context.args[0])
            end_timestamp = datetime.now()
            start_timestamp = end_timestamp - timedelta(hours=hour)
        elif len(context.args) == 2:
            start_timestamp_str, end_timestamp_str = context.args
            try:
                start_timestamp = datetime.fromisoformat(start_timestamp_str)
                end_timestamp = datetime.fromisoformat(end_timestamp_str)
                start_timestamp = str(start_timestamp)
                end_timestamp = str(end_timestamp)
            except ValueError:
                raise ValueError("Start and end times must be in ISO format (YYYY-MM-DDTHH:MM:SS)")
        else:
            raise ValueError("Invalid arguments")
            
        transactions = get_session_summary(usergroup=user_info["usergroup"], start_time=start_timestamp, end_time=end_timestamp)
        summary = {
            "addfund":0,
            "pay":0,
            "debit":0,
            "credit":0
        }
        
        text = f"From {start_timestamp} to {end_timestamp}:\n"
        
        for t in transactions:
            user_info = get_user_info(user_id=t["user_id"])
            name = user_info["username"]
            if t["transaction_type"] == 'pay':
                summary["pay"] += t["amount"]
                text += "- {name} paid {amount} Tk. for {item} at {time}\n".format(name = name, item = t["item"], time = t["timestamp"], amount = t["amount"])
            elif t["transaction_type"] == 'addfund':
                summary["addfund"] += t["amount"]
                text += "- {name} added {amount} Tk. at {time}\n".format(name = name, item = t["item"], time = t["timestamp"], amount = t["amount"])
            elif t["transaction_type"] == 'credit':
                summary["credit"] += t["amount"]
                text += f"- {t['item']} sent {t['amount']} Tk. to {user_info['username']} at {t['timestamp']}\n"
            elif t["transaction_type"] == 'debit':
                summary["debit"] += t["amount"]
                text += f"- {user_info['username']} sent {t['amount']} Tk. to {t['item']} at {t['timestamp']}\n"
        
        text += "\nIn this session:"
        text += "\nTotal added: {amount} Tk.".format(amount = round(summary['addfund'], 2))
        text += "\nTotal paid: {amount} Tk.".format(amount = round(summary['pay'], 2))
        text += "\nTotal transferred: {amount} Tk.".format(amount = round(summary['debit'], 2))
        text += "\nBalance: {amount} Tk.".format(amount = round(summary['pay'] - summary['addfund'], 2))

        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    
    except Exception as e:
        logging.error(e)
        await handle_error_command(update, context)