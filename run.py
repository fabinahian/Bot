from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from bot.handlers.info.info import start, setname, showmembers, help_command
from bot.handlers.transactions.transactions import pay, transfer, addfund, editamount, edititem, distribute
from bot.handlers.utils.utils import calc
from bot.handlers.statements.statements import balance, allbalance, history, session
from bot.response.response import generate_response

token = '6443735527:AAH-62niLYpw7z6VRSyz3IQkFNV9xB_sWhY'

def main():
    application = ApplicationBuilder().token(token).build()
    
    start_handler = CommandHandler("start", start)
    setname_handler = CommandHandler("setname", setname)
    balance_handler = CommandHandler('balance', balance)
    pay_handler = CommandHandler('pay', pay)
    transfer_handler = CommandHandler('transfer', transfer)
    distribute_handler = CommandHandler('distribute', distribute)
    history_handler = CommandHandler('history', history)
    session_handler = CommandHandler('session', session)
    addfund_handler = CommandHandler('addfund', addfund)
    editamount_handler = CommandHandler('editamount', editamount)
    edititem_handler = CommandHandler('edititem', edititem)
    showmembers_handler = CommandHandler('showmembers', showmembers)
    allbalance_handler = CommandHandler('allbalance', allbalance)
    # tabaqmenu_handler = CommandHandler('tabaqmenu', tabaqmenu)
    # whoami_handler = CommandHandler('whoami', whoami)
    calc_handler = CommandHandler('calc', calc)
    help_handler = CommandHandler('help', help_command)
    
    application.add_handler(start_handler)
    application.add_handler(setname_handler)
    application.add_handler(pay_handler)
    application.add_handler(transfer_handler)
    application.add_handler(distribute_handler)
    application.add_handler(balance_handler)
    application.add_handler(history_handler)
    application.add_handler(session_handler)
    application.add_handler(addfund_handler)
    application.add_handler(editamount_handler)
    application.add_handler(edititem_handler)
    application.add_handler(showmembers_handler)
    application.add_handler(allbalance_handler)
    # application.add_handler(tabaqmenu_handler)
    # application.add_handler(whoami_handler)
    application.add_handler(calc_handler)
    application.add_handler(help_handler)
    
    application.run_polling()

if __name__ == "__main__":
    main()