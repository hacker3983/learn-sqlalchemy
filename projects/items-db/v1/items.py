from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import Table, Column
from sqlalchemy import insert, select, update, delete
from sqlalchemy import Integer, String
from enum import IntEnum
import readline

class Option(IntEnum):
    EXIT = 5
    CREATE_ITEM = 1
    READ_ITEMS = 2
    UPDATE_ITEM = 3
    DELETE_ITEM = 4

class UpdateOption(IntEnum):
    ITEM_NAME = 1
    ITEM_DESCRIPTION = 2
    ITEM_VALUE = 3

def add_item(name, description, value):
    with engine.begin() as conn:
        conn.execute(insert(items_table).values(
            name=name, description=description,
            value=value
        ))

def read_items():
    with engine.connect() as conn:
        result = conn.execute(select(items_table)).all()
    return result

def print_items(result):
    for id, item_name, item_description, value in result:
        print(f"[{id}] {item_name} - {item_description} (value: {value})")

def update_item(item_id, item_name=None, item_description=None, item_value=None):
    with engine.begin() as conn:
        if item_name:
            try:
                conn.execute(
                    update(items_table)
                    .where(items_table.c.id == item_id)
                    .values(name=item_name)
                )
                print("Successfully updated item name!")
            except:
                print("Failed to update the name of the item!")
        elif item_description:
            try:
                conn.execute(
                    update(
                        items_table
                    )
                    .where(items_table.c.id == item_id)
                    .values(description=item_description)
                )
                print("Successfully updated item description!")
            except:
                print("Failed to update the description of the item!")
        elif item_value:
            try:
                conn.execute(
                    update(
                        items_table
                    )
                    .where(items_table.c.id == item_id)
                    .values(value=item_value)
                )
                print("Successfully updated item value!")
            except:
                print("Failed to update the value of the item!")

def delete_item(item_id):
    with engine.begin() as conn:
        conn.execute(
            delete(items_table)
            .where(items_table.c.id == item_id)
        )
        print("Successfully deleted item!")

engine = create_engine("sqlite+pysqlite:///test.db")
metadata_obj = MetaData()
items_table = Table(
    "items_table",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("name", String(50)),
    Column("description", String),
    Column("value", Integer)
)
metadata_obj.create_all(engine)

def print_menu():
    print("Welcome to items db!")
    print("Version: 1.0")
    print("Please select an Option below:")
    print("[1] Create a new item")
    print("[2] Read all items")
    print("[3] Update item")
    print("[4] Delete item")
    print("[5] Exit the program")

def get_option():
    return input("Select an option> ")

def get_item_details():
    item_name = input("Enter the name of the item: ")
    item_description = input("Enter the description of the item: ")
    item_value = int(input("Enter the value of the item: "))
    return (item_name, item_description, item_value)

def print_update_options():
    print("[1] Update item name")
    print("[2] Change item description")
    print("[3] Modify item value")
    try:
        option = int(input("Enter the item property you want to update> "))
    except ValueError:
        return None
    return option

def update_item_details():
    items = read_items()
    print_items(items)
    try:
        item_id = int(input("Please select an item> "))
    except ValueError:
        print("Error invalid item option.")
        print("Please try again...")
        return
    found = False
    for item in items:
        if item_id == item.id:
            found = True
    if not found:
        print("Error invalid item option.")
        print("Please try again...")
        return
    update_option = print_update_options()
    if update_option == UpdateOption.ITEM_NAME:
        item_name = input("Enter the new item name: ")
        update_item(item_id, item_name=item_name)
    elif update_option == UpdateOption.ITEM_DESCRIPTION:
        item_description = input("Enter the new item description: ")
        update_item(item_id, item_description=item_description)
    elif update_option == UpdateOption.ITEM_VALUE:
        try:
            item_value = int(input("Enter the new item value: "))
            update_item(item_id, item_value=item_value)
        except ValueError:
            print("Invalid item value.")
            print("Please try again...")
    else:
        print("Error invalid option")
        print("Please try again...")

def delete_item_details():
    items = read_items()
    print_items(items)
    try:
        item_id = int(input("Enter the item id: "))
        for item in items:
            if item.id == item_id:
                delete_item(item_id)
                return
        print("Failed to delete item.")
        print("Please try again...")
    except ValueError:
        print("Invalid item id.")
        print("Please try again...")

def main_menu():
    while True:
        print_menu()
        option = get_option().strip()
        try:
            option = int(option)
        except ValueError:
            print("Error the option you entered is invalid.")
            print("Please try again...")
            continue
        if option == Option.CREATE_ITEM:
            item_name, item_description, item_value = get_item_details()
            add_item(item_name, item_description, item_value)
        elif option == Option.READ_ITEMS:
            items = read_items()
            print_items(items)
        elif option == Option.UPDATE_ITEM:
            update_item_details()
        elif option == Option.DELETE_ITEM: 
            delete_item_details()
        elif option == Option.EXIT:
            print("Exiting the program...")
            break
        else:
            print("Error the option you entered is not a valid option.")
            print("Please try again...")

main_menu()
