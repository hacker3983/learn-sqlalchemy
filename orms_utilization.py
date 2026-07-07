from sqlalchemy import create_engine
from sqlalchemy import Integer, String
from sqlalchemy import ForeignKey
from sqlalchemy import select
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import Session
from sqlalchemy.orm import relationship
from sqlalchemy.orm import selectinload
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import contains_eager
from typing import List
from sqlalchemy.orm import Session

engine = create_engine("sqlite+pysqlite:///:memory:")
session = Session(engine)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user_account"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    age: Mapped[int]

    addresses: Mapped[List['Address']] = relationship(back_populates="user", lazy="selectin")

    def __repr__(self):
        return f"User(id={self.id!r}, name={self.name!r}, age={self.age!r})"

class Address(Base):
    __tablename__ = "address"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_account.id"))
    email_address: Mapped[str]

    user: Mapped["User"] = relationship(back_populates="addresses")

    def __repr__(self):
        return f"Address(id={self.id!r}, user_id={self.user_id!r}, email_address={self.email_address!r})"
print("Creating database tables!")
Base.metadata.create_all(engine)

print("====================================")
print("Working with ORM related objects")
print("====================================")
print("Persisting and loading relationships:")
u1 = User(name="John Doe", age=29)
print(u1.addresses)

a1 = Address(email_address="johndoe@gmail.com")
u1.addresses.append(a1)
print(u1.addresses)
print(a1.user)

a2 = Address(email_address="john21@icloud.com", user=u1)
print(u1.addresses)


# Equivalent modification
a2.user = u1
print(u1.addresses)

print("Cascading objects into the session:")
session.add(u1)
print("User 1 exists in session?")
print(u1 in session)

print("Address 1 exists in session?")
print(a1 in session)

print("Address 2 exists in session?")
print(a2 in session)

print("Before assigning to a real database row:")
print(u1.id)
print(a1.user_id)

print("Turning on loggin:")
engine.echo = True

print("Commiting session:")
session.commit()

print("======================")
print("Loading relationships:")
print("======================")
print(u1.id)

print("Lazying loading demo")
print(u1.addresses)

print("Due to lazy loading after populating data no more sql statements are executed:")
print(u1.addresses)

print("Address 1:", a1)
print("Address 2:", a2)

print("==============================")
print("Using Relations in queries")
print("==============================")
print("Using Relationships to Join:")
print(
    select(Address.email_address)
    .select_from(User)
    .join(User.addresses)
)

print("The ORM relationship mapping is not utilized by Select.join() or Select.join_from():")
print(
    select(Address.email_address)
    .join_from(User, Address)
)

print("===================")
print("Loader Strategies")
print("===================")
for user_obj in session.execute(
    select(User).options(
        selectinload(User.addresses)
    )
).scalars():
    print(user_obj.addresses)

print("Relationship.lazy option inside class.")

print("Selectin load stragety:")
statement = (
    select(User)
    .options(selectinload(User.addresses))
    .order_by(User.id)
)
for row in session.execute(statement):
    print(
        f"{row.User.name} ({', '.join(a.email_address for a in row.User.addresses)}))"
    )

print("Joined Load:")
statement = (
    select(Address)
    .options(
        joinedload(
            Address.user,
            innerjoin=True
        )
    )
    .order_by(Address.id)
)
for row in session.execute(statement):
    print(f"{row.Address.email_address} {row.Address.user.name}")

print("Explicit Join + Eager loading:")

statement = (
    select(Address)
    .join(Address.user)
    .where(User.name == "John")
    .options(contains_eager(Address.user))
    .order_by(Address.id)
)

for row in session.execute(statement):
    print(f"{row.Address.email_address} {row.Address.user.name}")

print("Applying Joined load separately:")
statement = (
    select(Address)
    .join(Address.user)
    .where(User.name == "John")
    .options(joinedload(Address.user))
    .order_by(Address.id)
)
print(statement)

print("Raiseload:")
#Ref: https://docs.sqlalchemy.org/en/20/tutorial/orm_related_objects.html
"""
>>> from sqlalchemy.orm import Mapped
>>> from sqlalchemy.orm import relationship


>>> class User(Base):
...     __tablename__ = "user_account"
...     id: Mapped[int] = mapped_column(primary_key=True)
...     addresses: Mapped[List["Address"]] = relationship(
...         back_populates="user", lazy="raise_on_sql"
...     )


>>> class Address(Base):
...     __tablename__ = "address"
...     id: Mapped[int] = mapped_column(primary_key=True)
...     user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
...     user: Mapped["User"] = relationship(back_populates="addresses", lazy="raise_on_sql")
>>> u1 = session.execute(select(User)).scalars().first()
SELECT user_account.id FROM user_account
[...] ()
>>> u1.addresses
Traceback (most recent call last):
...
sqlalchemy.exc.InvalidRequestError: 'User.addresses' is not available due to lazy='raise_on_sql'

>>> u1 = (
...     session.execute(select(User).options(selectinload(User.addresses)))
...     .scalars()
...     .first()
... )
SELECT user_account.id
FROM user_account
[...] ()
SELECT address.user_id AS address_user_id, address.id AS address_id
FROM address
WHERE address.user_id IN (?, ?, ?, ?, ?, ?)
[...] (1, 2, 3, 4, 5, 6)
"""

print("Closing session:")
session.close()
