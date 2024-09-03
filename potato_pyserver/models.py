from potato_pyserver.database import Base

import dataclasses
from typing import List, Optional
import enum

from pydantic import BaseModel

from sqlalchemy import String, ForeignKey, create_engine, Table, Integer, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session, composite


class Role(enum.Enum):
    USER = "user"
    ADMIN = "admin"


class Hamlet(Base):
    __tablename__ = "hamlets"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))

    items: Mapped[List["WorldItem"]] = relationship(back_populates="hamlet",
                                                    cascade="all, delete-orphan")

    hamlet_access_requests: Mapped[List["HamletAccessRequest"]] = relationship(back_populates="hamlet")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(30))
    username: Mapped[str] = mapped_column(String(30))
    hashed_password: Mapped[str] = mapped_column(String(60))

    first_name: Mapped[str] = mapped_column(String(30))
    last_name: Mapped[str] = mapped_column(String(30))

    role: Mapped[Role] = mapped_column(server_default="USER")

    hamlet_access_requests: Mapped[List["HamletAccessRequest"]] = relationship(back_populates="user")

    household_access_requests: Mapped[List["HouseholdAccessRequest"]] = relationship(back_populates="user")
    user_household_access: Mapped["UserHouseholdAccess"] = relationship(back_populates="user")


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
    user: Mapped[User] = relationship(back_populates="hamlet_access_requests")

    hamlet_id: Mapped[int] = mapped_column(ForeignKey("hamlets.id"))
    hamlet: Mapped[Hamlet] = relationship(back_populates="hamlet_access_requests")

    status: Mapped[str] = mapped_column(String(30))
    content: Mapped[str] = mapped_column(String(500))


class Household(Base):
    __tablename__ = "households"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))

    user_household_accesses: Mapped[List["UserHouseholdAccess"]] = relationship(back_populates="household")

    houses: Mapped[List["House"]] =  relationship(back_populates="household")

    household_access_requests: Mapped[List["HouseholdAccessRequest"]] = relationship(back_populates="household")


class UserHouseholdAccess(Base):
    __tablename__ = "user_household_accesses"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped[User] = relationship(back_populates="user_household_access")

    household_id: Mapped[int] = mapped_column(ForeignKey("households.id"))
    household: Mapped[Household] = relationship(back_populates="user_household_accesses")

    request_id: Mapped[int] = mapped_column(ForeignKey("household_access_requests.id"), nullable=True)
    request: Mapped["HouseholdAccessRequest"] = relationship(back_populates="user_household_access")


class HouseholdAccessRequest(Base):
    __tablename__ = "household_access_requests"

    id: Mapped[int] = mapped_column(primary_key=True)
    household_id: Mapped[int] = mapped_column(ForeignKey("households.id"))
    household: Mapped[Household] = relationship(back_populates="household_access_requests")

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped[User] = relationship(back_populates="household_access_requests")

    status: Mapped[str] = mapped_column(String(30))
    content: Mapped[str] = mapped_column(String(500))

    user_household_access: Mapped[UserHouseholdAccess] = relationship(back_populates="request")


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


@dataclasses.dataclass
class Position:
    x: float
    y: float
    z: float


class WorldItem(Base):
    __tablename__ = "world_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))

    position: Mapped[Position] = composite(mapped_column("x"),
                                           mapped_column("y"),
                                           mapped_column("z"))

    prefab_id: Mapped[int] = mapped_column(ForeignKey("prefabs.id"))
    prefab: Mapped["Prefab"] = relationship(back_populates="world_items")

    item_type_id: Mapped[int] = mapped_column(ForeignKey("world_item_types.id"))
    item_type: Mapped["WorldItemType"] = relationship(back_populates="items")

    hamlet_id: Mapped[int] = mapped_column(ForeignKey("hamlets.id"))
    hamlet: Mapped["Hamlet"] = relationship(back_populates="items")


class Prefab(Base):
    __tablename__ = "prefabs"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    path: Mapped[str] = mapped_column(String(30))

    model_id: Mapped[Optional[int]] = mapped_column(ForeignKey("three_d_models.id"))
    model: Mapped[Optional["ThreeDModel"]] = relationship(back_populates="prefabs")

    world_items: Mapped[List[WorldItem]] = relationship(back_populates="prefab")


class ThreeDModel(Base):
    __tablename__ = "three_d_models"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))

    prefabs: Mapped[List[Prefab]] = relationship(back_populates="model")


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
    session.add(Prefab(path="ConstructionSite", name="ConstructionSite"))
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
