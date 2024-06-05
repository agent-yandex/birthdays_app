from datetime import date, timedelta

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import select

from app.database.connection import sessionmaker
from app.database.models import User, Subscription
from app.utils.authorization import AuthorizedUser, get_user
from app.utils.responses import (
    UnauthorizedResponses,
    SubscribeResponses,
    UnsubscribeResponses,
)

router = APIRouter(tags=["subscriptions"])


@router.get(
    "/subscriptions/",
    response_model=list[User.UserModel],
    responses=UnauthorizedResponses.responses(),
    summary="All user subscriptions to birthdays",
)
async def all_birthdays(current_user: AuthorizedUser) -> list[User.UserModel]:
    subscriptions = []
    async with sessionmaker() as session:
        for subscription in current_user.subscriptions:
            user_sub = await session.scalar(select(User).where(User.id == subscription.user_sub_id))
            subscriptions.append(User.UserModel(**user_sub.__dict__))

    return subscriptions


class NotificationsModel(BaseModel):
    today_birthdays: list[User.UserModel]
    tomorrow_birthdays: list[User.UserModel]


@router.get(
    "/notifications/",
    response_model=NotificationsModel,
    responses=UnauthorizedResponses.responses(),
    summary="Birthday notifications",
)
async def notifications(current_user: AuthorizedUser):
    async with sessionmaker() as session:
        today_birthdays = []
        tomorrow_birthdays = []
        user = await session.scalar(select(User).where(User.id == current_user.id))
        for subscription in user.subscriptions:
            user_sub = await session.scalar(select(User).where(User.id == subscription.user_sub_id))

            current_date = date.today()
            tomorrow_date = current_date + timedelta(days=1)

            if (user_sub.birthday.day == current_date.day and
                user_sub.birthday.month == current_date.month):
                today_birthdays.append(User.UserModel(**user_sub.__dict__))
            if (user_sub.birthday.day == tomorrow_date.day and
                user_sub.birthday.month == tomorrow_date.month):
                tomorrow_birthdays.append(User.UserModel(**user_sub.__dict__))

    return NotificationsModel(today_birthdays=today_birthdays, tomorrow_birthdays=tomorrow_birthdays)


@router.post(
    "/subscribe/",
    response_model=User.UserModel,
    responses=SubscribeResponses.responses(),
    summary="Subscribe to user's birthday",
)
async def subscribe(
    current_user: AuthorizedUser,
    form_data: User.FindUserModel
) -> User.UserModel:
    user_sub = await get_user(form_data.username)
    if not user_sub:
        raise SubscribeResponses.USER_NOT_FOUND.value

    async with sessionmaker() as session:
        is_exist = await session.scalar(select(Subscription).where(
            Subscription.user_id == current_user.id,
            Subscription.user_sub_id == user_sub.id,
        ))
        if is_exist:
            raise SubscribeResponses.ALREADY_EXIST.value

        sub = Subscription(
            user_id=current_user.id,
            user_sub_id=user_sub.id,
        )
        session.add(sub)
        await session.commit()

    return User.UserModel(**user_sub.__dict__)


@router.delete(
    "/unsubscribe/",
    response_model=User.UserModel,
    responses=UnsubscribeResponses.responses(),
    summary="Unsubscribe from the birthday notification",
)
async def unsubscribe(
    current_user: AuthorizedUser,
    form_data: User.FindUserModel,
) -> User.UserModel:
    user_sub = await get_user(form_data.username)
    if not user_sub:
        raise UnsubscribeResponses.USER_NOT_FOUND.value
    
    async with sessionmaker() as session:
        sub = await session.scalar(select(Subscription).where(
            Subscription.user_id == current_user.id,
            Subscription.user_sub_id == user_sub.id,
        ))
        if not sub:
            raise UnsubscribeResponses.NOT_EXIST.value

        await session.delete(sub)
        await session.commit()

    return User.UserModel(**user_sub.__dict__)
