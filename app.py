import csv
from datetime import datetime
from db import Base, engine, session
from models import Product
from utils import clean_data, format_date, format_price, input_choice, input_int, input_currency


def import_inventory(filepath):
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


def export_inventory():
    now = datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')
    filename = f'inventory_{now}.csv'
    header = ['product_name', 'product_quantity', 'product_price', 'date_updated']
    data = session.query(Product).all()
    # print(','.join(header))
    with open(filename, 'w') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows([row.as_tuple() for row in data])
        print(f'Inventory exported to {filename}')

def main_menu():
    while True:
        print(f'''
        \rStore Inventory
        \r(V) Display Product by ID
        \r(A) Add a new product
        \r(B) Export
        \r(E) Exit
        ''')

        try:
            choice = input_choice('What would you like to do? ', ('v', 'a', 'b', 'e'))
        except ValueError as err:
            print(f'Oops! Something went wrong - {err}')
        else:
            if choice == 'v':
                while True:
                    print('\nProduct Details\n')
                    product_ids = [str(id) for id, in session.query(Product.product_id)]

                    try:
                        choice = input_choice(
                            f'Choose a product by it\'s id to view details: {product_ids} ', product_ids)
                    except ValueError as err:
                        print(f'Oops! Something went wrong - {err}')
                    else:
                        choice = int(choice)                
                        product = session.query(Product).filter(Product.product_id == choice).one()
                        print(f'''
                            \nViewing Details for {product.product_name}:
                            \rPrice: {format_price(product.product_price)}
                            \rAvailable Qty: {product.product_quantity}
                            \rLast Update: {format_date(product.date_updated)}
                        ''')
                        if not input('Press enter to continue.'):
                            break
            elif choice == 'a':
                while True:
                    print('\nAdd a New Product\n')
                    product_name = input('Name: ')
                    product_price = input_currency('Price (ex: 5.00): $')
                    product_quantity = input_int('Quantity (ex: 1000): ')

                    product = Product(product_name, product_quantity, product_price)
                    session.add(product)
                    session.commit()

                    print(f'''
                        \nAdded new product: {product.product_name}
                        \rPrice: {format_price(product.product_price)}
                        \rAvailable Qty: {product.product_quantity}
                        \rAdded On: {format_date(product.date_updated)}
                    ''')
                    if not input('Press enter to continue.'):
                        break
            elif choice == 'b':
                print('\nExporting data...\n')
                export_inventory()
                pass
            else:
                print('Goodbye!')
                break


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    import_inventory('inventory.csv')
    main_menu()
