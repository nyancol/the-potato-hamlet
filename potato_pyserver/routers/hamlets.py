from potato_pyserver.models import Hamlet, UserHamletAccess, HamletAccessRequest
from potato_pyserver.database import get_db
from potato_pyserver.dependencies import UserDataResponse, get_current_user

import logging

from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from pydantic import BaseModel


router = APIRouter()


class HamletCreation(BaseModel):
    name: str


class HamletResponse(BaseModel):
    id: int
    name: str
    access: bool


@router.get("/hamlets", response_model=List[HamletResponse], tags=["Hamlets"])
def fetch_hamlet_list(current_user: Annotated[UserDataResponse, Depends(get_current_user)],
                      db: Session = Depends(get_db)):
    rows = db.query(Hamlet, UserHamletAccess).outerjoin(UserHamletAccess).all()
    return [{"id": h.id, "name": h.name, "access": acc is not None} for (h, acc) in rows]


@router.get("/hamlets/{hamletId}", response_model=HamletResponse, tags=["Hamlets"])
def fetch_hamlet(hamletId: int,
                current_user: Annotated[UserDataResponse, Depends(get_current_user)],
                db: Session = Depends(get_db)):
    h, access = db.query(Hamlet, UserHamletAccess).filter(Hamlet.id == hamletId) \
                  .outerjoin(UserHamletAccess).first()

    if h is None:
        raise HTTPException(status_code=404, detail=f"Hamlet '{hamletId}' not found")

    return {"id": h.id, "name": h.name, "access": access is not None}


@router.post("/hamlets", response_model=HamletResponse, tags=["Hamlets"])
def create_hamlet(hamlet: HamletCreation,
                 current_user: Annotated[UserDataResponse, Depends(get_current_user)],
                 db: Session = Depends(get_db)):
    if db.query(Hamlet).filter(Hamlet.name == hamlet.name).first():
        raise HTTPException(status_code=409, detail=f"Hamlet '{hamlet.name}' already exists")

    new_hamlet = Hamlet(name=hamlet.name)
    db.add(new_hamlet)
    db.commit()
    db.refresh(new_hamlet)
    return HamletResponse(id=new_hamlet.id, name=new_hamlet.name, access=False)


@router.delete("/hamlets/{hameltId}", tags=["Hamlets"])
def delete_hamlet(hamletId: int,
                  current_user: Annotated[UserDataResponse, Depends(get_current_user)],
                  db: Session = Depends(get_db)):
    hamlet = db.query(Hamlet).filter(Hamlet.id == hamletId).first()
    if hamlet is None:
        raise HTTPException(status_code=404, detail=f"Hamlet '{hamletId}' not found")

    db.delete(hamlet)
    db.commit()
    return {"message": f"Hamlet '{hamlet.id}' deleted successfully"}



class HamletRequestCreation(BaseModel):
    hamlet_id: int
    user_id: int
    content: str
    status: str = "Submitted"


class HamletRequestStatusUpdate(BaseModel):
    id: int
    hamlet_id: int
    status: str


class HamletAccessRequestResponse(BaseModel):
    id: int
    hamlet_id: int
    hamlet: str
    user_id: int
    username: str
    status: str
    content: str


@router.get("/hamlets/{hamletId}/naturalisations",
            response_model=List[HamletAccessRequestResponse], tags=["Hamlets"])
def list_naturalisation_requests(hamletId: int,
                current_user: Annotated[UserDataResponse, Depends(get_current_user)],
                db: Session = Depends(get_db)):
    requests = db.query(HamletAccessRequest) \
                 .filter(HamletAccessRequest.hamlet_id == hamletId).all()

    return [{"id": req.id, "hamlet": req.hamlet.name, "username": req.user.username,
             "hamlet_id": req.hamlet_id, "user_id": req.user_id,
             "status": req.status, "content": req.content} for req in requests]


@router.get("/hamlets/{hamletId}/naturalisations/{requestId}",
            response_model=HamletAccessRequestResponse, tags=["Hamlets"])
def fetch_naturalisation_request(hamletId: int, requestId: int,
                current_user: Annotated[UserDataResponse, Depends(get_current_user)],
                db: Session = Depends(get_db)):
    request = db.query(HamletAccessRequest) \
                 .filter(HamletAccessRequest.id == requestId).first()

    if request is None:
        raise HTTPException(status_code=404, detail=f"Request '{requestId}' not found")

    return {"id": request.id, "hamlet": request.hamlet.name,
            "username": request.user.username,
            "hamlet_id": request.hamlet_id, "user_id": request.user_id,
            "status": request.status, "content": request.content}


@router.post("/hamlets/{hamletId}/naturalisations", response_model=HamletAccessRequestResponse,
             tags=["Hamlets"])
def create_naturalisation_request(hamletId: int, request: HamletRequestCreation,
                current_user: Annotated[UserDataResponse, Depends(get_current_user)],
                db: Session = Depends(get_db)):
    new_request = HamletAccessRequest(user_id=request.user_id, hamlet_id=request.hamlet_id,
                                      status="Submitted", content=request.content)
    db.add(new_request)
    db.commit()
    db.refresh(new_request)
    return {"id": new_request.id, "hamlet": new_request.hamlet.name,
            "username": new_request.user.username,
            "hamlet_id": new_request.hamlet_id, "user_id": new_request.user_id,
            "status": new_request.status, "content": new_request.content}


@router.put("/hamlets/{hamletId}/naturalisations/{requestId}/status",
            response_model=HamletAccessRequestResponse, tags=["Hamlets"])
def fetch_naturalisation_request(hamletId: int, requestId: int, request: HamletRequestStatusUpdate,
                current_user: Annotated[UserDataResponse, Depends(get_current_user)],
                db: Session = Depends(get_db)):
    result = db.query(HamletAccessRequest) \
                .filter(HamletAccessRequest.id == requestId) \
                .filter(HamletAccessRequest.hamlet_id == hamletId).first()

    if result is None:
        raise HTTPException(status_code=404, detail=f"Request '{requestId}' not found")

    if request.status == "Approved":
        db.add(UserHamletAccess(user_id=result.user_id, hamlet_id=request.hamlet_id,
                                request_id=result.id))
    db.query(HamletAccessRequest) \
            .filter(HamletAccessRequest.id == request.id) \
            .filter(HamletAccessRequest.hamlet_id == request.hamlet_id) \
            .update({"status": request.status})

    db.commit()
    db.refresh(result)
    return {"id": result.id, "hamlet": result.hamlet.name,
            "username": result.user.username,
            "hamlet_id": result.hamlet_id, "user_id": result.user_id,
            "status": result.status, "content": result.content}
