
import re
from datetime import datetime


def clean_date(dateStr):
    try:
        date = datetime.strptime(dateStr, '%m/%d/%Y')
    except ValueError:
        print(
            'The value entered is not the correct format. Please enter a date in the format: January 1, 2021')
    else:
        return date
    return None


def clean_price(priceStr):
    price = priceStr.split('$')[1] if '$' in priceStr else priceStr
    try:
        price = int(float(price) * 100)
    except ValueError:
        print('The value entered is not the correct format. Please enter a price in the format: $19.95')
    else:
        return price
    return None


def clean_item(item):
    cleaned_item = {}
    for key, value in item.items():
        if key == 'date_updated':
            cleaned_item[key] = clean_date(value)
        elif key == 'product_price':
            cleaned_item[key] = clean_price(value)
        elif key == 'product_quantity':
            cleaned_item[key] = int(value)
        else:
            cleaned_item[key] = value
    return cleaned_item


def clean_data(data):
    cleaned_data = []
    for item in data:
        cleaned_data.append(clean_item(item))
    return cleaned_data


def is_all_of_type(collection, type):
    return all(isinstance(x, type) for x in collection)


def input_choice(message, choices, case_sensitive=False):
    if type(message) != str:
        raise ValueError(
            'Expecting message argument to be a string')

    if type(choices) != tuple and type(choices) != list or len(choices) == 0 or not is_all_of_type(choices, str):
        raise ValueError(
            'Expecting choices argument to be a tuple or list of one or more strings')

    choice = input(message)

    if not case_sensitive:
        choices = [c.lower() for c in choices]
        choice = choice.lower()

    if choice not in choices:
        raise ValueError(
            f'Input not in choices: {choices}')

    return choice

def input_int(message, can_be_negative=True):
    value = input(message)
    value = int(value)

    if not can_be_negative and value < 0:
        raise ValueError(f'Input must be a non-negative number')

    return value

def input_currency(message):
    US_CURRENCY_REGEX = r'^[0-9]{1,3}(?:,?[0-9]{3})*(?:\.[0-9]{2})?$'

    value = input(message)

    if len(re.findall(US_CURRENCY_REGEX, value)) == 0:
        raise ValueError(f'Input must be a valid currency amount. For example 1,234.56')

    value = float(value)

    return int(value * 100)

def format_price(price_int):
    return f'${"{:.2f}".format(price_int / 100)}'

def format_date(datetime):
    return datetime.strftime('%B %d, %Y')
