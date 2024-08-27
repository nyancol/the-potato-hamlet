from potato_pyserver.models import get_user, Role
from potato_pyserver.database import get_db

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from pydantic import BaseModel, EmailStr, constr

import jwt
from jwt.exceptions import InvalidTokenError


from sqlalchemy.orm import Session


SECRET_KEY = "a0fe08ee3fca3694e3901e7998e9ed4ef85ba00c84be04fae62f8c750dd2f4c5"
ALGORITHM = "HS256"


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class TokenData(BaseModel):
    username: str | None = None


class UserData(BaseModel):
    username: constr(min_length=3, max_length=50)
    email: EmailStr
    first_name: str
    last_name: str


class UserDataResponse(UserData):
    id: int
    role: Role

    class Config:
        from_attributes = True


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],
                           db: Session = Depends(get_db)) -> UserDataResponse:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


class RoleChecker:
    def __init__(self, allowed_roles):
        self.allowed_roles = allowed_roles

    def __call__(self, user: Annotated[UserData, Depends(get_current_user)]):
        if user.role in self.allowed_roles:
            return True
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You don't have enough permissions")

