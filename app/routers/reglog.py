"""
API Router for user authentication and registration.

This module defines API endpoints using FastAPI's APIRouter for user authentication
(signin) and registration (signup). It includes dependencies, response models, and
helper functions related to user management.
"""

from typing import Annotated

from pydantic import BaseModel
from fastapi import Depends, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_async_session
from app.database.models import User, check_birthday
from app.utils.responses import SigninResponses, SignupResponses
from app.utils.authorization import (
    authenticate_user,
    create_access_token,
)

router = APIRouter(tags=["reglog"])


class Token(BaseModel):
    """Data model representing a JWT token."""

    access_token: str
    token_type: str


@router.post(
    "/signin/",
    response_model=Token,
    responses=SigninResponses.responses(),
    summary="Signin for get access token",
)
async def signin(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> Token:
    """
    Endpoint for user authentication to obtain an access token.

    Args:
        form_data: Form data containing username and password for authentication.
        session: Asynchronous database session.

    Raises:
        :HTTPException: If authentication fails, raises HTTP 401 Unauthorized error.

    Returns:
        Token: Pydantic data model representing a JWT token with access_token and token_type
    """
    user = await authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise SigninResponses.INCORRECT_SIGNIN.value
    access_token = await create_access_token(token_data={"sub": user.username})

    return Token(access_token=access_token, token_type="bearer")


@router.post(
    "/signup/",
    response_model=User.RegistrationModel,
    responses=SignupResponses.responses(),
    summary="Registration new user",
)
async def signup(
    form_data: User.RegistrationModel,
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> User.RegistrationModel:
    """
    Endpoint for registering a new user.

    Args:
        form_data: Data model representing user registration details.
        session: Asynchronous database session.

    Raises:
        :HTTPException:
            - If the provided birthday is in the future.
            - If the username is already in use.

    Returns:
        User.RegistrationModel: Data model representing the registered user details.
    """
    await check_birthday(form_data.birthday)

    if await session.scalar(select(User).where(User.username == form_data.username)):
        raise SignupResponses.USERNAME_IN_USE.value

    user = User(
        username=form_data.username,
        password=User.generate_hash(form_data.password),
        name=form_data.name,
        surname=form_data.surname,
        birthday=form_data.birthday,
    )

    session.add(user)
    await session.commit()

    return form_data
