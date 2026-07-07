from sqlalchemy import create_engine
from sqlalchemy import select, delete
from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import Session
from enum import IntEnum
import readline


engine = create_engine("sqlite+pysqlite:///test.db")

class Base(DeclarativeBase):
    pass

class Item(Base):
    __tablename__ = "item"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    description: Mapped[str]
    value: Mapped[int]

    def __repr__(self):
        return f"Item(id={self.id!r}, name={self.name!r}, description={self.description!r}, value={self.value!r})"

Base.metadata.create_all(engine)

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
    new_item = Item(
        name=name,
        description=description,
        value=value
    )
    with Session(engine) as session:
        session.add(new_item)
        session.commit()
        print("Successfully added item to the database!")

def read_items():
    with Session(engine) as session:
        result = session.execute(select(Item)).all()
    return result

def print_items(result):
    for item_row in result:
        item = item_row[0]
        print(f"[{item.id}] {item.name} - {item.description} (value: {item.value})")

def update_item(item_id, item_name=None, item_description=None, item_value=None):
    with Session(engine) as session:
        item = session.get(Item, item_id)
        if item_name:
            if item:
                item.name = item_name
                print("Successfully updated item name!")
            else:
                print("Failed to update the name of the item!")
        elif item_description:
            if item:
                item.description = item_description
                print("Successfully updated item description!")
            else:
                print("Failed to update the description of the item!")
        elif item_value:
            if item:
                item.value = item_value
                print("Successfully updated item value!")
            else:
                print("Failed to update the value of the item!")
        session.commit()

def delete_item(item_id):
    with Session(engine) as session:
        item = session.get(Item, item_id)
        if item:
            session.delete(item)
            session.commit()
            print("Successfully deleted item!")
            return True
    return False

def print_menu():
    print("Welcome to items db!")
    print("Version: 2.0")
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
    for item_row in items:
        item = item_row[0]
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
        status = delete_item(item_id)
        if not status:
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
