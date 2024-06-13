"""
Module defining SQLAlchemy models and utility functions for user management.

This module contains SQLAlchemy models representing users and their subscriptions,
along with utility functions for user authentication and validation.
"""

from datetime import date
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from passlib.handlers.pbkdf2 import pbkdf2_sha256
from pydantic import Field, StringConstraints
from pydantic_marshals.sqlalchemy import MappedModel
from sqlalchemy import Date, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(AsyncAttrs, DeclarativeBase):
    pass


class UUIDMixin:
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)


async def check_birthday(birthday: date) -> None:
    if birthday > date.today():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Birthday must be less then current date",
        )


class User(UUIDMixin, Base):
    __tablename__ = "user"

    username: Mapped[str] = mapped_column(String(20))
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(20))
    surname: Mapped[str] = mapped_column(String(20))
    birthday: Mapped[str] = mapped_column(Date)

    subscriptions: Mapped[list["Subscription"]] = relationship(
        back_populates="user", foreign_keys="Subscription.user_id", lazy="selectin",
    )

    # Validators
    UsernameType = Annotated[str, Field(pattern="^[a-z0-9_.]{4,20}$")]
    PasswordType = Annotated[str, Field(min_length=6, max_length=100)]
    NameType = Annotated[
        str | None,
        StringConstraints(strip_whitespace=True),
        Field(min_length=2, max_length=30),
    ]

    # Models for enpoints
    UserModel = MappedModel.create(columns=[username, name, surname, birthday])
    UserPatchModel = MappedModel.create(
        columns=[
            (name, NameType),
            (surname, NameType),
            birthday,
        ]
    )
    FindUserModel = MappedModel.create(columns=[username])
    RegistrationModel = MappedModel.create(
        columns=[
            (username, UsernameType),
            (password, PasswordType),
            (name, NameType),
            (surname, NameType),
            birthday,
        ],
    )

    @staticmethod
    def generate_hash(password: str) -> str:
        return pbkdf2_sha256.hash(password)

    def is_password_valid(self, password: str) -> bool:
        return pbkdf2_sha256.verify(password, self.password)

    __table_args__ = (
        UniqueConstraint("username", name="username_unique"),
        Index("hash_index_username", username, postgresql_using="hash"),
    )


class Subscription(UUIDMixin, Base):
    __tablename__ = "subscription"

    user_id: Mapped[str] = mapped_column(ForeignKey("user.id"))
    user_sub_id: Mapped[str] = mapped_column(ForeignKey("user.id"))

    user: Mapped["User"] = relationship(
        back_populates="subscriptions",
        foreign_keys="Subscription.user_id",
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id", "user_sub_id", name="user_id_subscription_id_unique",
        ),
        Index("hash_index_user_id", user_id, postgresql_using="hash"),
    )
