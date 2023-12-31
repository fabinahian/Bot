import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import sqlite3
import os
import datetime
import random
import uuid
import BotResponse
import re
import ast



db_file = 'Tabaq.db'
token = '6443735527:AAH-62niLYpw7z6VRSyz3IQkFNV9xB_sWhY'
only_admin_add_fund = True
profile_pic_folder = os.path.join(os.getcwd(), "images", "profiles")


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Command descriptions
COMMANDS = [
    "/start: Add yourself to the database (if not already added)",
    "/addfund [amount]: Add funds to your balance",
    "/pay [item] [payment]: Make a payment and subtract the bill from your balance",
    "/balance: Show your current balance",
    "/history [N]: Show the last N statements of your account. If nothing is passed then last 10 statements is shown",
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
    
def get_time_category(current_time:datetime.datetime)->str:

    current_time = current_time.time()
    if current_time < datetime.datetime.strptime("04:00", "%H:%M").time():
        return "Late Night"
    elif current_time < datetime.datetime.strptime("09:00", "%H:%M").time():
        return "Early Morning"
    elif current_time < datetime.datetime.strptime("12:00", "%H:%M").time():
        return "Morning"
    elif current_time < datetime.datetime.strptime("13:00", "%H:%M").time():
        return "Noon"
    elif current_time < datetime.datetime.strptime("17:00", "%H:%M").time():
        return "Afternoon"
    elif current_time < datetime.datetime.strptime("20:00", "%H:%M").time():
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

def getUserInfo(user_id = None, user_name = None, tx_id = None):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    if user_id is not None:
        cursor.execute("select user_id, username, admin, usergroup, balance from users where user_id = ?", (user_id,))    

    elif user_name is not None:
        cursor.execute("select user_id, username, admin, usergroup, balance from users where username like ?", (f'{user_name}%',))
    
    elif tx_id is not None:
        cursor.execute("select user_id, username, admin, usergroup, balance from users where username like ?", (f'{tx_id}%',))
    
    # Fetch all rows
    rows = cursor.fetchall()
    # Get the column names
    columns = [description[0] for description in cursor.description]
    # Convert rows to a list of dictionaries
    user_info = [dict(zip(columns, row)) for row in rows]
    
    user_info = user_info[0]
    
    conn.commit()
    conn.close()
    
    return user_info
    
def rename_file(old_filename, new_filename):
    try:
        os.rename(old_filename, new_filename)
        logging.info(f"File '{old_filename}' has been successfully renamed to '{new_filename}'.")
    except FileNotFoundError:
        logging.error(f"File '{old_filename}' not found.")
    except FileExistsError:
        logging.error(f"File '{new_filename}' already exists.")
  
def find_matching_string(strings, target_substring):
    for string in strings:
        s = string.replace(".jpg", "")
        if target_substring in s or s in target_substring:
            return string
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    user_id = update.message.from_user.id
    
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
    
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    existing_value = cursor.fetchone()
    
    if existing_value:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Hello again {}! You're already a member, so no need to \"start\"".format(name))
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome {}! You're now a member".format(name))
        cursor.execute("INSERT INTO users (user_id, username, usergroup, admin, balance) VALUES (?, ?, ?, ?, ?)", (user_id, name, user_group, admin_status, 0))
        conn.commit()
        
    conn.close()
    
async def setname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    user_id = update.message.from_user.id
    # print(context.args)
    new_name = ' '.join(context.args)
    
    cursor.execute("select username from users where user_id = ?", (user_id,))
    old_name = cursor.fetchone()[0]
    
    old_profile_file = os.path.join(profile_pic_folder, old_name + ".jpg")
    new_profile_file = os.path.join(profile_pic_folder, new_name + ".jpg")
    
    rename_file(old_filename=old_profile_file, new_filename=new_profile_file)
    
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
        text = "You know nothing {}".format(new_name)
    elif "queen" in new_name.lower():
        toss = random.randint(0,1)
        if toss == 0:
            text = "Hello, Your Majesty. I am delighted to meet you"
        elif toss == 1:
            text = "Mamaa Oooooo"
    elif "princess consuela banana hammock" in new_name.lower():
        text = "Okay so now I'm gonna call myself Crap Bag"
    else:
        toss = random.randint(0,4)
        if toss == 0:
            text = "Me: Your Honour, my client has decided to change their name to {}, because it's a cool name.\n\nJudge: Ah yes, it is a cool name. Motion granted!".format(new_name)
        elif toss == 1:
            text = "You're also gonna need a new passport {}. Don't worry, I'll arrange that too".format(new_name)
        elif toss == 2:
            text = "Hello {}!".format(new_name)
        elif toss == 3:
            text = "I'm so glad you changed your name {}, previous one sucked".format(new_name)
        elif toss == 4:
            text = "Your secret is safe with me detective {}. No one will know your real name".format(new_name)
            
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    

# Define the /addfund command
async def addfund(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.message.from_user.id
        user_info = getUserInfo(user_id=user_id)
        
        if user_info["admin"] == False:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="You can't add fund {}. You're not an admin".format(user_info["username"]))
            return
        else:
            member_name, amount = getStringAndNumber(context.args)
            if len(member_name) == 0:
                member_name = user_info["username"]
        
        member_info = getUserInfo(user_name=member_name) 

        if member_info["usergroup"] != update.message.chat.title:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="You can't add fund for {name}. They are from a different group".format(name = member_info["username"]))
            return
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, member_info["user_id"]))

        # Generate a unique transaction ID (TxID)
        tx_id = str(uuid.uuid4())[:8]
        
        # Insert a record in the transactions table
        cursor.execute("INSERT INTO transactions (user_id, tx_id, transaction_type, amount) VALUES (?, ?, 'addfund', ?)", (member_info["user_id"], tx_id, amount))

        cursor.execute("select balance from users where user_id = ?", (member_info["user_id"],))
        member_info["balance"] = cursor.fetchone()[0]
        
        conn.commit()
        conn.close()

        if member_info["balance"] >= 3000:
            text = random.choice(BotResponse.addfund["3k"])
            await context.bot.send_message(chat_id=update.effective_chat.id, 
                                           text=text.format(name = member_info["username"], 
                                                            balance = member_info["balance"],
                                                            amount = amount))
        elif member_info["balance"] >= 2000:
            text = random.choice(BotResponse.addfund["2k"])
            await context.bot.send_message(chat_id=update.effective_chat.id, 
                                           text=text.format(name = member_info["username"],
                                                            balance = member_info["balance"],
                                                            amount = amount))
        elif member_info["balance"] >= 1000:
            text = random.choice(BotResponse.addfund["1k"])
            await context.bot.send_message(chat_id=update.effective_chat.id, 
                                           text=text.format(name = member_info["username"],
                                                            balance = member_info["balance"],
                                                            amount = amount))
        elif member_info["balance"] >= 500:
            text = random.choice(BotResponse.addfund["500"])
            await context.bot.send_message(chat_id=update.effective_chat.id, 
                                           text=text.format(name = member_info["username"],
                                                            balance = member_info["balance"],
                                                            amount = amount))
        elif member_info["balance"] < 500:
            text = random.choice(BotResponse.addfund["<500"])
            await context.bot.send_message(chat_id=update.effective_chat.id, 
                                           text=text.format(name = member_info["username"],
                                                            balance = member_info["balance"],
                                                            amount = amount))

    except Exception as e:
        logging.error(e)
        await handle_error_command(update, context)


def getStringAndNumber(args:list):
    item = ""
    for x in args:
        if x[0] >= '0' and x[0] <= '9':
            bill = float(convert_units(x))
        else:
            item += x + " "
    return item[:-1], bill

# Define the /pay command
async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        time = update.message.date.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)
        item, bill = getStringAndNumber(context.args)
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
        user_info = getUserInfo(user_id=user_id)
        
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Generate a unique transaction ID (TxID)
        tx_id = str(uuid.uuid4())[:8]
        cursor.execute("INSERT INTO transactions (user_id, tx_id, transaction_type, item, amount) VALUES (?, ?, 'pay', ?, ?)", (user_id, tx_id, item, bill))
        cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (bill, user_id))
        cursor.execute("select balance from users where user_id = ?", (user_id,))
        user_info["balance"] = cursor.fetchone()[0]
        user_info["item"] = item
        user_info["bill"] = bill
        daytype = get_time_category(time)
        
        conn.commit()
        conn.close()
        
        if none_item:
            text = random.choice(BotResponse.pay["None"])
            await context.bot.send_message(chat_id=update.effective_chat.id, 
                                           text=text.format(name = user_info["username"],
                                                            balance = user_info["balance"],
                                                            bill = user_info["bill"],
                                                            item = user_info["item"]))
        elif user_info["balance"] == 0:
            text = random.choice(BotResponse.pay["0"])
            await context.bot.send_message(chat_id=update.effective_chat.id, 
                                           text=text.format(name = user_info["username"],
                                                            balance = user_info["balance"],
                                                            bill = user_info["bill"],
                                                            item = user_info["item"]))
        elif user_info["balance"] < 0:
            text = random.choice(BotResponse.pay["<0"])
            await context.bot.send_message(chat_id=update.effective_chat.id, 
                                           text=text.format(name = user_info["username"],
                                                            balance = user_info["balance"],
                                                            bill = user_info["bill"],
                                                            item = user_info["item"]))
        elif daytype in ["Late Night", "Early Morning", "Night"]:   
            text = random.choice(BotResponse.pay[">0day"])
            
            n = 'n' if user_info["item"].lower() in ['a', 'e', 'i', 'o', 'u'] else ''
            await context.bot.send_message(chat_id=update.effective_chat.id, 
                                           text=text.format(name = user_info["username"],
                                                            balance = user_info["balance"],
                                                            bill = user_info["bill"],
                                                            item = user_info["item"],
                                                            daytype = daytype,
                                                            n = n))
        else:   
            text = random.choice(BotResponse.pay[">0"])
            
            n = 'n' if user_info["item"].lower() in ['a', 'e', 'i', 'o', 'u'] else ''
            await context.bot.send_message(chat_id=update.effective_chat.id, 
                                           text=text.format(name = user_info["username"],
                                                            balance = user_info["balance"],
                                                            bill = user_info["bill"],
                                                            item = user_info["item"],
                                                            daytype = daytype,
                                                            n = n))
    
    except Exception as e:
        logging.error(e)
        await handle_error_command(update, context)
        

# Define the /pay command
async def transfer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.message.from_user.id
        user_info = getUserInfo(user_id=user_id)
        member, amount = getStringAndNumber(context.args)
        none_item = False
        if len(member) == 0:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="You can't transfer to yourself {name}".format(name = user_info["username"]))
            return
        
        member_info = getUserInfo(user_name=member)
        if member_info is None:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="I don't know this guy 😕".format(name = user_info["username"]))
            return
        if user_info["balance"] - amount < 0:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="You don't have enough balance to transfer, {name} 😕".format(name = user_info["username"]))
            return
        
        
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Generate a unique transaction ID (TxID)
        tx_id = str(uuid.uuid4())[:8]
        cursor.execute("INSERT INTO transactions (user_id, tx_id, transaction_type, item, amount) VALUES (?, ?, 'debit', ?, ?)", (user_id, tx_id, member_info["username"], amount))
        cursor.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (amount, user_id))
        tx_id = str(uuid.uuid4())[:8]
        cursor.execute("INSERT INTO transactions (user_id, tx_id, transaction_type, item, amount) VALUES (?, ?, 'credit', ?, ?)", (member_info["user_id"], tx_id, user_info["username"], amount))
        cursor.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, member_info["user_id"]))
        
        conn.commit()
        conn.close()
        
        user_info = getUserInfo(user_id=user_id)
        member_info = getUserInfo(user_id=member_info["user_id"])
        
        await context.bot.send_message(chat_id=update.effective_chat.id, 
                                       text="That's what friends are for 🤗. {name1} transferred {amount} Tk. to {name2}'s account. Here's your balance now {name1}: {balance1} Tk.".format(name1 = user_info["username"],
                                                                                                                                                                                            name2 = member_info["username"],
                                                                                                                                                                                            amount = amount,
                                                                                                                                                                                            balance1 = user_info["balance"]))
        
    
    except Exception as e:
        logging.error(e)
        await handle_error_command(update, context)


async def editamount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        tx_id, bill = context.args[0], float(context.args[1])                
        # print(tx_id, bill)
        user_id = update.message.from_user.id
    
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        cursor.execute("select username from users where user_id = ?", (user_id,))
        name = cursor.fetchone()[0]
        cursor.execute("select admin from users where user_id = ?", (user_id,))
        admin_status = cursor.fetchone()[0]
        if only_admin_add_fund and admin_status == False:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="You can't edit amount {}. You're not an admin".format(name))
            return
            
        cursor.execute("select user_id, amount, transaction_type from transactions where tx_id like ?", (f'{tx_id}%',))
        # Fetch all rows
        rows = cursor.fetchall()
        # Get the column names
        columns = [description[0] for description in cursor.description]

        # Convert rows to a list of dictionaries
        table_data = [dict(zip(columns, row)) for row in rows]
        
        old_amount = table_data[0]["amount"]
        item = table_data[0]["transaction_type"]
        user_id = table_data[0]["user_id"]
        
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
        
    except Exception as e:
        logging.error(e)
        await handle_error_command(update, context)

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
        
    except Exception as e:
        logging.error(e)
        await handle_error_command(update, context)
        
# Define the /balance command
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_info = getUserInfo(user_id=user_id)
    
    if user_info["balance"] >= 3000:
        text = random.choice(BotResponse.balance["3k"])
        
        image_folder = "images"
        balance_folder = "balance"
        low_folder = "rich"
        image_folder = os.path.join(os.getcwd(), image_folder, balance_folder, low_folder)
        image_files = [os.path.join(image_folder, f) for f in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, f))]

        await update.message.reply_photo(photo=random.choice(image_files), caption=text.format(name = user_info["username"],
                                                                                          balance = user_info["balance"]))
        # await context.bot.send_message(chat_id=update.effective_chat.id, text=text.format(name = user_info["username"],
        #                                                                                   balance = user_info["balance"]))
    elif user_info["balance"] >=2000:
        text = random.choice(BotResponse.balance["2k"])
        image_folder = "images"
        balance_folder = "balance"
        low_folder = "rich"
        image_folder = os.path.join(os.getcwd(), image_folder, balance_folder, low_folder)
        image_files = [os.path.join(image_folder, f) for f in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, f))]

        await update.message.reply_photo(photo=random.choice(image_files), caption=text.format(name = user_info["username"],
                                                                                          balance = user_info["balance"]))
        # await context.bot.send_message(chat_id=update.effective_chat.id, text=text.format(name = user_info["username"],
        #                                                                                   balance = user_info["balance"]))
    elif user_info["balance"] >= 1000:
        text = random.choice(BotResponse.balance["1k"])
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text.format(name = user_info["username"],
                                                                                          balance = user_info["balance"]))
    elif user_info["balance"] >= 500:
        text = random.choice(BotResponse.balance["500"])
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text.format(name = user_info["username"],
                                                                                          balance = user_info["balance"]))
    elif user_info["balance"] >= 100:
        text = random.choice(BotResponse.balance["100"])
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text.format(name = user_info["username"],
                                                                                          balance = user_info["balance"]))
    elif user_info["balance"] > 0:
        text = random.choice(BotResponse.balance[">0"])
        await context.bot.send_message(chat_id=update.effective_chat.id, text=text.format(name = user_info["username"],
                                                                                          balance = user_info["balance"]))
    elif user_info["balance"] == 0:
        text = random.choice(BotResponse.balance["0"])
        
        image_folder = "images"
        balance_folder = "balance"
        low_folder = "low"
        image_folder = os.path.join(os.getcwd(), image_folder, balance_folder, low_folder)
        image_files = [os.path.join(image_folder, f) for f in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, f))]

        await update.message.reply_photo(photo=random.choice(image_files), caption=text.format(name = user_info["username"],
                                                                                          balance = user_info["balance"]))
        # await context.bot.send_message(chat_id=update.effective_chat.id, text=text.format(name = user_info["username"],
        #                                                                                   balance = user_info["balance"]))
    elif user_info["balance"] < 0:
        text = random.choice(BotResponse.balance["<0"])
        
        image_folder = "images"
        balance_folder = "balance"
        low_folder = "low"
        image_folder = os.path.join(os.getcwd(), image_folder, balance_folder, low_folder)
        image_files = [os.path.join(image_folder, f) for f in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, f))]

        await update.message.reply_photo(photo=random.choice(image_files), caption=text.format(name = user_info["username"],
                                                                                          balance = user_info["balance"]))
        # await context.bot.send_message(chat_id=update.effective_chat.id, text=text.format(name = user_info["username"],
        #                                                                                   balance = user_info["balance"]))
    
            
    

# Define the /history command
async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
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
            await handle_error_command(update, context)
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
            elif row["transaction_type"] == "pay":
                text += "- On {}, you added {} Tk. to your fund. TxID: {}\n".format(row["timestamp"], row["amount"], row["tx_id"])
            elif row["transaction_type"] == "credit":
                text += "- On {}, {} Tk. was transferred to your fund from {}. TxID: {}\n".format(row["timestamp"], row["amount"], row["item"], row["tx_id"])
            elif row["transaction_type"] == "debit":
                text += "- On {}, you transferred {} Tk. to {}. TxID: {}\n".format(row["timestamp"], row["amount"], row["item"], row["tx_id"])
                
        cursor.execute("select balance from users where user_id = ?", (user_id,))
        bl = cursor.fetchone()[0]
        
        text += "\nYour current balance is {} Tk.".format(bl)
        
        conn.commit()
        conn.close()

        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    
    except Exception as e:
        logging.error(e)
        await handle_error_command(update, context)
    
async def showmembers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_group = update.message.chat.title
    user_id = update.message.from_user.id
    if user_group is None:
        user_group = user_id
        
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    cursor.execute("select username, admin from users where usergroup = ?", (user_group,))
    # Fetch all rows
    rows = cursor.fetchall()
    # Get the column names
    columns = [description[0] for description in cursor.description]

    # Convert rows to a list of dictionaries
    table_data = [dict(zip(columns, row)) for row in rows]
    
    text = ""
    count = 1
    for row in table_data:
        text += "{}. {}".format(count, row["username"])
        count += 1
        if row["admin"] == 1:
            text += " (Admin)"
        text += "\n"
    
    conn.commit()
    conn.close()

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)
    
async def allbalance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_group = update.message.chat.title
    user_id = update.message.from_user.id
    if user_group is None:
        user_group = user_id
        
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    cursor.execute("select username, admin, balance from users where usergroup = ? order by balance desc", (user_group,))    
    # Fetch all rows
    rows = cursor.fetchall()
    # Get the column names
    columns = [description[0] for description in cursor.description]

    # Convert rows to a list of dictionaries
    table_data = [dict(zip(columns, row)) for row in rows]
    total = len(rows)
    text = ""
    count = 1
    fund = 0
    for row in table_data:
        fund += row["balance"]
        text += "{}. {}".format(count, row["username"])
        if count == 1:
            text += " 👑 "
        if count == total and count != 1:
            text += " 😞 "
        count += 1
        if row["admin"] == 1:
            text += " (Admin)"
        text += ":{} Tk.".format(row["balance"])
        text += "\n"
    text += "\nTotal amount in the fund: {} Tk.".format(fund)
    conn.commit()
    conn.close()

    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

async def tabaqmenu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_info = getUserInfo(user_id=user_id)
    image_folder = "images"
    menu_folder = "menu"
    menu_image_folder = os.path.join(os.getcwd(), image_folder, menu_folder)
    image_files = [os.path.join(menu_image_folder, f) for f in os.listdir(menu_image_folder) if os.path.isfile(os.path.join(menu_image_folder, f))]

    for image in image_files:
        with open(image, 'rb') as photo:
            await update.message.reply_photo(photo=photo, caption="Tabq Menu")
            
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Pick one {name}".format(name=user_info["username"]))
    
async def whoami(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_info = getUserInfo(user_id=user_id)
    
    image_files = [f for f in os.listdir(profile_pic_folder)]
    image = find_matching_string(image_files, user_info["username"])
    if image is None:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Are you John Cena? Cause I can't see you")
        return
    
    image = os.path.join(profile_pic_folder, image)
    with open(image, 'rb') as photo:
        await update.message.reply_photo(photo=photo, caption="This is you {}".format(user_info["username"]))
    
async def calc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_info = getUserInfo(user_id=user_id)
    if len(context.args) == 0:
        text = "You have give me something to calculate, {name}".format(name=user_info["username"])
        
    expression = ' '.join(context.args)
    result = calculate_expression(expression)
    if result is None:
        await handle_error_command(update, context)
        return
    
    text = "Ans = {result}".format(expression=expression, result = result)
    
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
    transfer_handler = CommandHandler('transfer', transfer)
    history_handler = CommandHandler('history', history)
    addfund_handler = CommandHandler('addfund', addfund)
    editamount_handler = CommandHandler('editamount', editamount)
    edititem_handler = CommandHandler('edititem', edititem)
    showmembers_handler = CommandHandler('showmembers', showmembers)
    allbalance_handler = CommandHandler('allbalance', allbalance)
    tabaqmenu_handler = CommandHandler('tabaqmenu', tabaqmenu)
    whoami_handler = CommandHandler('whoami', whoami)
    calc_handler = CommandHandler('calc', calc)
    help_handler = CommandHandler('help', help_command)
    
    application.add_handler(start_handler)
    application.add_handler(setname_handler)
    application.add_handler(pay_handler)
    application.add_handler(transfer_handler)
    application.add_handler(balance_handler)
    application.add_handler(history_handler)
    application.add_handler(addfund_handler)
    application.add_handler(editamount_handler)
    application.add_handler(edititem_handler)
    application.add_handler(showmembers_handler)
    application.add_handler(allbalance_handler)
    application.add_handler(tabaqmenu_handler)
    application.add_handler(whoami_handler)
    application.add_handler(calc_handler)
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
            usergroup TEXT,
            balance REAL DEFAULT 0.0,
            admin INTEGER DEFAULT 0
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
