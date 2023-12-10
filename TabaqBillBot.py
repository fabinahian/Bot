import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import sqlite3
import os
import datetime
import random
import uuid

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
    "/setname name: Set what the bot will call you",
    "/editamount txId correct_amount: Change the amount for txId",
    "/edititem txId correct_item: Change the item for txId",
    "/help: Show this message"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    name = update.message.from_user.first_name
    if name is None:
        name = update.message.from_user.last_name
    if name is None:
        name = update.message.from_user.username
    
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    existing_value = cursor.fetchone()
    
    if existing_value:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello again {}! You're already a member, so no need to \"start\"".format(name))
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome {}! You're now a member".format(name))
        cursor.execute("INSERT INTO users (user_id, username) VALUES (?, ?)", (user_id, name))
        conn.commit()
        
    conn.close()
    
async def setname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    user_id = update.message.from_user.id
    # print(context.args)
    new_name = ' '.join(context.args)
    print(new_name)
    
    cursor.execute("select username from users where user_id = ?", (user_id,))
    old_name = cursor.fetchone()[0]
    
    if len(context.args) == 0:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Oh come on {}! You gotta give me a name.".format(old_name))
        conn.commit()
        conn.close()
        return
    
    cursor.execute("UPDATE users SET username = ? WHERE user_id = ?", (new_name, user_id))
    
    conn.commit()
    conn.close()
    
    text = ""
    if "heisenberg" in new_name.lower():
        text = "You: Say my name\n\nMe: {}\n\nYou: You're Goddamn right".format(new_name)
    elif "john cena" in new_name.lower():
        text = "Oh no! I can't see you"
    elif "john" in new_name.lower():
        text = "You know nothing John Snow"
    elif "queen" in new_name.lower():
        toss = random.randint(0,1)
        if toss == 0:
            text = "Hello, Your Majesty. I am delighted to meet you"
        elif toss == 1:
            text = "Mamaa Oooooo"
    elif "princess consuela banana hammock" in new_name.lower():
        text = "Okay so now I'm gonna call myself Crap Bag"
    else:
        toss = random.randint(0,3)
        if toss == 0:
            text = "Me: Your Honour, my client has decided to change their name to {}, because it's a cool name.\n\nJudge: Ah yes, it is a cool name. Motion granted!".format(new_name)
        elif toss == 1:
            text = "You're also gonna need a new passport {}. Don't worry, I'll arrange that too".format(new_name)
        elif toss == 2:
            text = "Hello {}!".format(new_name)
        elif toss == 3:
            text = "I'm so glad you changed your name {}, previous one sucked".format(new_name)
            
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    

# Define the /addfund command
async def addfund(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Extract the amount from the command
        amount = float(context.args[0])

        # Update user's balance
        user_id = update.message.from_user.id
        
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        
        # Update user's balance in the database
        cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))

        # Generate a unique transaction ID (TxID)
        tx_id = str(uuid.uuid4())[:8]
        
        # Insert a record in the transactions table
        cursor.execute("INSERT INTO transactions (user_id, tx_id, transaction_type, amount) VALUES (?, ?, 'addfund', ?)", (user_id, tx_id, amount))

        cursor.execute("select balance from users where user_id = ?", (user_id,))
        bl = cursor.fetchone()[0]
        
        cursor.execute("select username from users where user_id = ?", (user_id,))
        name = cursor.fetchone()[0]
        
        conn.commit()
        conn.close()

        if amount > 2000:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Oh my god {}! You almost bought the cafe! Here's your balance rich guy: {} Tk".format(name, bl))
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Congratulations {}! You've added {} Tk to your account. You're current balance is {} Tk.".format(name, amount, bl))

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
    
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Generate a unique transaction ID (TxID)
        tx_id = str(uuid.uuid4())[:8]
        cursor.execute("INSERT INTO transactions (user_id, tx_id, transaction_type, item, amount) VALUES (?, ?, 'pay', ?, ?)", (user_id, tx_id, item, bill))
        cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (bill, user_id))
        cursor.execute("select balance from users where user_id = ?", (user_id,))
        bl = cursor.fetchone()[0]
        cursor.execute("select username from users where user_id = ?", (user_id,))
        name = cursor.fetchone()[0]
        
        conn.commit()
        conn.close()
        
        if none_item:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="So not gonna tell me what you had, huh? Okay {}, here's your balance: {} Tk.".format(name, bl))
        elif bl <= 0:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Hey {}! You paid {} Tk. for {}. You ran out of fund! Your current balance is {} Tk.".format(name, bill, item, bl))
        elif bl < 50:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Hey {}! You paid {} Tk. for {}. You're almost running out of fund! Your current balance is {} Tk.".format(name, bill, item, bl))
        else:        
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Hey {}! You paid {} Tk. for {}. Your current balance is {} Tk.".format(name, bill, item, bl))
        
    except (IndexError, ValueError):
        handle_error_command(update, context)


async def editamount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        tx_id, bill = context.args[0], float(context.args[1])                
        # print(tx_id, bill)
        user_id = update.message.from_user.id
    
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        cursor.execute("select amount, transaction_type from transactions where tx_id like ?", (f'{tx_id}%',))
        # Fetch all rows
        rows = cursor.fetchall()
        # Get the column names
        columns = [description[0] for description in cursor.description]

        # Convert rows to a list of dictionaries
        table_data = [dict(zip(columns, row)) for row in rows]
        
        old_amount = table_data[0]["amount"]
        item = table_data[0]["transaction_type"]
        
        if item == "pay":
            diff = old_amount - bill
        else:
            diff = bill - old_amount
        
        cursor.execute("UPDATE transactions SET amount = ? where tx_id like ?", (bill, f'{tx_id}%'))
        cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (diff, user_id))
        cursor.execute("select balance from users where user_id = ?", (user_id,))
        bl = cursor.fetchone()[0]
        cursor.execute("select username from users where user_id = ?", (user_id,))
        name = cursor.fetchone()[0]
        
        conn.commit()
        conn.close()
        
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Here you go {}, fixed it. Now your balance is {} Tk.".format(name, bl))
        
    except (IndexError, ValueError):
        handle_error_command(update, context)

async def edititem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        tx_id, item = context.args[0], ' '.join(context.args[1:])             
        print(tx_id, item)
        user_id = update.message.from_user.id
    
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        cursor.execute("UPDATE transactions SET item = ? where tx_id like ?", (item, f'{tx_id}%'))

        cursor.execute("select username from users where user_id = ?", (user_id,))
        name = cursor.fetchone()[0]
        
        conn.commit()
        conn.close()
        
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Here you go {}, fixed it. That day you had {}".format(name, item))
        
    except (IndexError, ValueError):
        handle_error_command(update, context)
        
# Define the /balance command
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    cursor.execute("select balance from users where user_id = ?", (user_id,))
    bl = cursor.fetchone()[0]
    
    cursor.execute("select username from users where user_id = ?", (user_id,))
    name = cursor.fetchone()[0]
    
    conn.commit()
    conn.close()
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hey {}! You're current balance is {} Tk. Have a great day!".format(name, bl))

# Define the /history command
async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    cursor.execute("select username from users where user_id = ?", (user_id,))
    name = cursor.fetchone()[0]
        
    if len(context.args) == 1 and context.args[0].isnumeric():
        cursor.execute("select * from transactions where user_id = ? order by timestamp desc limit ?", (user_id, int(context.args[0])))
    elif len(context.args) == 0:
        cursor.execute("select * from transactions where user_id = ? order by timestamp desc limit 10", (user_id,))
    else:
        conn.commit()
        conn.close()
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Oops! {} made an error in command".format(name))
        return
    
    # Fetch all rows
    rows = cursor.fetchall()
    # Get the column names
    columns = [description[0] for description in cursor.description]

    # Convert rows to a list of dictionaries
    table_data = [dict(zip(columns, row)) for row in rows]
    
    text = "Good day {}! Here's your transaction history:\n\n".format(name)
    
    for row in table_data:
        if row["transaction_type"] == "pay":
            text += "- On {}, you paid {} Tk. for {}. TxID: {}\n".format(row["timestamp"], row["amount"], row["item"], row["tx_id"])
        else:
            text += "- On {}, you added {} Tk. to your fund. TxID: {}\n".format(row["timestamp"], row["amount"], row["tx_id"])
    
    cursor.execute("select balance from users where user_id = ?", (user_id,))
    bl = cursor.fetchone()[0]
    
    text += "\nYour current balance is {} Tk.".format(bl)
    
    conn.commit()
    conn.close()

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

# Define a function to handle incoming messages
async def handle_error_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("select username from users where user_id = ?", (user_id,))
    name = cursor.fetchone()[0]
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Oops! That's not a valid command {}".format(name))

# Define the /help command
async def help_command(update, context):
    help_message = "Available commands:\n"
    help_message += '\n'.join(COMMANDS)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=help_message)
    
def main():
    application = ApplicationBuilder().token(token).build()
    
    start_handler = CommandHandler("start", start)
    setname_handler = CommandHandler("setname", setname)
    balance_handler = CommandHandler('balance', balance)
    pay_handler = CommandHandler('pay', pay)
    history_handler = CommandHandler('history', history)
    addfund_handler = CommandHandler('addfund', addfund)
    editamount_handler = CommandHandler('editamount', editamount)
    edititem_handler = CommandHandler('edititem', edititem)
    help_handler = CommandHandler('help', help_command)
    
    application.add_handler(start_handler)
    application.add_handler(setname_handler)
    application.add_handler(pay_handler)
    application.add_handler(balance_handler)
    application.add_handler(history_handler)
    application.add_handler(addfund_handler)
    application.add_handler(editamount_handler)
    application.add_handler(edititem_handler)
    application.add_handler(help_handler)
    
    application.run_polling()

if __name__ == "__main__":
    # Connect to the SQLite database
    conn = sqlite3.connect('Tabaq.db')
    cursor = conn.cursor()

    # Create tables if they don't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            user_id INTEGER UNIQUE NOT NULL,
            username TEXT,
            balance REAL DEFAULT 0.0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            tx_id TEXT UNIQUE NOT NULL,
            transaction_type TEXT NOT NULL,
            item TEXT,
            amount REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    main()
