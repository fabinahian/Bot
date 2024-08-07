import os
from dotenv import load_dotenv


load_dotenv()


class Config():
    TabaqBillBot_Token = os.getenv('BOT_TOKEN')
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///bot/database/data/Tabaq.db')
    OPENAI_API_TOKEN = os.getenv('OPENAI_API_TOKEN')

