from potato_pyserver.database import Base

from typing import List, Optional
import enum

from pydantic import BaseModel

from sqlalchemy import String, ForeignKey, create_engine, Table, Integer, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session


class Role(enum.Enum):
    USER = "user"
    ADMIN = "admin"


class Hamlet(Base):
    __tablename__ = "hamlets"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))

    items: Mapped[List["WorldItem"]] = relationship(back_populates="hamlet",
                                                    cascade="all, delete-orphan")

    access_requests: Mapped[List["HamletAccessRequest"]] = relationship(back_populates="hamlet")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(30))
    username: Mapped[str] = mapped_column(String(30))
    hashed_password: Mapped[str] = mapped_column(String(60))

    first_name: Mapped[str] = mapped_column(String(30))
    last_name: Mapped[str] = mapped_column(String(30))

    household_id: Mapped[Optional[int]] = mapped_column(ForeignKey("households.id"))
    household: Mapped["Household"] = relationship(back_populates="users")

    role: Mapped[Role] = mapped_column(server_default="USER")

    access_requests: Mapped[List["HamletAccessRequest"]] = relationship(back_populates="user")


def get_user(db: Session, username: str):
    user = db.query(User).filter(User.username == username).first()
    if user is not None:
        return user


class UserHamletAccess(Base):
    __tablename__ = "user_hamlet_access"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    hamlet_id: Mapped[int] = mapped_column(ForeignKey("hamlets.id"), primary_key=True)
    request_id: Mapped[int] = mapped_column(ForeignKey("hamlet_access_requests.id"))


class HamletAccessRequest(Base):
    __tablename__ = "hamlet_access_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped[User] = relationship(back_populates="access_requests")

    hamlet_id: Mapped[int] = mapped_column(ForeignKey("hamlets.id"))
    hamlet: Mapped[Hamlet] = relationship(back_populates="access_requests")

    status: Mapped[str] = mapped_column(String(30))
    content: Mapped[str] = mapped_column(String(500))


class Household(Base):
    __tablename__ = "households"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))

    users: Mapped[List["User"]] = relationship(back_populates="household")

    houses: Mapped[List["House"]] =  relationship(back_populates="household")


class Character(Base):
    __tablename__ = "characters"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))


class House(Base):
    __tablename__ = "houses"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))

    item_id: Mapped[int] = mapped_column(ForeignKey("world_items.id"))
    item: Mapped["WorldItem"] = relationship()

    household_id: Mapped[int] = mapped_column(ForeignKey("households.id"))
    household: Mapped["Household"] = relationship(back_populates="houses")


class WorldItemType(Base):
    __tablename__ = "world_item_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))

    items: Mapped["WorldItem"] = relationship(back_populates="item_type")


class WorldItem(Base):
    __tablename__ = "world_items"

    id: Mapped[int] = mapped_column(primary_key=True)

    item_type_id: Mapped[int] = mapped_column(ForeignKey("world_item_types.id"))
    item_type: Mapped["WorldItemType"] = relationship(back_populates="items")

    hamlet_id: Mapped[int] = mapped_column(ForeignKey("hamlets.id"))
    hamlet: Mapped["Hamlet"] = relationship(back_populates="items")


class StreetFurniture(Base):
    __tablename__ = "street_furnitures"

    id: Mapped[int] = mapped_column(primary_key=True)

    world_item_id: Mapped[int] = mapped_column(ForeignKey("world_items.id"))


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))


conversation_user_mapping = Table(
    "conversation_user_mapping",
    Base.metadata,
    Column("conversation_id", Integer,
           ForeignKey("conversations.id", ondelete="CASCADE"),
           primary_key=True),
    Column("user_id", Integer,
           ForeignKey("users.id", ondelete="CASCADE"),
           primary_key=True)
)


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship()

    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id"))
    conversation: Mapped["Conversation"] = relationship()


def populate_world_item_types(engine):
    session = Session(engine)
    session.add(WorldItemType(name="house"))
    session.commit()


def populate_hamlets(engine):
    session = Session(engine)
    session.add(Hamlet(name="Le Hameau des Patates"))
    session.commit()


def reset_tables(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    populate_world_item_types(engine)
    populate_hamlets(engine)
