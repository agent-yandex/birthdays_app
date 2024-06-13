"""This module defines custom response classes."""

from enum import Enum
from typing import Any

from fastapi import HTTPException, status


class Responses(HTTPException, Enum):
    """
    Custom enumeration class for defining HTTP error responses.

    This class extends both HTTPException and Enum to define custom responses for various HTTP error scenarios.
    It provides a method to generate a dictionary of HTTP response codes with corresponding error details and examples.

    Attributes:
        value (HTTPException): The base HTTPException value associated with each response.
    """

    value: HTTPException

    @classmethod
    def responses(cls) -> dict[str | int, dict[str, Any]]:
        result: dict[str | int, dict[str, Any]] = {}
        code_counts: dict[int, int] = {}
        for response in cls.__members__.values():
            error = response.value
            code_counts[error.status_code] = code_counts.get(error.status_code, -1) + 1

            status_code = str(error.status_code) + " " * code_counts[error.status_code]
            result[status_code] = {
                "description": error.detail,
                "content": {
                    "application/json": {
                        "schema": {"properties": {"detail": {"const": error.detail}}},
                        "example": {"detail": error.detail},
                    }
                },
            }
        return result


class UnauthorizedResponses(Responses):
    UNAUTHORIZED = (status.HTTP_401_UNAUTHORIZED, "Unauthorized user")


class SigninResponses(Responses):
    INCORRECT_SIGNIN = (status.HTTP_401_UNAUTHORIZED, "Incorrect username or password")


class SignupResponses(Responses):
    INCORRECT_BIRTHDAY = (
        status.HTTP_409_CONFLICT,
        "Birthday must be less then current date",
    )
    USERNAME_IN_USE = (status.HTTP_409_CONFLICT, "Username already in use")


class SubscribeResponses(Responses):
    UNAUTHORIZED = (status.HTTP_401_UNAUTHORIZED, "Unauthorized user")
    USER_NOT_FOUND = (status.HTTP_404_NOT_FOUND, "User not found")
    ALREADY_EXIST = (status.HTTP_409_CONFLICT, "Already subscribed")


class UnsubscribeResponses(Responses):
    UNAUTHORIZED = (status.HTTP_401_UNAUTHORIZED, "Unauthorized user")
    USER_NOT_FOUND = (status.HTTP_404_NOT_FOUND, "User not found")
    NOT_EXIST = (status.HTTP_409_CONFLICT, "There is no subscription")


class ChangePasswordResponses(Responses):
    WRONG_PASSWORD = (status.HTTP_401_UNAUTHORIZED, "Wrong password")
    PASSWORD_MATCHES_CURRENT = (
        status.HTTP_409_CONFLICT,
        "New password matches the current one",
    )


class UpdateProfileResponses(Responses):
    UNAUTHORIZED = (status.HTTP_401_UNAUTHORIZED, "Unauthorized user")
    INCORRECT_BIRTHDAY = (
        status.HTTP_409_CONFLICT,
        "Birthday must be less then current date",
    )
