from sqlalchemy import create_engine
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy import select, update
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Session

engine = create_engine("sqlite+pysqlite:///:memory:")
engine.echo = True

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user_account"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    age: Mapped[int] = mapped_column(Integer)

    def __repr__(self):
        return f"User(id={self.id!r}, name={self.name!r}, age={self.age!r})"


class Address(Base):
    __tablename__ = "address"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey(User.id))
    email_address: Mapped[str] = mapped_column(String)

    def __repr__(self):
        return f"Address(id={self.id!r}, user_id={self.user_id!r}, email_address={self.email_address!r})"

Base.metadata.create_all(engine)

print("Inserting Rows using the ORM unit of work pattern:")
user_a = User(name="John", age=19)
user_b = User(name="Max", age=20)
user_c = User(name="Alex", age=18)
user_d = User(name="Katie", age=21)
print(user_a)
print(user_b)

print("Adding objects to a Session without context manager we must close it manually:")
session = Session(engine)
session.add(user_a)
session.add(user_b)
session.add(user_c)
session.add(user_d)
print("Seeing pending objects state with session:")
print(session.new)

print("Pushing / Flushing changes to database:")
session.flush()
print("Flushing changes using session.commit():")
session.commit()

print("Getting id for inserted objects:")
print(user_a, "id:", user_a.id)
print(user_b, "id:", user_b.id)
print(user_c, "id:", user_c.id)
print(user_d, "id:", user_d.id)

print("Getting Objects by the Primary Key from the Identity Map:")
some_user = session.get(User, 4)
print(some_user)
print(some_user is user_d)
some_user = session.get(User, 2)
print(some_user)
print(some_user is user_a)
print("Commiting:")
session.commit()

print("======================================================")
print("Updating ORM objects using the Unit of Work pattern")
print("======================================================")
alex = session.execute(select(User).filter_by(name="Alex")).scalar_one()
print(alex)

print("Altering attributes of an object is reflected:")
alex.age = 20
print(alex)

print("Altering object becomes part of Session.dirty:")
print(session.dirty)
print(alex in session.dirty)

print("After a flush the changes or altered attributes are updated flushes are done automatically:")
alex_age = session.execute(select(User.age).where(User.name == "Alex")).scalar_one()
print("Alex age:", alex_age)

print("Checking dirty status:")
print(alex in session.dirty)


print("===============================================")
print("Deleting ORM objects with Unit of Work Pattern")
print("===============================================")

print("Deleting the user John:")
john = session.get(User, 1)
print(john)
print("Marking for deletion nothing happens until flushed:")
session.delete(john)
print("Flushing by executing query:")
result = session.execute(select(User).where(User.name == "John")).first()
print(result)

print("Rolling back:")
session.rollback()

print("Inspecting expiration process of objects after a rollback:")
print(john.__dict__)

print(john.name)

print("Inspecting population process:")
print(john.__dict__)

print("Checking identity:")
print(john in session)

print("Commiting changes:")
session.commit()
print("Closing sessions with no context manager with:")
session.close()

print("Checking expiry state after closing session:")
#print(john.name)

print("Reassignment of detached objects:")
session.add(john)
print(john.name)
