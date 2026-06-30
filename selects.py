from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import Table, Column, String, Integer
from sqlalchemy import insert, select
from sqlalchemy import ForeignKey
from sqlalchemy import func, cast, desc
from sqlalchemy import text
from sqlalchemy import literal_column
from sqlalchemy import and_, or_
from sqlalchemy import union_all
from sqlalchemy import JSON
from sqlalchemy import type_coerce
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import Session
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import aliased
from sqlalchemy.dialects import mysql

engine = create_engine("sqlite+pysqlite:///:memory:")
engine.echo = True

meta_data = MetaData()
user_table = Table(
        "user_account",
        meta_data,
        Column("id", Integer, primary_key=True),
        Column("name", String(30)),
        Column("age", Integer)
)

address_table = Table(
        "address",
        meta_data,
        Column("id", Integer, primary_key=True),
        Column("user_id", Integer, ForeignKey("user_account.id")),
        Column("email_address", String)
)

meta_data.create_all(engine)

user_data = [
        {
            "user_id": 1,
            "name": "John", "age": 21,
            "email_address": "johndoe@gmail.com"
        },
        {
            "user_id": 2,
            "name": "Alex", "age": 18,
            "email_address": "alex19@gmail.com"
        },
        {
            "user_id": 3,
            "name": "Katie", "age": 25,
            "email_address": "katie1956@gmail.com"
        }
]

with engine.begin() as conn:
    statement = insert(user_table)
    conn.execute(statement, user_data)
    
    statement = insert(address_table)
    conn.execute(statement, user_data)

print("Selecting data:")
statement = select(user_table).where(user_table.c.name == "Alex")
print(statement)

with engine.connect() as conn:
    result = conn.execute(statement)
    for row in result:
        print(row)

# Create ORM Table
print("------------------")
print("Using ORM")
print("------------------")
class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "orm_user_account"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    age: Mapped[int]

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, age={self.age!r})"

class Address(Base):
    __tablename__ = "orm_address"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("orm_user_account.id"))
    email_address: Mapped[str]

    def __repr__(self) -> str:
        return f"Address(id={self.id!r}, user_id={self.user_id!r}, email_address={self.email_address!r})"

print("Creating Orm User account and Address table:")
Base.metadata.create_all(engine)
Address.metadata.create_all(engine)

with Session(engine) as session:
    user_id = 1
    for row in user_data:
        name = row["name"]
        age = row["age"]
        email_address = row["email_address"]

        new_user = User(name=name, age=age)
        session.add(new_user)

        new_address = Address(
                user_id=user_id,
                email_address=email_address
        )
        session.add(new_address)
        user_id += 1

    session.commit()

print("Selecting with ORM by using Session:")
statement = select(User).where(User.name == "Katie")
with Session(engine) as session:
    result = session.execute(statement)
    for row in result:
        print(row)

print("Setting the Columns and FROM clause:")
print(select(user_table))

print("Selecting from individual columns using Core approach:")
print(select(user_table.c.name, user_table.c.age))

print("Selecting from individual columns using From clause with a tuple of string names:")
print(select(user_table.c["name", "age"]))

print("-------------------------------------")
print("Selecting ORM Entities and Columns")
print("-------------------------------------")
print(select(User))

print("Executing with ORM:")
with Session(engine) as session:
    row = session.execute(select(User)).first()
    print(row)
    print(repr(row))
    user = row[0]
    print(user.id, user.name, user.age)

    print("Selecting using scalars method:")
    user = session.scalars(select(User)).first()
    print(user)

    print("Selecting individual columns of an ORM entity as distinct elements:")
    statement = select(User.name, User.age)
    print(statement)
    row = session.execute(statement).first()
    print(row)

    print("Selecting / Mixing attributes of another entity on another table:")
    statement = (
            select(User.name, Address).
            where(User.id == Address.user_id).
            order_by(Address.id)
    )
    print(statement)
    result = session.execute(statement).all()
    print(result)

print("----------------------------------------")
print("Selecting from Labeled SQL Expressions:")
print("----------------------------------------")
statement = select(
        ("Username: " + user_table.c.name).label("username")
).order_by(user_table.c.name)

with engine.connect() as conn:
    for row in conn.execute(statement):
        print(f"{row.username}")

    print("Selecting with Textual Column Expressions:")
    statement = select(
        text("'someone phrase'"),
        user_table.c.name
    ).order_by(user_table.c.name)
    result = conn.execute(statement)
    print(result.all())

    print("Selecting with Literal COLUMN Expressions:")
    statement = (
            select(literal_column("'some phrase'").
            label("p"), user_table.c.name).
            order_by(user_table.c.name)
    )
    result = conn.execute(statement)
    for row in result:
        print(f"{row.p} {row.name}")

print("-----------------")
print("The Where Clause")
print("-----------------")
print(user_table.c.name == "squidward")
print(address_table.c.user_id > 10)

print("Generating Where clause by using resulting objects:")
print(select(user_table).where(user_table.c.name == "Alex"))

print("Invoking multiple expressions joined by and with where method:")
print(
    select(address_table.c.email_address)
    .where(user_table.c.name == "John")
    .where(address_table.c.user_id == user_table.c.id)
)

print("Passing multiple expressions to where method:")
print(
    select(address_table.c.email_address).
    where(
        user_table.c.name == "John",
        address_table.c.user_id == user_table.c.id
    )
)

print("AND and OR conjunctions:")
print(
        select(Address.email_address).
        where(
            and_(
                or_(User.name == "John", User.name == "Katie"),
                Address.user_id == User.id
            )
        )
)

print("Parenthesis / order of operations:")
print(
        select(Address.email_address).
        where(
            or_(
                User.name == "Alex",
                and_(Address.user_id == User.id, User.name == "Katie")
            )
        )
)

print("Select Filtering:")
print(
        select(User).
        filter_by(name="Alex", age=18)
)
print("----------------------------------")
print("Explicit FROM clauses and JOINS")
print("----------------------------------")
print("Selecting a single column includes table in from clause:")
print(select(user_table.c.name))

print("Selecting two columns from two tables includes both tables in from clause:")
print(select(user_table.c.name, address_table.c.email_address))

print("Selecting and Joining two tables with join_from():")
print(
        select(user_table.c.name, address_table.c.email_address)
            .join_from(
                user_table, address_table
            )
)

print("Selecting and Joining two tables with join():")
print(
        select(user_table.c.name, address_table.c.email_address).
        join(
            address_table
        )
)

print("Adding elements to the From clause explicitly:")
print(
    select(address_table.c.email_address).
    select_from(user_table).
    join(address_table)
)

print("Using select_from method to use Count sql expression:")
print(
        select(func.count("*")).
        select_from(user_table)
)

print("Setting the ON clause manually:")
print(
        select(address_table.c.email_address)
        .select_from(user_table)
        .join(address_table,
              user_table.c.id == address_table.c.user_id)
)

print("Outer and Full Join:")
print(
    select(user_table).
    join(address_table, isouter=True)
)

print("Order By, Group By, Having:")
statement = (
        select(user_table).
        order_by(user_table.c.name)
)
print(statement)

with engine.connect() as conn:
    result = conn.execute(statement)
    for row in result:
        print(row)

    print("Order by ascending or descending:")
    print("Descending order example:")
    statement = (
        select(User).order_by(User.name.desc())
    )
    print(statement)

    result = conn.execute(statement)
    for row in result:
        print(row)

print("Aggregate functions with GROUP BY / HAVING:")
count_fn = func.count(user_table.c.id)
print(count_fn)

print("Group By example:")
with engine.connect() as conn:
    result = conn.execute(
        select(User.name, func.count(Address.id).label("count"))
        .join(Address)
        .group_by(User.name)
        .having(func.count(Address.id) > 1)
    )
    print(result.all())
print("Ordering or Grouping by a Label:")
statement = (
        select(Address.user_id, func.count(Address.id).label("num_addresses"))
        .group_by("user_id")
        .order_by("user_id", desc("num_addresses"))
)
print(statement)

print("-------------------")
print("Using Aliases")
print("-------------------")
user_alias_1 = user_table.alias()
user_alias_2 = user_table.alias()
print(
        select(
            user_alias_1.c.name, user_alias_2.c.name
        ).join_from(
            user_alias_1, user_alias_2,
            user_alias_1.c.id > user_alias_2.c.id
        )
)

print("----------------------")
print("Orm Entity Aliases")
print("----------------------")
address_alias_1 = aliased(Address)
address_alias_2 = aliased(Address)
print(
        select(User).
        join_from(User, address_alias_1)
        .where(address_alias_1.email_address == "alex19@gmail.com")
        .join_from(User, address_alias_2)
        .where(address_alias_2.email_address == "alex19@aol.com")
)

print("----------------------------")
print("Subqueries and CTEs")
print("----------------------------")
print("Selecting with subquery utilizing aggregate functions:")
subq = (
        select(
            func.count(
                address_table.c.id
            )
            .label("count"),
            address_table.c.user_id
        )
        .group_by(address_table.c.user_id)
        .subquery()
)
print(subq)

print("Subquery object behaves like any other FROM object usch as Table:")
print(select(subq.c.user_id, subq.c.count))

print("Applying subquery object to a larger select statement that will join the data to the user_account table")
statement = (
    select(
        user_table.c.name,
        user_table.c.age,
        subq.c.count
    ).join_from(
        user_table, subq
    )
)
print(statement)

print("-------------------------------")
print("Common Table Expressions (CTES)")
print("-------------------------------")
subq = (
    select(
        func.count(address_table.c.id)
        .label(
            "count"
        ),
        address_table.c.user_id
    )
    .group_by(
        address_table.c.user_id
    )
    .cte()
)

statement = (
    select(
        user_table.c.name,
        user_table.c.age,
        subq.c.count
    )
    .join_from(
        user_table, subq
    )
)
print(statement)

print("ORM Entity Subqueries/CTES:")
print("Applying aliased() to the Subquery construct:")
subq = (
    select(
        Address
    )
    .where(
        ~Address.email_address
        .like("%@aol.com")
    )
    .subquery()
)
address_subq = aliased(
    Address,
    subq
)

statement = (
        select(User, address_subq)
        .join_from(User, address_subq)
        .order_by(User.id, address_subq.id)
)

with Session(engine) as session:
    result = session.execute(statement)
    for user, address in result:
        print(f"{user} {address}")
print("CTE Construct alternative:")
cte_obj = (
    select(Address)
    .where(
        ~Address.email_address
        .like("%@aol.com")
    )
    .cte()
)
address_cte = aliased(Address, cte_obj)
statement = (
    select(User, address_cte)
    .join_from(User, address_cte)
    .order_by(User.id, address_cte.id)
)
with Session(engine) as session:
    result = session.execute(statement)
    for user, address in result:
        print(f"{user} {address}")

print("------------------------------------")
print("Scalar and Correlated Subqueries")
print("------------------------------------")
print("Scalar subquery example:")
subq = (
    select(
        func.count(address_table.c.id)
    )
    .where(
        user_table.c.id == address_table.c.user_id
    )
    .scalar_subquery()
)
print(subq)
print("Example of Column Element SQL Expression:")
print(subq == 5)

print("Tables are automatically correlated in scalar subqueries:")
statement = select(
    user_table.c.name,
    subq.label("address_count")
)
print(statement)
print("Specifying Correlation:")
"""
Proving concept:
InvalidRequestError
statement = (
    select(
        user_table.c.name,
        address_table.c.email_address,
        subq.label("address_count")
    )
    .join_from(user_table, address_table)
    .order_by(user_table.c.id, address_table.c.id)
)
print(statement)
"""

subq = (
    select(func.count(address_table.c.id))
    .where(
        user_table.c.id == address_table.c.user_id
    )
    .scalar_subquery()
    .correlate(user_table)
)

with engine.connect() as conn:
    result = conn.execute(
        select(
            user_table.c.name,
            address_table.c.email_address,
            subq.label("address_count")
        )
        .join_from(user_table, address_table)
        .order_by(
            user_table.c.id,
            address_table.c.id
        )
    )
    print(result.all())

print("-----------------------------------------")
print("Union, Union All and other set options")
print("-----------------------------------------")
statement1 = (
    select(user_table)
    .where(user_table.c.name == "Alex")
)
statement2 = (
    select(user_table)
    .where(user_table.c.name == "Katie")
)
u = union_all(statement1, statement2)
with engine.connect() as conn:
    result = conn.execute(u)
    print(result.all())

print("Using Compound Selects as a subquery:")
u_subq = u.subquery()
statement = (
    select(
        u_subq.c.name,
        address_table.c.email_address
    )
    .join_from(address_table, u_subq)
    .order_by(
        u_subq.c.name,
        address_table.c.email_address
    )
)
with engine.connect() as conn:
    result = conn.execute(statement)
    print(result.all())

print("Selecting ORM Entities from Unions:")
statement1 = select(User).where(User.name == "John")
statement2 = select(User).where(User.name == "Alex")
u = union_all(statement1, statement2)

orm_statement = select(User).from_statement(u)
with Session(engine) as session:
    result = session.execute(orm_statement)
    for obj in result:
        print(obj)

print("Utilizing flexibility of Union or other Set Related Constructs:")
user_alias = aliased(User, u.subquery())
orm_statement = select(user_alias).order_by(user_alias.id)
with Session(engine) as session:
    result = session.execute(orm_statement).scalars()
    for obj in result:
        print(obj)

print("Exists subqueries:")
subq = (
    select(
        func.count(address_table.c.id)
    )
    .where(
        user_table.c.id == address_table.c.user_id
    )
    .group_by(address_table.c.user_id)
    .having(
        func.count(address_table.c.id) > 1
    )
).exists()
with engine.connect() as conn:
    result = conn.execute(
        select(user_table.c.name)
        .where(subq)
    )
    print(result.all())

print("Negation of Exists:")
subq = (
    select(address_table.c.id)
    .where(
        user_table.c.id == address_table.c.user_id
    )
).exists()

with engine.connect() as conn:
    result = conn.execute(
        select(user_table.c.name)
        .where(~subq)
    )
    print(result.all())

print("------------------------------")
print("Working with SQL Functions:")
print("------------------------------")
print("1. The count function (counts how many rows are returned):")
print(select(func.count()).select_from(user_table))
print("2. The lower function (Converts a string to lowercase):")
print(select(func.lower()).select_from(user_table))
print("3. The now function (Returns the current date and time):")
statement = select(func.now())
with engine.connect() as conn:
    result = conn.execute(statement)
    print(result.all())
print("Any name that is accessed from the func() namespace is considered to be a SQL function.")
print(select(func.some_function(user_table.c.name, 17)))

print("Functions have return types:")
print(func.now().type)
print(func.run_some_calculation().type)

print("Creating and applying a specific type for a function:")
function_expr = func.json_object('{a, 1, b, "def", c, 3.5}', type_=JSON)
statement = select(function_expr["def"])
print(statement)

print("Built in Functions have Pre-Configured Return Types:")
m1 = func.max(Column("some_int", Integer))
print(m1.type)

m2 = func.max(Column("some_str", String))
print(m2.type)

print(func.now().type)
print(func.current_date().type)

print(func.concat("x", "y").type)

print(func.upper("lowercase").type)

print(select(func.upper("lowercase") + " suffix"))

print(func.count().type)
print(func.json_object('{"a", "b"}').type)

print("Using Window Functions:")
statement = (
    select(
        func.row_number().over(
            partition_by=user_table.c.name
        ),
        user_table.c.name,
        address_table.c.email_address
    )
    .select_from(user_table)
    .join(address_table)
)

with engine.connect() as conn:
    result = conn.execute(statement)
    print(result.all())

print("ORDER BY using .over.order_by():")
statement = (
    select(
        func.count().over(
            order_by=user_table.c.name
        ),
        user_table.c.name,
        address_table.c.email_address
    )
    .select_from(user_table)
    .join(address_table)
)
with engine.connect() as conn:
    result = conn.execute(statement)
    print(result.all())

print("Special Modifiers within group, filter:")
print("Within group():")
print(
    func.unnest(
        func.percentile_disc([0.25, 0.5, 0.75, 1])
        .within_group(user_table.c.name)
    )
)
print("Filter():")
statement = (
    select(
        func.count(
            address_table.c.email_address
        )
        .filter(
            user_table.c.name == "Katie"
        ),
        func.count(
            address_table.c.email_address
        ).filter(
            user_table.c.name == "Alex"
        )
    )
    .select_from(user_table)
    .join(address_table)
)
with engine.connect() as conn:
    result = conn.execute(statement)
    print(result.all())

print("Table Valued Functions:")
onetwothree = func.json_each('["one", "two", "three"]').table_valued("value")
statement = (
    select(onetwothree)
    .where(
        onetwothree.c.value.in_(
            ["two", "three"]
        )
    )
)
with engine.connect() as conn:
    result = conn.execute(statement)
    print(result.all())
print("Column Valued Functions - Table Valued function as a scalar column:")
statement = (
    select(
        func.json_array_elements(
            '["one", "two"]'
        )
        .column_valued(
            "x"
        )
    )
)
print(statement)

print("Data Casts and Type Coercion:")
statement = select(
    cast(user_table.c.id, String)
)
with engine.connect() as conn:
    result = conn.execute(statement)
    print(result.all())


print("Casting to a givn python data type:")
print(cast("{'a': 'b'}", JSON)["a"])

print("type_coerce - a Python only cast")
statement = (
    select(
        type_coerce(
            {
                "some_key": {
                    "foo": "bar"
                }
            },
            JSON
        )["some_key"]
    )
)
print(statement.compile(dialect=mysql.dialect()))
