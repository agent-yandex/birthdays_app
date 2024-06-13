"""Tests for user authentication and registration endpoints."""

from typing import Any

from sqlalchemy import select

from conftest import client, async_session_maker
from app.database.models import User


async def test_signup(user_data: dict[str, Any]) -> None:
    """
    Test the user signup endpoint.

    Args:
        user_data: User data including username, password, name, surname, and birthday.

    Raises:
        AssertionError: If the user creation fails or the HTTP status code is not 200.
    """
    response = client.post(url="/api/signup", json=user_data)
    async with async_session_maker() as session:
        user = await session.scalar(
            select(User).where(User.username == user_data["username"]),
        )
        assert user.username == user_data["username"]

    assert response.status_code == 200


async def test_signup_conflict(user_data: dict[str, Any]) -> None:
    """
    Test the user signup endpoint with conflicting data.

    Args:
       user_data: User data including username and password.

    Raises:
       AssertionError: If the HTTP status code is not 422 indicating validation error.
    """
    conflict_data = user_data.copy()
    del conflict_data["password"]
    response = client.post(url="/api/signup", json=conflict_data)

    assert response.status_code == 422


def test_signin(user_data: dict[str, Any]) -> None:
    """
    Test the user signin endpoint.

    Args:
        user_data: User data including username and password.

    Raises:
        AssertionError: If the HTTP status code is not 200 indicating successful signin.
    """
    response = client.post(
        url="/api/signin",
        data={
            "username": user_data["username"],
            "password": user_data["password"],
        },
    )

    assert response.status_code == 200


def test_signin_conflict(second_user_data: dict[str, Any]) -> None:
    """
    Test the user signin endpoint with incorrect credentials.

    Args:
       second_user_data: User data for a different user.

    Raises:
       AssertionError: If the HTTP status code is not 401 indicating unauthorized access.
    """
    response = client.post(
        url="/api/signin",
        data={
            "username": second_user_data["username"],
            "password": second_user_data["password"],
        },
    )

    assert response.status_code == 401


async def test_signup_second_user(second_user_data: dict[str, Any]) -> None:
    """
    Test signing up a second user using the signup endpoint.

    Args:
        second_user_data: User data for the second user.

    Raises:
        AssertionError: If the user creation fails or the HTTP status code is not 200.
    """
    response = client.post(url="/api/signup", json=second_user_data)
    async with async_session_maker() as session:
        user = await session.scalar(
            select(User).where(User.username == second_user_data["username"]),
        )
        assert user.username == second_user_data["username"]

    assert response.status_code == 200


def get_test_user_token(user_data: dict[str, Any]) -> str:
    """
    Obtain an access token for a test user.

    Args:
        user_data: User data including username and password.

    Returns:
        str: Access token string.
    """
    response = client.post(
        url="/api/signin",
        data={
            "username": user_data["username"],
            "password": user_data["password"],
        },
    )

    return response.json()["access_token"]
