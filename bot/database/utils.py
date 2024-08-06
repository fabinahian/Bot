from sqlalchemy.orm import Session
from sqlalchemy import or_
from bot.database.models import User, Transaction
from bot.database.database import get_session
import uuid


credit_transaction_types = ["addfund", "credit"]
debit_transaction_types = ["pay", "debit"]



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

def update_username(user_id, new_username):
    session = get_session()
    user = session.query(User).filter_by(user_id=user_id).first()
    if user:
        user.username = new_username
        session.commit()
    session.close()
    
def get_usernames_by_usergroup(usergroup):
    session = get_session()
    users = session.query(User).filter_by(usergroup=usergroup).all()
    session.close()
    return [{'username': user.username, 'balance': user.balance, 'admin': user.admin} for user in users]

def insert_transaction_and_update_balance(user_id, item, transaction_type, amount):
    session = get_session()
    
    if transaction_type in debit_transaction_types and amount > 0:
            amount = -1*amount
    
    try:
        # Insert the transaction
        tx_id = str(uuid.uuid4())
        transaction = Transaction(
            user_id=user_id,
            tx_id=tx_id,
            transaction_type=transaction_type,
            item=item,
            amount=abs(amount)
        )
        session.add(transaction)
        
        
        # Update the user's balance
        user = session.query(User).filter_by(user_id=user_id).first()
        if user:
            user.balance += amount
        else:
            raise ValueError("User not found")

        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def update_transaction_and_balance(tx_id, new_amount = None, item = None):
    session = get_session()
    try:
        # Retrieve the transaction
        transaction = session.query(Transaction).filter_by(tx_id=tx_id).first()
        if not transaction:
            raise ValueError("Transaction not found")

        amount_difference = 0
        
        if new_amount is not None:
            # Calculate the difference between the new amount and the current amount
            amount_difference = new_amount - transaction.amount

            # Update the transaction with the new amount
            transaction.amount = new_amount

        if item is not None:
            transaction.item = item
        
        # Update the user's balance
        user = session.query(User).filter_by(user_id=transaction.user_id).first()
        if user:
            user.balance += amount_difference
        else:
            raise ValueError("User not found")

        session.commit()
        return user.as_dict()  # Return the updated user information as a dictionary
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


# Add this method to the User model for convenience
def as_dict(self):
    return {c.name: getattr(self, c.name) for c in self.__table__.columns}

User.as_dict = as_dict
