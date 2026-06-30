from typing import List
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import Table, Column, Integer, String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

engine = create_engine("sqlite+pysqlite:///:memory:")
engine.echo = True
metadata_obj = MetaData()
#print(metadata_obj)
#print(dir(metadata_obj))

user_table = Table(
        "user_account",
        metadata_obj,
        Column("id", Integer, primary_key=True),
        Column("name", String(30)),
        Column("phone_number", String)
)
#print(user_table)
#print(dir(user_table))
print("Accessing table columns and properties:")
print(user_table.c.name)
print(user_table.c.keys())

print("Getting the column associated with the primary key:")
print(user_table.primary_key)

print("Foreign Key Constraints:")
address_table = Table(
        "address",
        metadata_obj,
        Column("id", Integer, primary_key=True),
        Column("user_id", ForeignKey("user_account.id"), nullable=False),
        Column("email_address", String, nullable=False)
)
print("Emitting or sending out DDL (DATA DEFINITION LANGUAGE) to the database to construct SQL statements from our defined data or objects")
metadata_obj.create_all(engine)

print("Dropping all DDLS or commands:")
metadata_obj.drop_all(engine)
print("----------------------------------------")
print("Utilizing ORM Declarative Forms to define table meta data:")
print("----------------------------------------")
print("Establishing a Declarative Base:")
class Base(DeclarativeBase):
    pass

print("Base metadata:")
print(Base.metadata)
print("Base registry (central mapper configuration unit):")
print(Base.registry)

print("Declaring ORM Mapped Classes:")

class User(Base):
    __tablename__ = "user_account"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30)) 
    fullname: Mapped[Optional[str]]

    addresses: Mapped[List["Address"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"

class Address(Base):
    __tablename__ = "address"

    id: Mapped[int] = mapped_column(primary_key=True)
    email_address: Mapped[str]
    user_id = mapped_column(ForeignKey("user_account.id"))

    user: Mapped[User] = relationship(back_populates="addresses")

    def __repr__(self) -> str:
        return f"Address(id={self.id!r}, email_address={self.email_address!r})"

print("Creating an ORM data value:")
new_user = User(name="John", fullname="John Doe")
print(new_user)

print("-----------------------")
print("Table Reflections:")
print("-----------------------")
some_table = Table(
    "some_table",
    metadata_obj,
    Column("id", Integer, primary_key=True),
    Column("name", String(30))
)
metadata_obj.create_all(engine)
some_table = Table("some_table",
            metadata_obj,
            autoload_with=engine
)
print(repr(some_table))
