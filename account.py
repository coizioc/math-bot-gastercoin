"""Implements an i/o system for accessing and changing GasterCoin account values."""
import ujson

ACCOUNTS_FILE = f'./subs/gastercoin/resources/accounts.json'

BALANCE_KEY = 'balance'
FREE_MONEY_KEY = 'free_money'
SPECIAL_MOVE_KEY = 'special_move'
DEFAULT_ACCOUNT = {BALANCE_KEY: 0,
                   FREE_MONEY_KEY: 0,
                   SPECIAL_MOVE_KEY: 'being lame and not having a special move set by typing '
                                     '`~dm special edit [message]`'}

SUCCESS_STRING = 'SUCCESS'


def parse_int(number_as_string, return_bool=False):
    """Converts an string into an int if the string represents a valid integer"""
    try:
        if len(number_as_string) > 1:
            int(str(number_as_string)[:-1])
        else:
            if len(number_as_string) == 0:
                if return_bool:
                    return False
                else:
                    raise ValueError
            if len(number_as_string) == 1 and number_as_string.isdigit():
                if return_bool:
                    return True
                else:
                    return int(number_as_string)
            else:
                if return_bool:
                    return False
                else:
                    raise ValueError
    except ValueError:
        if return_bool is False:
            raise ValueError
        else:
            return False
    last_char = str(number_as_string)[-1]
    if not return_bool:
        if last_char.isdigit():
            return int(number_as_string)
        elif last_char == 'k':
            return int(number_as_string[:-1]) * 1000
        elif last_char == 'm':
            return int(number_as_string[:-1]) * 1000000
        elif last_char == 'b':
            return int(number_as_string[:-1]) * 1000000000
        else:
            raise ValueError
    if return_bool:
        if last_char.isdigit() or last_char in ['k', 'm', 'b']:
            return True
        else:
            return False


def update_account(userid, amount, key=BALANCE_KEY):
    """Changes the value of a key within a user's account."""
    userid = str(userid)
    with open(ACCOUNTS_FILE, 'r') as f:
        accounts = ujson.load(f)

    if userid not in accounts:
        accounts[userid] = DEFAULT_ACCOUNT

    if key == BALANCE_KEY:
        accounts[str(userid)][BALANCE_KEY] += amount
    if key == FREE_MONEY_KEY:
        accounts[str(userid)][FREE_MONEY_KEY] = amount
    if key == SPECIAL_MOVE_KEY:
        accounts[str(userid)][SPECIAL_MOVE_KEY] = amount

    with open(ACCOUNTS_FILE, 'w') as f:
        ujson.dump(accounts, f)


def read_account(userid, key=BALANCE_KEY):
    """Reads the value of a key within a user's account."""
    userid = str(userid)
    try:
        with open(ACCOUNTS_FILE, 'r') as f:
            accounts = ujson.load(f)
        if userid not in accounts:
            accounts[userid] = DEFAULT_ACCOUNT
        return accounts[userid][key]
    except KeyError:
        return 0


def check_if_valid_transaction(userid, amount, username=None, zero_valid=False):
    """Determines whether a user can make a transaction or not based on the inputted amount."""
    try:
        amount = parse_int(str(amount))
        if amount <= 0 and not zero_valid or amount < 0 and zero_valid:
            return f'Error: G${amount} is not a valid transaction amount.'
        author_balance = read_account(userid)
        if author_balance < amount:
            if username is None:
                return f'Error: Insufficient funds. Your current balance is G${author_balance}.'
            else:
                return f"Error: Insufficient funds. {username}'s current balance is G${author_balance}."
        return SUCCESS_STRING
    except ValueError:
        return f'Error: G${amount} is not a valid number.'
