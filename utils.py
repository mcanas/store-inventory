import csv
import re
from db import session
from datetime import datetime
from models import Product


def clean_date(dateStr):
    '''Parses a date string in the format mm/dd/yyy and returns a datetime object'''

    try:
        date = datetime.strptime(dateStr, '%m/%d/%Y')
    except ValueError:
        print(
            'The value entered is not the correct format. Please enter a date in the format: January 1, 2021')
    else:
        return date
    return None


def clean_price(priceStr):
    '''Parses a price string in the format of $19.95 and returns an integer value'''

    price = priceStr.split('$')[1] if '$' in priceStr else priceStr
    try:
        price = int(float(price) * 100)
    except ValueError:
        print('The value entered is not the correct format. Please enter a price in the format: $19.95')
    else:
        return price
    return None


def clean_item(item):
    '''Takes product info from dictionary and prepares it for insertion into the database'''

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
    '''Take a list of product dictionaries and returns a list of cleaned product dictionaries'''

    cleaned_data = []
    for item in data:
        cleaned_data.append(clean_item(item))
    return cleaned_data


def is_all_of_type(collection, type):
    '''Takes a list or tuple and returns True if all elements match the given type, otherwise False'''

    return all(isinstance(x, type) for x in collection)


def input_choice(message, choices, case_sensitive=False):
    '''An input method that will accept a value from a list/tuple of choices.
        Returns the value if valid, otherwise will raise an error'''

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
            f'Your choice "{choice}" is not in the list of available values: {", ".join(choices)}')

    return choice


def input_int(message, can_be_negative=True):
    '''An input method that accepts only an integer-like value.
        Returns the int value if valid, otherwise will raise an error'''

    value = input(message)
    value = int(value)

    if not can_be_negative and value < 0:
        raise ValueError(f'Input must be a non-negative number')

    return value


def input_currency(message):
    '''An input method that only accepts a value in the format of US currency.
        Returns a converted int value if valid, otherwise will raise an error'''
    US_CURRENCY_REGEX = r'^[0-9]{1,3}(?:,?[0-9]{3})*(?:\.[0-9]{2})?$'

    value = input(message)

    if len(re.findall(US_CURRENCY_REGEX, value)) == 0:
        raise ValueError(
            f'Input must be a valid currency amount. For example 1,234.56')

    value = float(value)

    return int(value * 100)


def format_price(price_int):
    '''Takes an integer value and returns a string in the format of US currency'''

    return f'${"{:.2f}".format(price_int / 100)}'


def format_date(datetime):
    '''Takes a datetime value and returns a string in the format of January 1, 2020'''
    return datetime.strftime('%B %d, %Y')


def import_inventory(filepath):
    '''Takes a filepath to a csv file and imports product related info into the database'''

    cleaned_data = None

    with open(filepath, newline='') as csvfile:
        cleaned_data = clean_data(csv.DictReader(csvfile))
        csvfile.close()

    if cleaned_data:
        for item in cleaned_data:
            product_in_db = session.query(Product).filter(
                Product.product_name == item['product_name']).one_or_none()

            if product_in_db:
                if product_in_db.date_updated < item['date_updated']:
                    product_in_db.product_price = item['product_price']
                    product_in_db.product_quantity = item['product_quantity']
                    product_in_db.date_updated = item['date_updated']
            else:
                product = Product(**item)
                session.add(product)

        session.commit()


def view_inventory():
    '''The menu interface to view inventory by id'''

    while True:
        product_ids = [str(id)
                       for id, in session.query(Product.product_id)]

        try:
            print(
                f'\nAvailable products by id: {", ".join(product_ids)}')
            choice = input_choice(
                f'\nWhich product would you like to view?: ', product_ids)
        except ValueError as err:
            print(f'\nOops! Something went wrong - {err}')
        else:
            choice = int(choice)
            product = session.query(Product).filter(
                Product.product_id == choice).one()
            print(f'''
                \nViewing Details for {product.product_name}:
                \rPrice: {format_price(product.product_price)}
                \rAvailable Qty: {product.product_quantity}
                \rLast Update: {format_date(product.date_updated)}
            ''')
            if not input('Press enter to continue.'):
                break


def add_product():
    '''The menu interface to add or update product'''

    while True:
        print('\nAdd a New Product\n')
        product_name = input('Name: ')
        product_price = input_currency('Price (ex: 5.00): $')
        product_quantity = input_int('Quantity (ex: 1000): ')

        product = session.query(Product).filter(
            Product.product_name == product_name).one_or_none()

        if product != None:
            product.product_name = product_name
            product.product_price = product_price
            product.product_quantity = product_quantity
            print(f'''
                \nUpdated product: {product.product_name}
                \rPrice: {format_price(product.product_price)}
                \rAvailable Qty: {product.product_quantity}
                \rUpdated On: {format_date(product.date_updated)}
            ''')
        else:
            product = Product(
                product_name, product_quantity, product_price)
            session.add(product)
            print(f'''
                \nAdded new product: {product.product_name}
                \rPrice: {format_price(product.product_price)}
                \rAvailable Qty: {product.product_quantity}
                \rAdded On: {format_date(product.date_updated)}
            ''')

        session.commit()

        if not input('Press enter to continue.'):
            break


def export_inventory(filepath):
    '''Exports the current inventory database to a backup.csv file.'''

    print('\nExporting data...\n')
    header = ['product_name', 'product_quantity',
              'product_price', 'date_updated']
    data = session.query(Product).all()
    with open(filepath, 'w') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows([row.as_tuple() for row in data])
        print(f'Inventory exported to {filepath}')
