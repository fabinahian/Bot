from bot.handlers.common import get_user_info, handle_error_command, get_GMT6_time
from bot.handlers.common import getStringAndNumber
from bot.database.utils import insert_transaction_and_update_balance, update_transaction_and_balance, distribute_payment, distribute_payment_between_users
from telegram import Update
from telegram.ext import ContextTypes
from bot.logging_config import logger, logging
from datetime import datetime
import random

logger = logging.getLogger(__name__)

    
async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        time = datetime.now()
        time = get_GMT6_time(time)
        item, bill = getStringAndNumber(context.args)
        bill = round(bill, 2)
        
        none_item = False
        if len(item) == 0:
            none_item = True
            toss = random.randint(0, 2)
            if toss == 0:
                item = "God knows what"
            elif toss == 1:
                item = "Something illegal"
            elif toss == 2:
                item = "Something embarrassing"
                
        # print(item, bill)
        user_id = update.message.from_user.id
        user_info = get_user_info(user_id=user_id)
        user_info["balance"] -= bill
        insert_transaction_and_update_balance(user_id=user_id, item=item, 
                                              transaction_type="pay", amount=bill)
        text = f"You paid {bill} Tk. for {item}. Your balance is {user_info["balance"]}"
        
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    
    except Exception as e:
        logging.error(e)
        await handle_error_command(update, context)
        
        
async def transfer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.message.from_user.id
        user_info = get_user_info(user_id=user_id)
        member, amount = getStringAndNumber(context.args)
        none_item = False
        if len(member) == 0:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="You can't transfer to yourself {name}".format(name = user_info["username"]))
            return
        
        member_info = get_user_info(user_name=member)
        if member_info is None:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="I don't know this guy 😕".format(name = user_info["username"]))
            return
        if user_info["balance"] - amount < 0:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="You don't have enough balance to transfer, {name} 😕".format(name = user_info["username"]))
            return
        
        
        
        insert_transaction_and_update_balance(user_id=user_info["user_id"], item=member_info["username"], transaction_type="debit", amount=amount)
        insert_transaction_and_update_balance(user_id=member_info["user_id"], item=user_info["username"], transaction_type="credit", amount=amount)
        
        user_info = get_user_info(user_id=user_id)
        member_info = get_user_info(user_id=member_info["user_id"])
        
        await context.bot.send_message(chat_id=update.effective_chat.id, 
                                       text="That's what friends are for 🤗. {name1} transferred {amount} Tk. to {name2}'s account. Here's your balance now {name1}: {balance1} Tk.".format(name1 = user_info["username"],
                                                                                                                                                                                            name2 = member_info["username"],
                                                                                                                                                                                            amount = amount,
                                                                                                                                                                                            balance1 = user_info["balance"]))
        
    
    except Exception as e:
        logging.error(e)
        await handle_error_command(update, context)



async def addfund(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.message.from_user.id
        user_info = get_user_info(user_id=user_id)
        
        if user_info["admin"] == False:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="You can't add fund {}. You're not an admin".format(user_info["username"]))
            return
        else:
            member_name, amount = getStringAndNumber(context.args)
            logger.debug(member_name)
            if len(member_name) == 0:
                member_name = user_info["username"]
        
        member_info = get_user_info(user_name=member_name) 

        if member_info["usergroup"] != update.message.chat.title:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="You can't add fund for {name}. They are from a different group".format(name = member_info["username"]))
            return
        
        insert_transaction_and_update_balance(user_id=member_info["user_id"], item="", transaction_type="addfund", amount=amount)

    except Exception as e:
        logging.error(e)
        await handle_error_command(update, context)
        

async def editamount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        tx_id, bill = context.args[0], float(context.args[1])                
        # print(tx_id, bill)
        user_id = update.message.from_user.id
        user_info = get_user_info(user_id=user_id)
        
        user_info = update_transaction_and_balance(tx_id=tx_id, new_amount=bill)
        
        text="Here you go {}, fixed it. Now your balance is {} Tk.".format(user_info["username"], user_info["balance"])
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        
    except Exception as e:
        logging.error(e)
        await handle_error_command(update, context)
        
        
async def edititem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        tx_id, item = context.args[0], str(context.args[1])
        user_id = update.message.from_user.id
        user_info = get_user_info(user_id=user_id)
        
        user_info = update_transaction_and_balance(tx_id=tx_id, item=item)
        
        text="Here you go {}, fixed it.".format(user_info["username"])
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        
    except Exception as e:
        logging.error(e)
        await handle_error_command(update, context)


async def distribute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.message.from_user.id
        user_info = get_user_info(user_id=user_id)
        
        if(len(context.args) == 0):
            raise ValueError("Invalid argument passed")
        
        item, total_amount = getStringAndNumber(context.args[:2])
        
        if(len(context.args) > 2):
            usernames = context.args[2:]
            amount_distributed = distribute_payment_between_users(usernames=usernames, total_amount=total_amount, item=item)
            text=f"{amount_distributed} Tk. ditributed between {str(usernames)}"
        else:
            amount_distributed = distribute_payment(usergroup=user_info["usergroup"], total_amount=total_amount, item=item)
            text=f"{amount_distributed} Tk. ditributed between all users of the group {user_info["usergroup"]}"
            
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
        
    except Exception as e:
        logging.error(e)
        await handle_error_command(update, context)