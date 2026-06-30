from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String
from sqlalchemy import MetaData
from sqlalchemy import insert
from sqlalchemy import select, bindparam
from sqlalchemy import ForeignKey

engine = create_engine("sqlite+pysqlite:///:memory:")
engine.echo = True

metadata_obj = MetaData()
user_table = Table(
        "user_account",
        metadata_obj,
        Column("id", Integer, primary_key=True),
        Column("name", String(30)),
        Column("fullname", String)
)

metadata_obj.create_all(engine)

print("insert statements core:")
statement = insert(user_table).values(name="John", fullname="John Doe")
print(statement)

print("Compiling statement:")
compiled = statement.compile()
print(compiled)
print(compiled.params)

print("Executing statement:")
with engine.connect() as conn:
    result = conn.execute(statement)
    print("Getting primary_key:")
    print(result.inserted_primary_key)
    conn.commit()

print("Inserts generate the values clause automatically:")
print(insert(user_table))

print("Inserting multiple values at once:")
with engine.connect() as conn:
    result = conn.execute(
        insert(user_table),
        [
            {"name": "Alex", "fullname": "Alex Francis"},
            {"name": "Kevin", "fullname": "Kevin Bradshaw"}
        ]
    )
    conn.commit()


print("Advanced concept scalar subquery insert when a particular column doesn't exist within a table:")
address_table = Table(
        "address",
        metadata_obj,
        Column("id", Integer, primary_key=True),
        Column("user_id", Integer, ForeignKey("user_account.id"), nullable=False),
        Column("email_address", String)
)
metadata_obj.create_all(engine)

scalar_subq = (
        select(user_table.c.id).
        where(user_table.c.name == bindparam("username"))
        .scalar_subquery()
)

with engine.connect() as conn:
    result = conn.execute(
            insert(address_table).values(
                user_id = scalar_subq
            ),
            [
                {"username": "John", "email_address": "johndoe@gmail.com"},
                {"username": "Alex", "email_address": "alex21@gmail.com"},
                {"username": "Kevin", "email_address": "kevin91@gmail.com"}
            ]
    )
    conn.commit()

print("Empty Inserts:")
print(insert(user_table).values().compile(engine))

print("Insert and Returning last created primary key:")
insert_statement = insert(address_table).returning(
        address_table.c.id, address_table.c.email_address
)
print(insert_statement)


print("Insert.from Select combination:")
select_statement = select(user_table.c.id, user_table.c.name + "@gmail.com")
insert_statement = insert(address_table).from_select(
        ["user_id", "email_address"],
        select_statement
)
print(insert_statement.returning(address_table.c.id, address_table.c.email_address))
