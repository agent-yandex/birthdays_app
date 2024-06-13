"""
API endpoints for managing user profiles and related operations.

This module defines FastAPI routers and functions for handling user profile management,
password changes, and profile updates.
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_async_session
from app.database.models import User, check_birthday
from app.utils.authorization import AuthorizedUser
from app.utils.responses import (
    UnauthorizedResponses,
    ChangePasswordResponses,
    UpdateProfileResponses,
)

router = APIRouter(tags=["profile"])


@router.get(
    "/profile/",
    response_model=User.UserModel,
    responses=UnauthorizedResponses.responses(),
    summary="Profile data",
)
async def profile(current_user: AuthorizedUser) -> User.UserModel:
    """
    Endpoint to retrieve the profile data of the current authenticated user.

    Args:
        current_user:  the current authenticated user.

    Returns:
        User.UserModel: Pydantic data model representing the profile data of the current user.
    """
    return User.UserModel(**current_user.__dict__)


@router.patch(
    "/update_profile/",
    response_model=User.UserModel,
    responses=UpdateProfileResponses.responses(),
    summary="Update user profile",
)
async def update_profile(
    current_user: AuthorizedUser,
    form_data: User.UserPatchModel,
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> User.UserModel:
    """
    Endpoint to update the profile information of the current authenticated user.

    Args:
        current_user: Instance of AuthorizedUser representing the current authenticated user.
        form_data: Pydantic model containing the new profile data.
        session: Asynchronous database session obtained from get_async_session dependency.

    Raises:
        :HTTPException: If the provided birthday is in the future.

    Returns:
        User.UserModel: Pydantic data model representing the updated profile data of the user.
    """
    await check_birthday(form_data.birthday)

    user = await session.scalar(select(User).where(User.id == current_user.id))
    user.name = form_data.name
    user.surname = form_data.surname
    user.birthday = form_data.birthday

    await session.commit()
    await session.refresh(user)

    return User.UserModel(**user.__dict__)


class PasswordChangeModel(BaseModel):
    """Data model for password changes."""

    password: str
    new_password: Annotated[str, Field(min_length=6, max_length=100)]


@router.put(
    "/change_password/",
    response_model=User.UserModel,
    responses=ChangePasswordResponses.responses(),
    summary="Reset password",
)
async def change_user_password(
    current_user: AuthorizedUser,
    form_data: PasswordChangeModel,
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> User.UserModel:
    """
    Endpoint to change the password of the current authenticated user.

    Args:
        current_user: Instance of AuthorizedUser representing the current authenticated user.
        form_data: Pydantic model containing the current and new passwords.
        session: Asynchronous database session obtained from get_async_session dependency.

    Raises:
        :HTTPException: If the current password is incorrect.

    Returns:
        User.UserModel: Pydantic data model representing the updated profile data of the user.
    """
    if not current_user.is_password_valid(form_data.password):
        raise ChangePasswordResponses.WRONG_PASSWORD.value
    if current_user.is_password_valid(form_data.new_password):
        raise ChangePasswordResponses.PASSWORD_MATCHES_CURRENT.value

    user = await session.scalar(select(User).where(User.id == current_user.id))
    user.password = User.generate_hash(form_data.new_password)
    await session.commit()
    await session.refresh(user)

    return User.UserModel(**current_user.__dict__)
