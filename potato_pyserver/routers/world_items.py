from potato_pyserver.models import House, WorldItem, WorldItemType, Position, Prefab
from potato_pyserver.database import get_db
from potato_pyserver.routers.users import UserDataResponse
from potato_pyserver.dependencies import get_current_user

from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session
from pydantic import BaseModel


router = APIRouter()


class HouseRequestData(BaseModel):
    household_id: int
    hamlet_id: int
    name: str


class PositionData(BaseModel):
    x: float
    y: float
    z: float


class WorldItemData(BaseModel):
    id: int
    position: PositionData
    hamlet_id: int


class HouseData(BaseModel):
    id: int
    item_id: int
    item: WorldItemData
    household_id: int


class PrefabData(BaseModel):
    id: int


def generate_new_house(db, hamlet_id, household_id, house_name):
    """Returns a house item in a new free location"""
    # This implementation generates randomly house locations in an array of 5 x 5
    # Over a map of size 1000 x 1000
    try:
        houses = db.query(House).all()
        current_locations = set((h.item.position.x, h.item.position.z) for h in houses)
        x, z = create_new_house_location(current_locations)
        item_type_id = db.query(WorldItemType).filter_by(name="house").first().id
        prefab_id = db.query(Prefab).filter_by(name="ConstructionSite").first().id
        new_item = WorldItem(name=house_name,
                             position=Position(x, 0, z),
                             prefab_id=prefab_id,
                             item_type_id=item_type_id,
                             hamlet_id=hamlet_id)
        db.add(new_item)
        db.flush()

        new_house = House(name=house_name,
                          item_id=new_item.id,
                          household_id=household_id)
        db.add(new_house)
        db.commit()

        db.refresh(new_house)
        return new_house
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"An error occurred when creating the house: {str(e)}")


def create_new_house_location(current_locations):
    map_size = 1000
    max_locations_row = 5
    for x in range(0, map_size, int(map_size / max_locations_row)):
        for z in range(0, map_size, int(map_size / max_locations_row)):
            if (x , z) not in current_locations:
                return (x, z)
    raise Exception("No locations available for new houses")


@router.get("/worldItems/{hamletId}/houses/{houseId}", response_model=HouseData,
            tags=["World Items"])
def fetch_house(hamletId: int, houseId: int,
        current_user: Annotated[UserDataResponse, Depends(get_current_user)],
        db: Session = Depends(get_db)):
    house = db.query(House).join(House.item) \
                           .filter(WorldItem.hamlet_id == hamletId) \
                           .filter(House.id == houseId) \
                           .first()
    if house is None:
        raise HTTPException(status_code=404, detail=f"House '{houseId}' not found")
    return {"id": house.id, "item_id": house.item_id, "household_id": house.household_id,
            "item": {"id": house.item.id, "hamlet_id": house.item.hamlet_id,
                     "position": house.item.position}}


@router.get("/worldItems/{hamletId}/houses", response_model=List[HouseData],
            tags=["World Items"])
def list_houses(hamletId: int,
        current_user: Annotated[UserDataResponse, Depends(get_current_user)],
        db: Session = Depends(get_db)):
    houses = db.query(House).join(House.item) \
                            .filter(WorldItem.hamlet_id == hamletId) \
                            .all()

    return [{"id": house.id, "item_id": house.item_id, "household_id": house.household_id,
            "item": {"id": house.item.id, "hamlet_id": house.item.hamlet_id,
                     "position": house.item.position}} for house in houses]


@router.post("/worldItems/{hamletId}/houses", response_model=HouseData,
             tags=["World Items"])
def create_house(hamletId: int, house: HouseRequestData,
        current_user: Annotated[UserDataResponse, Depends(get_current_user)],
        db: Session = Depends(get_db)):
    new_house = generate_new_house(db, hamletId, house.household_id, house.name)
    return {"id": new_house.id, "item_id": new_house.item_id,
            "household_id": new_house.household_id,
            "item": {"id": new_house.item.id, "hamlet_id": new_house.item.hamlet_id,
                     "position": new_house.item.position}}


@router.put("/worldItems/{hamletId}/houses/{houseId}/position", response_model=PositionData,
        tags=["World Items"])
def update_house_position(hamletId: int, houseId: int, position: PositionData,
        current_user: Annotated[UserDataResponse, Depends(get_current_user)],
        db: Session = Depends(get_db)):
    house = db.query(House).filter(House.id == houseId).first()
    if house is None:
        raise HTTPException(status_code=404, detail=f"House '{houseId}' not found")

    db.query(WorldItem).filter(WorldItem.id == house.item_id) \
                       .update({"position": Position(position.x, position.y, position.z)})
    db.commit()
    db.refresh(house)
    return house.item.position


@router.put("/worldItems/{hamletId}/houses/{houseId}/prefab", response_model=PositionData,
        tags=["World Items"])
def update_house_prefab(hamletId: int, houseId: int, prefab: PrefabData,
        current_user: Annotated[UserDataResponse, Depends(get_current_user)],
        db: Session = Depends(get_db)):
    house = db.query(House).filter(House.id == houseId).first()
    if house is None:
        raise HTTPException(status_code=404, detail=f"House '{houseId}' not found")

    db.query(WorldItem).filter(WorldItem.id == house.item_id) \
                       .update({"position": Position(position.x, position.y, position.z)})
    db.commit()
    db.refresh(house)
    return house.item.position


@router.delete("/worldItems/{hamletId}/houses/{houseId}", tags=["World Items"])
def delete_household(hamletId: int, houseId: int, db: Session = Depends(get_db)):
    house = db.query(House).filter(House.id == houseId).first()
    if house is None:
        raise HTTPException(status_code=404, detail=f"House '{houseId}' not found")

    db.delete(house)
    db.commit()
    return {"message": f"House '{houseId}' deleted successfully"}

