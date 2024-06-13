"""
This module defines the API endpoints for managing user subscriptions and notifications.

Each endpoint uses dependencies to authenticate the user and manage database sessions.
Responses include various HTTP status codes and corresponding response models.
"""

from datetime import date, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_async_session
from app.database.models import Subscription, User
from app.utils.authorization import AuthorizedUser, get_user
from app.utils.responses import (
    SubscribeResponses,
    UnauthorizedResponses,
    UnsubscribeResponses,
)

router = APIRouter(tags=["subscriptions"])


@router.get(
    "/subscriptions/",
    response_model=list[User.UserModel],
    responses=UnauthorizedResponses.responses(),
    summary="All user subscriptions to birthdays",
)
async def all_birthdays(
    current_user: AuthorizedUser,
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> list[User.UserModel]:
    """
    Endpoint to retrieve all subscriptions of the current authenticated user.

    Args:
        current_user: Instance of AuthorizedUser representing the current authenticated user.
        session: Asynchronous database session obtained from get_async_session dependency.

    Raises:
        :HTTPException: If the user is not authenticated.

    Returns:
        list[User.UserModel]: List of Pydantic data models (subscriptions of the user).
    """
    subscriptions = []
    for subscription in current_user.subscriptions:
        user_sub = await session.scalar(
            select(User).where(User.id == subscription.user_sub_id),
        )
        subscriptions.append(User.UserModel(**user_sub.__dict__))

    return subscriptions


class NotificationsModel(BaseModel):
    """Data model representing notifications."""

    today_birthdays: list[User.UserModel]
    tomorrow_birthdays: list[User.UserModel]


@router.get(
    "/notifications/",
    response_model=NotificationsModel,
    responses=UnauthorizedResponses.responses(),
    summary="Birthday notifications",
)
async def notifications(
    current_user: AuthorizedUser,
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> NotificationsModel:
    """
    Endpoint to retrieve notifications for today's and tomorrow's birthdays of the users.

    Args:
        current_user: Instance of AuthorizedUser representing the current authenticated user.
        session: Asynchronous database session obtained from get_async_session dependency.

    Raises:
        :HTTPException: If the user is not authenticated.

    Returns:
        NotificationsModel: A model containing lists of today's and tomorrow's birthdays.
    """
    today_birthdays = []
    tomorrow_birthdays = []

    user = await session.scalar(select(User).where(User.id == current_user.id))
    for subscription in user.subscriptions:
        user_sub = await session.scalar(
            select(User).where(User.id == subscription.user_sub_id),
        )

        current_date = date.today()
        tomorrow_date = current_date + timedelta(days=1)

        is_today_birthday = (
            user_sub.birthday.day == current_date.day
            and user_sub.birthday.month == current_date.month
        )
        is_tomorrow_birthday = (
            user_sub.birthday.day == tomorrow_date.day
            and user_sub.birthday.month == tomorrow_date.month
        )

        if is_today_birthday:
            today_birthdays.append(User.UserModel(**user_sub.__dict__))
        if is_tomorrow_birthday:
            tomorrow_birthdays.append(User.UserModel(**user_sub.__dict__))

    return NotificationsModel(
        today_birthdays=today_birthdays,
        tomorrow_birthdays=tomorrow_birthdays,
    )


@router.post(
    "/subscribe/",
    response_model=User.UserModel,
    responses=SubscribeResponses.responses(),
    summary="Subscribe to user's birthday",
)
async def subscribe(
    current_user: AuthorizedUser,
    form_data: User.FindUserModel,
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> User.UserModel:
    """
    Endpoint to subscribe the current authenticated user to another user's birthday notifications.

    Args:
        current_user: Instance of AuthorizedUser representing the current authenticated user.
        form_data: Data model containing the username of the user to subscribe to.
        session: Asynchronous database session obtained from get_async_session dependency.

    Raises:
        :HTTPException:
            - If the user to subscribe to is not found.
            - If the subscription already exists.

    Returns:
        User.UserModel: Pydantic data model representing the subscribed user.
    """
    user_sub = await get_user(form_data.username, session)
    if not user_sub:
        raise SubscribeResponses.USER_NOT_FOUND.value

    is_exist = await session.scalar(
        select(Subscription).where(
            Subscription.user_id == current_user.id,
            Subscription.user_sub_id == user_sub.id,
        ),
    )
    if is_exist:
        raise SubscribeResponses.ALREADY_EXIST.value

    sub = Subscription(
        user_id=current_user.id,
        user_sub_id=user_sub.id,
    )
    session.add(sub)
    await session.commit()
    await session.refresh(user_sub)

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
    session: Annotated[AsyncSession, Depends(get_async_session)],
) -> User.UserModel:
    """
    Endpoint to unsubscribe the current authenticated user to user's birthday notifications.

    Args:
        current_user: Instance of AuthorizedUser representing the current authenticated user.
        form_data: Data model containing the username of the user to unsubscribe from.
        session: Asynchronous database session obtained from get_async_session dependency.

    Raises:
        :HTTPException:
            - If the user to unsubscribe from is not found.
            - If the subscription does not exist.

    Returns:
        User.UserModel: Pydantic data model representing the unsubscribed user.
    """
    user_sub = await get_user(form_data.username, session)
    if not user_sub:
        raise UnsubscribeResponses.USER_NOT_FOUND.value

    sub = await session.scalar(
        select(Subscription).where(
            Subscription.user_id == current_user.id,
            Subscription.user_sub_id == user_sub.id,
        ),
    )
    if not sub:
        raise UnsubscribeResponses.NOT_EXIST.value

    await session.delete(sub)
    await session.commit()
    await session.refresh(user_sub)

    return User.UserModel(**user_sub.__dict__)
