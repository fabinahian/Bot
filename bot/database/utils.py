from sqlalchemy.orm import Session
from sqlalchemy import or_
from bot.database.models import User, Transaction
from bot.database.database import get_session


def get_user_by_username(usernames:list)->list:
    session = get_session()
    users = session.query(User).filter(or_(*[User.username.like(f"%{name}%") for name in usernames])).all()
    session.close()
    return [user.as_dict() for user in users]

def get_user_by_user_id(user_id):
    session = get_session()
    user = session.query(User).filter_by(user_id=user_id).first()
    session.close()
    return user.as_dict() if user else None

def get_user_by_tx_id(tx_id):
    session = get_session()
    transaction = session.query(Transaction).filter_by(tx_id=tx_id).first()
    if not transaction:
        session.close()
        return None
    user = session.query(User).filter_by(user_id=transaction.user_id).first()
    session.close()
    return user.as_dict() if user else None

def create_user(user_id, username, usergroup, admin, balance):
    session = get_session()
    new_user = User(
        user_id=user_id,
        username=username,
        usergroup=usergroup,
        admin=admin,
        balance=balance
    )
    session.add(new_user)
    session.commit()
    session.close()

# Add this method to the User model for convenience
def as_dict(self):
    return {c.name: getattr(self, c.name) for c in self.__table__.columns}

User.as_dict = as_dict
