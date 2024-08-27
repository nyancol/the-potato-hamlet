from potato_pyserver.models import User, Hamlet, Household
from potato_pyserver.database import get_db
from potato_pyserver.routers.users import UserDataResponse
from potato_pyserver.routers.hamlets import HamletResponse
from potato_pyserver.dependencies import get_current_user

from typing import Union, Optional, List, Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, constr


router = APIRouter()


class HouseholdCreation(BaseModel):
    name: str


class HouseholdResponse(BaseModel):
    id: int
    name: str


@router.get("/households/{householdId}", response_model=HouseholdResponse, tags=["Households"])
async def read_household_me(
        current_user: Annotated[UserDataResponse, Depends(get_current_user)],
        db: Session = Depends(get_db)):
    user = db.query(User).filter_by(User.id == current_user.id)
    return user.household


@router.get("/households/{householdId}", response_model=HouseholdResponse, tags=["Households"])
def fetch_household(householdId: int, db: Session = Depends(get_db)):
    household = db.query(Household).filter(Household.id == householdId).first()
    if household is None:
        raise HTTPException(status_code=404, detail=f"Household '{householdId}' not found")
    return household


@router.post("/households", response_model=HouseholdResponse, tags=["Households"])
def create_household(household: HouseholdCreation, db: Session = Depends(get_db)):
    if db.query(Household).filter(Household.name == household.name).first():
        raise HTTPException(status_code=409, detail=f"Household '{household.name}' already exists")

    new_household = Household(name=household.name)
    db.add(new_household)
    db.commit()
    db.refresh(new_household)
    return HamletResponse(id=new_household.id, name=new_household.name)


@router.delete("/households/{householdId}", tags=["Households"])
def delete_household(householdId: int, db: Session = Depends(get_db)):
    household = db.query(Household).filter(Household.id == householdId).first()
    if household is None:
        raise HTTPException(status_code=404, detail=f"Hamlet '{hamletId}' not found")

    db.delete(household)
    db.commit()
    return {"message": f"Household '{Household.id}' deleted successfully"}


@router.post("/households/{householdId}/users", tags=["Households"])
def add_user_to_household(householdId: int, userId: int, db: Session = Depends(get_db)):
    household = db.query(Household).filter(Household.id == householdId).first()
    if household is None:
        raise HTTPException(status_code=409, detail=f"Household '{Household.name}' does not exist")

    db.query(User).where(User.id == userId).update(dict(household_id=householdId))
    db.commit()
    return


class HouseholdUsersResponse(BaseModel):
    users: List[UserDataResponse]


@router.get("/households/{householdId}/users", response_model=HouseholdUsersResponse,
            tags=["Households"])
def get_user_in_household(householdId: int, db: Session = Depends(get_db)):
    users = db.query(User).filter(User.household_id == householdId).all()
    return HouseholdUsersResponse(users=[UserDataResponse(id=u.id, username=u.username,
                                                      email=u.email, first_name=u.first_name,
                                                      last_name=u.last_name) for u in users])
