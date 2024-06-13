"""Test suite for subscription management endpoints."""

from typing import Any

from sqlalchemy import select

from conftest import client, async_session_maker
from test_auth import get_test_user_token
from app.database.models import User, Subscription


async def test_subscribe(
    user_data: dict[str, Any], second_user_data: dict[str, Any],
) -> None:
    """
    Test subscribing to another user.

    Args:
        user_data: User data including username and password.
        second_user_data: User data of the user to subscribe to.
    """
    response = client.post(
        url="/api/subscribe",
        json={"username": second_user_data["username"]},
        headers={"Authorization": f"Bearer {get_test_user_token(user_data)}"},
    )

    async with async_session_maker() as session:
        user_sub = await session.scalar(
            select(User).where(User.username == second_user_data["username"]),
        )
        sub = await session.scalar(
            select(Subscription).where(Subscription.user_sub_id == user_sub.id),
        )

        assert sub.user_sub_id == user_sub.id

    assert response.status_code == 200


def test_subscribe_conflict(
    user_data: dict[str, Any], second_user_data: dict[str, Any],
) -> None:
    """
    Test handling of conflicting subscription attempts.

    Args:
        user_data: User data including username and password.
        second_user_data: User data of the user to attempt to subscribe to.
    """
    response = client.post(
        url="/api/subscribe",
        json={"username": second_user_data["username"]},
        headers={"Authorization": f"Bearer {get_test_user_token(user_data)}"},
    )

    assert response.status_code == 409


def test_get_subscribes(user_data: dict[str, Any]) -> None:
    """
    Test fetching user subscriptions.

    Args:
        user_data: User data including username and password.
    """
    response = client.get(
        "/api/subscriptions",
        headers={"Authorization": f"Bearer {get_test_user_token(user_data)}"},
    )

    assert response.status_code == 200


async def test_unsubscribe(
    user_data: dict[str, Any], second_user_data: dict[str, Any],
) -> None:
    """
    Test unsubscribing from another user.

    Args:
        user_data: User data including username and password.
        second_user_data: User data of the user to unsubscribe from.
    """
    response = client.delete_with_payload(
        url="/api/unsubscribe",
        json={"username": second_user_data["username"]},
        headers={"Authorization": f"Bearer {get_test_user_token(user_data)}"},
    )

    async with async_session_maker() as session:
        user_sub = await session.scalar(
            select(User).where(User.username == second_user_data["username"]),
        )
        sub = await session.scalar(
            select(Subscription).where(Subscription.user_sub_id == user_sub.id),
        )
        assert sub is None

    assert response.status_code == 200


def test_unsubscribe_conflict(
    user_data: dict[str, Any], second_user_data: dict[str, Any],
) -> None:
    """
    Test handling of conflicting unsubscribe attempts.

    Args:
        user_data: User data including username and password.
        second_user_data: User data of the user to attempt to unsubscribe from.
    """
    response = client.delete_with_payload(
        url="/api/unsubscribe",
        json={"username": second_user_data["username"]},
        headers={"Authorization": f"Bearer {get_test_user_token(user_data)}"},
    )

    assert response.status_code == 409
