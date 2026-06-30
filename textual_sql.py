from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.orm import Session

engine = create_engine("sqlite+pysqlite:///:memory:")
engine.echo = True

persons = [
        {"name": "John", "age": 20},
        {"name":"Alex", "age": 18},
        {"name": "Alexis", "age": 16},
        {"name": "Brandon", "age": 25}
]
print("Commit as you go style:")
with engine.connect() as conn:
    conn.execute(text("CREATE TABLE Persons (name str, age int)"))
    conn.execute(text(
        """
        INSERT INTO
            Persons (name, age)
            VALUES(:name, :age)
        """),
        persons
    )
    result = conn.execute(text("SELECT * FROM Persons"))
    print(result.all())
    conn.commit()

print("Begin once style:")
with engine.begin() as conn:
    conn.execute(
        text(
        """
        INSERT INTO
            Persons (name, age)
            VALUES(:name, :age)
        """),
        persons
    )
    result = conn.execute(text("SELECT * FROM Persons"))
    print(result.all())

    print("Fetching rows:")
    result = conn.execute(text("SELECT name, age FROM Persons"))
    for row in result:
        print(f"name: {row.name}, age: {row.age}")

    print("Fetch rows via tuple assignment:")
    result = conn.execute(text("SELECT name, age FROM Persons"))
    for name, age in result:
        print(name, age)

    print("Fetch rows via tuple indexing:")
    result = conn.execute(text("SELECT name, age FROM Persons"))
    for row in result:
        name = row[0]
        age = row[1]
        print(name, age)

    print("Fetch rows via Attribute Name:")
    result = conn.execute(text("SELECT name, age FROM Persons"))
    for row in result:
        age = row.age
        print(f"Row: {row.name} {age}")

    print("Fetch rows via Mapping Access dictionaries:")
    result = conn.execute(text("SELECT name, age FROM Persons"))
    for dict_row in result.mappings():
        print(f"{dict_row['name']} {dict_row['age']}")

    print("Sending Parameters:")
    result = conn.execute(text("SELECT name, age FROM Persons WHERE age > :age"), {"age": 18})
    for row in result.mappings():
        print(f"name: {row['name']}, age: {row['age']}")

    print("Sending Multiple Parameters:")
    result = conn.execute(text(
        """
        INSERT INTO Persons VALUES (:name, :age)
        """),
        [

            {"name":"Max", "age": 35},
            {"name":"Peter", "age": 19},
            {"name":"Daniel", "age": 14},
            {"name":"Katie", "age": 40}
        ]
    )
    result = conn.execute(text("SELECT * FROM Persons"))
    for name, age in result:
        print(name, age)

print()
print("----------------------------------")
print("| Executing with an ORM Session  |")
print("----------------------------------")
print()

with Session(engine) as session:
    result = session.execute(text("SELECT name, age FROM Persons WHERE age < :age"), {"age": 20})
    for name, age in result:
        print(name, age)
    session.execute(text("UPDATE Persons SET age=:age WHERE name=:name"), {"name": "John", "age": 18})
    result = session.execute(text("SELECT * from Persons"))
    for name, age in result:
        print(name, age)
    session.commit()
