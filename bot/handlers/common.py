import ast
import re
from datetime import datetime, timedelta
from bot.logging_config import logger, logging
from bot.database.utils import get_user_by_username, get_user_by_user_id, get_user_by_tx_id


logger = logging.getLogger(__name__)

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
    
def get_time_category(current_time:datetime)->str:

    current_time = current_time.time()
    if current_time < datetime.strptime("04:00", "%H:%M").time():
        return "Late Night"
    elif current_time < datetime.strptime("09:00", "%H:%M").time():
        return "Early Morning"
    elif current_time < datetime.strptime("12:00", "%H:%M").time():
        return "Morning"
    elif current_time < datetime.strptime("13:00", "%H:%M").time():
        return "Noon"
    elif current_time < datetime.strptime("17:00", "%H:%M").time():
        return "Afternoon"
    elif current_time < datetime.strptime("20:00", "%H:%M").time():
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

def get_GMT6_time(time:datetime):
    return time + timedelta(hours=6)

def get_user_info(user_id = None, user_name = None, tx_id = None):
    if user_id is not None:
        logger.debug(f"User ID {user_id}")
        user_info = get_user_by_user_id(user_id=user_id)
        logger.debug(f"User Info: {user_info}")
        return user_info
    if user_name is not None:
        logger.debug(f"User Name(s) {user_id}")
        multiple_usernames = True
        if not isinstance(user_name, list):
            multiple_usernames = False
            user_name = [user_name]
        user_info = get_user_by_username(usernames=user_name)
        logger.debug(f"User Info: {user_info}")
        if multiple_usernames:
            return user_info
        return user_info[0]
    
    if tx_id is not None:
        logger.debug(f"Transaction ID {user_id}")
        user_info = get_user_by_tx_id(tx_id=tx_id)
        logger.debug(f"User Info: {user_info}")
        return user_info
    
    return None
    
    
    