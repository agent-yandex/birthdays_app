import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
import dotenv
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext

from app.database.connection import engine, sessionmaker
from app.database.models import User
from app.utils.responses import UnauthorizedResponses

dotenv.load_dotenv()

SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/signin/", auto_error=False)


async def get_user(username: str) -> User:
    async with sessionmaker() as session:
        user = await session.scalar(select(User).where(User.username == username))
        return user


async def authenticate_user(username: str, password: str) -> User | bool:
    user = await get_user(username)
    if not user:
        return False
    if not user.is_password_valid(password):
        return False
    return user


async def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise UnauthorizedResponses.UNAUTHORIZED.value
    except InvalidTokenError:
        raise UnauthorizedResponses.UNAUTHORIZED.value

    user = await get_user(username=username)
    if user is None:
        raise UnauthorizedResponses.UNAUTHORIZED.value
    return user


AuthorizedUser = Annotated[User.UserModel, Depends(get_current_user)]
