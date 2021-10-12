import csv
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


def export_inventory(filepath):
    header = ['product_name', 'product_quantity',
              'product_price', 'date_updated']
    data = session.query(Product).all()
    with open(filepath, 'w') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows([row.as_tuple() for row in data])
        print(f'Inventory exported to {filepath}')


def app():
    while True:
        print(f'''
        \rStore Inventory
        \r(V) View a single product's inventory
        \r(A) Add a new product to the database
        \r(B) Make a backup of the entire inventory
        \r(E) Exit
        ''')

        try:
            choice = input_choice(
                'What would you like to do? ', ('v', 'a', 'b', 'e'))
        except ValueError as err:
            print(f'\nOops! Something went wrong - {err}')
        else:
            if choice == 'v':
                while True:
                    product_ids = [str(id)
                                   for id, in session.query(Product.product_id)]

                    try:
                        print(f'\nAvailable products by id: {product_ids}')
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
            elif choice == 'a':
                while True:
                    print('\nAdd a New Product\n')
                    product_name = input('Name: ')
                    product_price = input_currency('Price (ex: 5.00): $')
                    product_quantity = input_int('Quantity (ex: 1000): ')

                    product = session.query(Product).filter(
                        Product.product_name == product_name).one()

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
            elif choice == 'b':
                print('\nExporting data...\n')
                export_inventory('backup.csv')
                pass
            else:
                print('Goodbye!')
                break


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    import_inventory('inventory.csv')
    app()
