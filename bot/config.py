import os
from dotenv import load_dotenv


load_dotenv()


class Config():
    TabaqBillBot_Token = os.getenv('BOT_TOKEN')
    DATABASE_URL = os.getenv('DATABASE_URL')

