from datetime import datetime
from typing import Annotated

from pydantic import BaseModel
from fastapi import Depends, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from app.database.connection import sessionmaker
from app.database.models import User, check_birthday
from app.utils.responses import SigninResponses, SignupResponses
from app.utils.authorization import (
    authenticate_user,
    create_access_token,
)

router = APIRouter(tags=["reglog"])


class Token(BaseModel):
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
) -> Token:
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise SigninResponses.INCORRECT_SIGNIN.value
    access_token = await create_access_token(data={"sub": user.username})

    return Token(access_token=access_token, token_type="bearer")


@router.post(
    "/signup/",
    response_model=User.RegistrationModel,
    responses=SignupResponses.responses(),
    summary="Registration new user",
)
async def signup(
    form_data: User.RegistrationModel,
) -> User.RegistrationModel:
    await check_birthday(form_data.birthday)

    async with sessionmaker() as session:
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
