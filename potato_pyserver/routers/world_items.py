from potato_pyserver.models import House, WorldItem, WorldItemType
from potato_pyserver.database import get_db

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session
from pydantic import BaseModel


router = APIRouter()


class HouseData(BaseModel):
    household_id: int
    hamlet_id: int
    name: str


class HouseDataResponse(HouseData):
    id: int
    item_id: int


@router.get("/worldItems/houses/{houseId}", response_model=HouseDataResponse, tags=["World Items"])
def fetch_house(houseId: int, db: Session = Depends(get_db)):
    house = db.query(House).filter(House.id == houseId).first()
    if house is None:
        raise HTTPException(status_code=404, detail=f"House '{houseId}' not found")
    return {"household_id": house.household_id, "hamlet_id": house.item.hamlet_id,
            "name": house.name, "id": house.id, "item_id": house.item_id}


@router.post("/worldItems/houses", status_code=201, response_model=HouseDataResponse,
             tags=["World Items"])
def create_house(house: HouseData, db: Session = Depends(get_db)):
    try:
        with db.begin():
            item_type = db.query(WorldItemType).filter_by(name="house").first()
            new_item = WorldItem(item_type_id=item_type.id, hamlet_id=house.hamlet_id)
            db.add(new_item)
            db.flush()

            new_house = House(name=house.name, item_id=new_item.id, household_id=house.household_id)
            db.add(new_house)
            db.commit()

        db.refresh(new_house)
        return {"household_id": new_house.household_id, "hamlet_id": new_item.hamlet_id, "name": new_house.name, "id": new_house.id, "item_id": new_house.item_id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"An error occurred when creating the house: {str(e)}")


@router.delete("/worldItems/houses/{itemId}", tags=["World Items"])
def delete_household(itemId: int, db: Session = Depends(get_db)):
    house = db.query(House).filter(House.id == itemId).first()
    if house is None:
        raise HTTPException(status_code=404, detail=f"House '{itemId}' not found")

    db.delete(house)
    db.commit()
    return {"message": f"House '{itemId}' deleted successfully"}

