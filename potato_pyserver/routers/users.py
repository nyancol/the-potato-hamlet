from potato_pyserver.models import User, get_user, Household, UserHouseholdAccess
from potato_pyserver.database import get_db
from potato_pyserver.dependencies import UserData, get_current_user, SECRET_KEY, ALGORITHM, UserDataResponse, RoleChecker, Role

from datetime import timedelta, datetime, timezone
from typing import List, Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from pydantic import BaseModel, EmailStr, constr

import jwt

from sqlalchemy.orm import Session

from passlib.context import CryptContext


ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()



class Token(BaseModel):
    access_token: str
    token_type: str


class UserDataForm(UserData):
    password: constr(min_length=6, max_length=50)


def authenticate_user(db: Session, username: str, password: str) -> UserData:
    user: UserInDB = get_user(db, username)
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
) -> Token:
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/users/me/", response_model=UserDataResponse, tags=["Users"])
async def read_users_me(
    current_user: Annotated[UserDataResponse, Depends(get_current_user)],
):
    return current_user


@router.post("/users", tags=["Users"])
def user_registration(userForm: UserDataForm, db: Session = Depends(get_db)) -> UserDataResponse:
    if db.query(User).filter(User.username == userForm.username).first():
        raise HTTPException(status_code=409, detail=f"Username '{userForm.username}' already exists")

    if db.query(User).filter(User.email == userForm.email).first():
        raise HTTPException(status_code=409, detail=f"Email '{userForm.email}' already exists")

    hashed_password = pwd_context.hash(userForm.password)
    new_user = User(email=userForm.email, username=userForm.username,
                    hashed_password=hashed_password, first_name=userForm.first_name,
                    last_name=userForm.last_name)
    db.add(new_user)

    household = Household(name=f"Famille de {new_user.first_name}")
    db.add(household)
    db.commit()

    db.refresh(new_user)
    db.refresh(household)
    db.add(UserHouseholdAccess(user_id=new_user.id, household_id=household.id))
    db.commit()
    return new_user


@router.delete("/users/{userId}", tags=["Users"])
def delete_user(userId: int,
                current_user: Annotated[UserDataResponse, Depends(get_current_user)],
                db: Session = Depends(get_db)):
    if current_user.id != userId:
        raise HTTPException(status_code="409", detail=f"Cannot delete another user")
    user = db.query(User).filter(User.id == userId).first()
    if user is None:
        raise HTTPException(status_code=404, detail=f"User '{userId}' not found")

    db.delete(user)
    db.commit()

    return {"message": f"User '{user.id}' deleted successfully"}


@router.put("/users/{userId}", response_model=UserDataResponse, tags=["Users"])
def update_user(userId: int, user: UserData,
                current_user: Annotated[UserDataResponse, Depends(get_current_user)],
                db: Session = Depends(get_db)):
    if current_user.id != userId:
        raise HTTPException(status_code=409, detail=f"Cannot update another user")
    existing_user = db.query(User).filter(User.id == userId).first()
    if existing_user is None:
        raise HTTPException(status_code=404, detail=f"User '{userId}' not found")

    db.query(User).filter(User.id == userId).update(dict(user))
    db.commit()
    db.refresh(existing_user)
    return existing_user


@router.get("/users/{userId}", response_model=UserDataResponse, tags=["Users"])
def fetch_user(userId: int,
               current_user: Annotated[UserDataResponse, Depends(get_current_user)],
               db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == userId).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/users", response_model=List[UserDataResponse], tags=["Users"])
def list_users(current_user: Annotated[UserDataResponse, Depends(get_current_user)],
               db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users


class UserRole(BaseModel):
    role: Role


@router.get("/users/{userId}/roles", response_model=UserRole, tags=["Users"])
def fetch_user_role(userId: int,
                    current_user: Annotated[UserDataResponse, Depends(get_current_user)],
                    db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == userId).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"role": user.role}


@router.put("/users/{userId}/roles", response_model=UserDataResponse, tags=["Users"])
def update_user_role(userId: int, user_role: UserRole,
                    current_user: Annotated[UserDataResponse, Depends(get_current_user)],
                    db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == userId).first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db.query(User).filter(User.id == userId).update({"role": user_role.role})
    db.commit()
    db.refresh(user)
    return {"role": user.role}

