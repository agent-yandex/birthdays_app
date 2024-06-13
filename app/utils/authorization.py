"""Utility functions and configurations for user authentication and token management."""

from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from sqlalchemy import select
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_async_session
from app.database.models import User
from app.utils.responses import UnauthorizedResponses
from app.utils.config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/signin/", auto_error=False)


async def get_user(username: str, session: AsyncSession) -> User:
    """
    Retrieve a user from the database based on the username.

    Args:
        username (str): The username of the user to retrieve.
        session (AsyncSession): Asynchronous database session obtained from get_async_session.

    Returns:
        User: The user object retrieved from the database.
    """
    user = await session.scalar(select(User).where(User.username == username))
    return user


async def authenticate_user(
    username: str, password: str, session: AsyncSession,
) -> User | bool:
    """
    Authenticate a user based on the provided username and password.

    Args:
        username: The username of the user to authenticate.
        password: The password of the user to authenticate.
        session: Asynchronous database session obtained from get_async_session.

    Returns:
        Union: User or boolean indicating if the user is authenticated or not.
    """
    user = await get_user(username, session)
    if not user:
        return False
    if not user.is_password_valid(password):
        return False
    return user


async def create_access_token(token_data: dict[str, str]) -> str:
    """
    Create an access token with the provided token data.

    Args:
        token_data: Data to encode into the access token.

    Returns:
        str: Encoded JWT access token string.
    """
    to_encode = token_data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> User:
    """
    Retrieve the current authenticated user based on the provided JWT token.

    Args:
        token: JWT token obtained from the authentication header.
        session: Asynchronous database session.

    Returns:
        User: The user object corresponding to the authenticated user.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise UnauthorizedResponses.UNAUTHORIZED.value
    except InvalidTokenError:
        raise UnauthorizedResponses.UNAUTHORIZED.value

    user = await get_user(username, session)
    if user is None:
        raise UnauthorizedResponses.UNAUTHORIZED.value
    return user


AuthorizedUser = Annotated[User.UserModel, Depends(get_current_user)]
