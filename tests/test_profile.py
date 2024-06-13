"""Test suite for user profile management and authentication endpoints."""

from typing import Any

from sqlalchemy import select

from conftest import client, async_session_maker
from test_auth import get_test_user_token
from app.database.models import User


def test_profile(user_data: dict[str, Any]) -> None:
    """
    Test fetching user profile information.

    Args:
        user_data: User data including username and password.
    """
    response = client.get(
        url="/api/profile",
        headers={"Authorization": f"Bearer {get_test_user_token(user_data)}"},
    )
    assert User.UserModel(**response.json()) == User.UserModel(**user_data)


def test_update_profile(
    user_data: dict[str, Any], second_user_data: dict[str, Any],
) -> None:
    """
    Test updating user profile information.

    Args:
        user_data: User data including username and password.
        second_user_data: User data for updating profile information.
    """
    response = client.patch(
        "/api/update_profile",
        json={
            "name": second_user_data["name"],
            "surname": second_user_data["surname"],
            "birthday": second_user_data["birthday"],
        },
        headers={"Authorization": f"Bearer {get_test_user_token(user_data)}"},
    )

    exception_model = User.UserModel(
        username=user_data["username"],
        name=second_user_data["name"],
        surname=second_user_data["surname"],
        birthday=second_user_data["birthday"],
    )
    assert User.UserModel(**response.json()) == exception_model
    assert response.status_code == 200


async def test_change_password_conflict(
    user_data: dict[str, Any], second_user_data: dict[str, Any],
) -> None:
    """
    Test handling of conflicting password change attempts.

    Args:
        user_data: User data including username and password.
        second_user_data: User data for conflicting password change attempt.
    """
    response = client.put(
        "/api/change_password",
        json={
            "password": second_user_data["password"],
            "new_password": user_data["password"],
        },
        headers={"Authorization": f"Bearer {get_test_user_token(user_data)}"},
    )

    assert response.status_code == 401


async def test_change_password(
    user_data: dict[str, Any], second_user_data: dict[str, Any],
) -> None:
    """
    Test successful password change operation.

    Args:
        user_data: User data including username and password.
        second_user_data: User data for updating password.
    """
    response = client.put(
        "/api/change_password",
        json={
            "password": user_data["password"],
            "new_password": second_user_data["password"],
        },
        headers={"Authorization": f"Bearer {get_test_user_token(user_data)}"},
    )

    async with async_session_maker() as session:
        user = await session.scalar(
            select(User).where(User.username == user_data["username"]),
        )
        assert user.is_password_valid(second_user_data["password"])

        user.password = User.generate_hash(user_data["password"])
        await session.commit()
        await session.refresh(user)

    assert response.status_code == 200
