from db import Base, engine, session
from utils import add_product, export_inventory, import_inventory, input_choice, view_inventory


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
                view_inventory()
            elif choice == 'a':
                add_product()
            elif choice == 'b':
                export_inventory('backup.csv')
            else:
                print('Goodbye!')
                break


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    import_inventory('inventory.csv')
    app()
