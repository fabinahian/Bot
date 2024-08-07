import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bot.config import Config

# Ensure the 'data' directory exists
if not os.path.exists('data'):
    os.makedirs('data')

engine = create_engine(Config.DATABASE_URL)
Session = sessionmaker(bind=engine)

def init_db():
    from .models import Base
    Base.metadata.create_all(engine)

def get_session():
    return Session()
