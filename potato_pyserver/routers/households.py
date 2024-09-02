from potato_pyserver.models import User, Hamlet, Household, HouseholdAccessRequest, UserHouseholdAccess
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


@router.get("/households/me", response_model=HouseholdResponse, tags=["Households"])
async def read_household_me(
        current_user: Annotated[UserDataResponse, Depends(get_current_user)],
        db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == current_user.id).first()
    return user.user_household_access.household


@router.get("/households", response_model=List[HouseholdResponse], tags=["Households"])
def list_households(current_user: Annotated[UserDataResponse, Depends(get_current_user)],
                    db: Session = Depends(get_db)):
    return db.query(Household).all()


@router.get("/households/{householdId}", response_model=HouseholdResponse, tags=["Households"])
def fetch_household(householdId: int,
                    current_user: Annotated[UserDataResponse, Depends(get_current_user)],
                    db: Session = Depends(get_db)):
    household = db.query(Household).filter(Household.id == householdId).first()
    if household is None:
        raise HTTPException(status_code=404, detail=f"Household '{householdId}' not found")
    return household


@router.put("/households/{householdId}", response_model=HouseholdResponse, tags=["Households"])
def rename_household(householdId: int,
                    new_household: HouseholdResponse,
                    current_user: Annotated[UserDataResponse, Depends(get_current_user)],
                    db: Session = Depends(get_db)):
    household = db.query(Household).filter(Household.id == householdId).first()
    if household is None:
        raise HTTPException(status_code=404, detail=f"Household '{householdId}' not found")

    db.query(Household).filter(Household.id == householdId).update({"name": new_household.name})
    db.commit()
    db.refresh(household)
    return household


@router.post("/households", response_model=HouseholdResponse, tags=["Households"])
def create_household(household: HouseholdCreation,
                     current_user: Annotated[UserDataResponse, Depends(get_current_user)],
                     db: Session = Depends(get_db)):
    if db.query(Household).filter(Household.name == household.name).first():
        raise HTTPException(status_code=409, detail=f"Household '{household.name}' already exists")

    new_household = Household(name=household.name)
    db.add(new_household)
    db.commit()
    db.refresh(new_household)

    db.query(UserHouseholdAccess) \
      .filter(UserHouseholdAccess.user_id == current_user.id) \
      .update({"household_id": new_household.id, "request_id": None})
    db.commit()
    return {"id": new_household.id, "name": new_household.name}


@router.delete("/households/{householdId}", tags=["Households"])
def delete_household(householdId: int,
                     current_user: Annotated[UserDataResponse, Depends(get_current_user)],
                     db: Session = Depends(get_db)):
    household = db.query(Household).filter(Household.id == householdId).first()
    if household is None:
        raise HTTPException(status_code=404, detail=f"Hamlet '{hamletId}' not found")

    db.delete(household)
    db.commit()
    return {"message": f"Household '{Household.id}' deleted successfully"}



@router.get("/households/{householdId}/users", response_model=List[UserDataResponse],
            tags=["Households"])
def get_user_in_household(householdId: int, db: Session = Depends(get_db)):
    user_accesses = db.query(UserHouseholdAccess) \
                      .filter(UserHouseholdAccess.household_id == householdId).all()
    return [u.user for u in user_accesses]


class HouseholdAccessRequestPayload(BaseModel):
    household_id: int
    user_id: int
    content: str


class HouseholdAccessRequestData(BaseModel):
    id: int
    household_id: int
    user_id: int
    status: str
    content: str


@router.post("/households/{householdId}/accessRequests",
             response_model=HouseholdAccessRequestData, tags=["Households"])
def create_household_access_request(householdId: int,
            payload: HouseholdAccessRequestPayload,
            current_user: Annotated[UserDataResponse, Depends(get_current_user)],
            db: Session = Depends(get_db)):
    household = db.query(Household).filter(Household.id == householdId).first()
    if household is None:
        raise HTTPException(status_code=409, detail=f"Household '{Household.name}' does not exist")
    access_request = HouseholdAccessRequest(household_id=householdId, user_id=current_user.id,
                                            status="Pending", content=payload.content)

    db.add(access_request)
    db.commit()
    db.refresh(access_request)
    return {"id": access_request.id, "household_id": householdId,
            "user_id": current_user.id, "status": "Pending", "content": payload.content}


@router.get("/households/{householdId}/accessRequests",
            response_model=List[HouseholdAccessRequestData], tags=["Households"])
def list_household_access_request(householdId: int,
            current_user: Annotated[UserDataResponse, Depends(get_current_user)],
            db: Session = Depends(get_db)):
    household = db.query(Household).filter(Household.id == householdId).first()
    if household is None:
        raise HTTPException(status_code=409, detail=f"Household '{Household.name}' does not exist")
    return household.household_access_requests


@router.get("/households/{householdId}/accessRequests/{requestId}",
            response_model=HouseholdAccessRequestData, tags=["Households"])
def fetch_household_access_request(householdId: int, requestId: int,
            current_user: Annotated[UserDataResponse, Depends(get_current_user)],
            db: Session = Depends(get_db)):
    access_request = db.query(HouseholdAccessRequest) \
                       .filter(HouseholdAccessRequest.id == requestId).first()
    if access_request is None:
        raise HTTPException(status_code=409, detail=f"Access request '{requestId}' does not exist")
    return access_request


@router.put("/households/{householdId}/accessRequests/{requestId}",
            response_model=HouseholdAccessRequestData, tags=["Households"])
def approve_household_access_request(householdId: int,
            requestId: int,
            status_update: HouseholdAccessRequestData,
            current_user: Annotated[UserDataResponse, Depends(get_current_user)],
            db: Session = Depends(get_db)):

    access_request = db.query(HouseholdAccessRequest) \
                       .filter(HouseholdAccessRequest.id == requestId).first()
    if access_request is None:
        raise HTTPException(status_code=409, detail=f"Access request '{requestId}' does not exist")

    db.query(HouseholdAccessRequest) \
      .filter(HouseholdAccessRequest.id == requestId) \
      .update({"status": status_update.status})

    if status_update.status == "Approved":
        db.query(UserHouseholdAccess) \
          .filter(UserHouseholdAccess.user_id == status_update.user_id) \
          .update({"household_id": householdId, "request_id": requestId})

    db.commit()
    db.refresh(access_request)
    return access_request
