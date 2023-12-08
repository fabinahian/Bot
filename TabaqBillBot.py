import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import sqlite3
import os
import datetime

db_file = 'Tabaq.db'
token = '6443735527:AAH-62niLYpw7z6VRSyz3IQkFNV9xB_sWhY'

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Command descriptions
COMMANDS = [
    "/start: Add yourself to the database (if not already added)",
    "/addfund amount: Add funds to your balance",
    "/pay item payment: Make a payment and subtract the bill from your balance",
    "/balance: Show your current balance",
    "/history N: Show the last N statements of your account. If nothing is passed then last 10 statements is shown",
    "/help: Show this message"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    first_name = update.message.from_user.first_name
    last_name = update.message.from_user.last_name
    
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    existing_value = cursor.fetchone()
    
    if existing_value:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello again {}! You're already a member, so no need to \"start\"".format(last_name))
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome {}! You're now a member".format(last_name))
        cursor.execute("INSERT INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
        conn.commit()
        
    conn.close()

# Define the /addfund command
async def addfund(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Extract the amount from the command
        amount = float(context.args[0])

        # Update user's balance
        user_id = update.message.from_user.id
        last_name = update.message.from_user.last_name
        
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Update user's balance in the database
        cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))

        # Insert a record in the transactions table
        cursor.execute("INSERT INTO transactions (user_id, transaction_type, amount) VALUES (?, 'addfund', ?)", (user_id, amount))

        cursor.execute("select balance from users where user_id = ?", (user_id,))
        bl = cursor.fetchone()[0]
        conn.commit()
        conn.close()

        if amount > 2000:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Oh my god {}! You almost bought the cafe! Here's your balance rich guy: {} Tk".format(last_name, bl))
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Congratulations {}! You've added {} Tk to your account. You're current balance is {} Tk.".format(last_name, amount, bl))

    except (IndexError, ValueError):
        handle_error_command(update, context)


def getItemAndBill(args:list):
    item = ""
    for x in args:
        if x[0] >= '0' and x[0] <= '9':
            bill = float(x)
        else:
            item += x + " "
    return item[:-1], bill

# Define the /pay command
async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        item, bill = getItemAndBill(context.args)
        print(item, bill)
        user_id = update.message.from_user.id
        last_name = update.message.from_user.last_name
        
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        cursor.execute("INSERT INTO transactions (user_id, transaction_type, item, amount) VALUES (?, 'pay', ?, ?)", (user_id, item, bill))
        cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (bill, user_id))
        cursor.execute("select balance from users where user_id = ?", (user_id,))
        bl = cursor.fetchone()[0]
        
        conn.commit()
        conn.close()
        
        if bl <= 0:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Hey {}! You paid {} Tk. for {}. You ran out of fund! Your current balance is {} Tk.".format(last_name, bill, item, bl))
        elif bl < 50:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Hey {}! You paid {} Tk. for {}. You're almost running out of fund! Your current balance is {} Tk.".format(last_name, bill, item, bl))
        else:        
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Hey {}! You paid {} Tk. for {}. Your current balance is {} Tk.".format(last_name, bill, item, bl))
        
    except (IndexError, ValueError):
        handle_error_command(update, context)

# Define the /balance command
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    last_name = update.message.from_user.last_name
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    cursor.execute("select balance from users where user_id = ?", (user_id,))
    bl = cursor.fetchone()[0]
    
    conn.commit()
    conn.close()
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hey {}! You're current balance is {} Tk. Have a great day!".format(last_name, bl))

# Define the /history command
async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    last_name = update.message.from_user.last_name
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    if len(context.args) == 1 and context.args[0].isnumeric():
        cursor.execute("select * from transactions where user_id = ? order by timestamp desc limit ?", (user_id, int(context.args[0])))
    elif len(context.args) == 0:
        cursor.execute("select * from transactions where user_id = ? order by timestamp desc limit 10", (user_id,))
    else:
        conn.commit()
        conn.close()
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Oops! {} made an error in command".format(last_name))
        return
    
    # Fetch all rows
    rows = cursor.fetchall()
    # Get the column names
    columns = [description[0] for description in cursor.description]

    # Convert rows to a list of dictionaries
    table_data = [dict(zip(columns, row)) for row in rows]
    
    text = "Good day {}! Here's your transaction history:\n\n".format(last_name)
    
    for row in table_data:
        if row["transaction_type"] == "pay":
            text += "- On {}, you paid {} Tk. for {}\n".format(row["timestamp"], row["amount"], row["item"])
        else:
            text += "- On {}, you added {} Tk. to your fund\n".format(row["timestamp"], row["amount"])
    
    cursor.execute("select balance from users where user_id = ?", (user_id,))
    bl = cursor.fetchone()[0]
    
    text += "\nYour current balance is {} Tk.".format(bl)
    
    conn.commit()
    conn.close()

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

# Define a function to handle incoming messages
async def handle_error_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    last_name = update.message.from_user.last_name
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Oops! That's not a valid command {}".format(last_name))

# Define the /help command
async def help_command(update, context):
    help_message = "Available commands:\n"
    help_message += '\n'.join(COMMANDS)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=help_message)
    
def main():
    application = ApplicationBuilder().token(token).build()
    
    start_handler = CommandHandler("start", start)
    balance_handler = CommandHandler('balance', balance)
    pay_handler = CommandHandler('pay', pay)
    history_handler = CommandHandler('history', history)
    addfund_handler = CommandHandler('addfund', addfund)
    help_handler = CommandHandler('help', help_command)
    
    application.add_handler(start_handler)
    application.add_handler(pay_handler)
    application.add_handler(balance_handler)
    application.add_handler(history_handler)
    application.add_handler(addfund_handler)
    application.add_handler(help_handler)
    
    application.run_polling()

if __name__ == "__main__":
    main()
