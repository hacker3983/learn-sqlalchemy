from sqlalchemy import create_engine
from sqlalchemy import Table, Column
from sqlalchemy import String, Integer
from sqlalchemy import MetaData
from sqlalchemy import insert, select
from sqlalchemy import update, delete
from sqlalchemy import bindparam
from sqlalchemy import ForeignKey

engine = create_engine("sqlite+pysqlite:///:memory:")
engine.echo = True

metadata_obj = MetaData()

user_table = Table(
    "user_account",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("name", String(40)),
    Column("age", Integer)
)

address_table = Table(
    "address",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("user_account.id")),
    Column("email_address", String)
)

some_table = Table(
    "some_table",
    metadata_obj,
    Column("x", Integer),
    Column("y", Integer)
)

metadata_obj.create_all(engine)

user_data = [
        {"name": "John", "age": 18,
         "email_address": "john@gmail.com"},
        {"name": "Alex", "age": 16,
         "email_address": "alex@gmail.com"},
        {"name": "Max", "age": 21,
         "email_address": "max@gmail.com"},
        {"name": "Katie", "age": 19,
         "email_address": "katie@gmail.com"},
        {"name": "Peter", "age": 22,
         "email_address": "peter@gmail.com"},
        {"name": "Tiana", "age": 20,
         "email_address": "tiana@gmail.com"
        }
]
print("==============================")
print("Update and Delete statements")
print("==============================")
with engine.begin() as conn:
    conn.execute(insert(user_table), user_data)
    conn.execute(insert(address_table), user_data)
    result = conn.execute(select(user_table)).all()
    print("Getting inserted data:")
    for user in result:
        print(user)

print("Basic Update:")
statement = (
    update(user_table)
    .where(user_table.c.name == "Peter")
    .values(age=20)
)
print(statement)

print("Update with values method:")
statement = (
    update(user_table)
    .values(name="Username: " + user_table.c.name)
)
print(statement)

print("Update with bindparam() bound parameters:")
statement = (
    update(user_table)
    .where(
        user_table.c.name == bindparam("oldname")
    )
    .values(name=bindparam("newname"))
)
with engine.begin() as conn:
    conn.execute(
        statement,
        [
            {"oldname": "Peter", "newname": "Jack"},
            {"oldname": "Alex", "newname": "Alexis"}
        ]
    )
    result = conn.execute(
        select(user_table)
    ).all()
    for user in result:
        print(user)

print("Correlated Updates via Correlated subquery:")
scalar_subq = (
    select(address_table.c.email_address)
    .where(
        address_table.c.user_id == user_table.c.id
    )
    .order_by(address_table.c.id)
    .limit(1)
    .scalar_subquery()
)

update_statement = update(user_table).values(age=scalar_subq)
print(update_statement)

print("Update From:")
update_statement = (
    update(user_table)
    .where(user_table.c.id == address_table.c.user_id)
    .where(address_table.c.email_address == "max@gmail.com")
    .values(name="M")
)
print(update_statement)

print("Update multiple tables mysql syntax:")
from sqlalchemy.dialects import mysql
print(update_statement.compile(dialect=mysql.dialect()))

print("Update From and Values combined:")
from sqlalchemy import Values

values = Values(
    user_table.c.id,
    user_table.c.name,
    name="my_values"
).data(
    [
        (1, "new_name"),
        (2, "another_name"),
        (3, "name_name")
    ]
)
update_statement = (
    user_table.update()
    .values(
        name=values.c.name
    )
    .where(
        user_table.c.id == values.c.id
    )
)
from sqlalchemy.dialects import postgresql
print(update_statement.compile(dialect=postgresql.dialect()))

print("Parameter Order Updates:")
update_statement = (
    update(some_table)
    .ordered_values(
        (some_table.c.y, 20),
        (some_table.c.x, some_table.c.y + 10)
    )
)
print(update_statement)

print("====================")
print("Delete Statements")
print("====================")
statement = (
    delete(user_table)
    .where(user_table.c.name == "John")
)
print(statement)

print("Multiple Table Deletes My SQL:")
delete_statement = (
    delete(user_table)
    .where(user_table.c.id == address_table.c.user_id)
    .where(address_table.c.email_address == "john@gmail.com")
)
print(delete_statement.compile(dialect=mysql.dialect()))
print("Getting affected row count from update, delete:")
with engine.begin() as conn:
    result = conn.execute(
        update(user_table)
        .values(age=19)
        .where(user_table.c.name == "John")
    )
    print(result.rowcount)

print("Utilizing Returning with Update, Delete:")
update_statement = (
    update(user_table)
    .where(user_table.c.name == "John")
    .values(name="John the One")
    .returning(user_table.c.id, user_table.c.name)
)
print(update_statement)

delete_statement = (
    delete(user_table)
    .where(user_table.c.name == "John")
    .returning(user_table.c.id, user_table.c.name)
)
print(delete_statement)
