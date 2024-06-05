from typing import Annotated

from fastapi import APIRouter
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.database.connection import sessionmaker
from app.database.models import User, check_birthday
from app.utils.authorization import AuthorizedUser, get_user
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
    return User.UserModel(**current_user.__dict__)


@router.patch(
    "/update_profile/",
    response_model=str,
    responses=UpdateProfileResponses.responses(),
    summary="Update user profile",
)
async def update_profile(
    current_user: AuthorizedUser,
    form_data: User.UserPatchModel
) -> str:
    await check_birthday(form_data.birthday)

    async with sessionmaker() as session:
        user = await session.scalar(select(User).where(User.id == current_user.id))
        user.name = form_data.name
        user.surname = form_data.surname
        user.birthday = form_data.birthday

        await session.commit()

    return "Succes"


class PasswordChangeModel(BaseModel):
    password: str
    new_password: Annotated[str, Field(min_length=6, max_length=100)]


@router.put(
    "/change_password/",
    response_model=User.UserModel,
    summary="Reset password"
)
async def change_user_password(
    current_user: AuthorizedUser,
    form_data: PasswordChangeModel,
) -> User.UserModel:
    if not current_user.is_password_valid(form_data.password):
        raise ChangePasswordResponses.WRONG_PASSWORD.value
    if current_user.is_password_valid(form_data.new_password):
        raise ChangePasswordResponses.PASSWORD_MATCHES_CURRENT.value

    async with sessionmaker() as session:
        user = await session.scalar(select(User).where(User.id == current_user.id))
        user.password = User.generate_hash(form_data.new_password)
        await session.commit()

    return User.UserModel(**current_user.__dict__)
