"""Test setup and fixtures for FastAPI application testing."""

from typing import AsyncGenerator, Any

import pytest
import rstr
from faker import Faker
from faker.providers import BaseProvider, internet
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.database.connection import get_async_session
from app.database.models import Base
from app.main import app
from app.utils.config import (
    PG_USER_TEST as PG_USER,
    PG_PASSWORD_TEST as PG_PASSWORD,
    PG_HOST_TEST as PG_HOST,
    PG_PORT_TEST as PG_PORT,
    PG_DBNAME_TEST as PG_DBNAME,
)

DB_URL = f"postgresql+asyncpg://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DBNAME}"

engine_test = create_async_engine(DB_URL, poolclass=NullPool)
async_session_maker = sessionmaker(
    engine_test, class_=AsyncSession, expire_on_commit=False,
)
Base.metadata.bind = engine_test


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Asynchronous generator that yields an SQLAlchemy AsyncSession.

    This function asynchronously creates a session using the async_session_maker
    context manager. It yields the created session once it is acquired.

    Yields:
        AsyncSession: An SQLAlchemy AsyncSession object.
    """
    async with async_session_maker() as session:
        yield session


app.dependency_overrides[get_async_session] = override_get_async_session


@pytest.fixture(autouse=True, scope="session")
async def prepare_database():
    """
    Fixture for setting up and tearing down the test database.

    Yields:
        None
    """
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn_drop:
        await conn_drop.run_sync(Base.metadata.drop_all)


class RegexGeneratorProvider(BaseProvider):
    """Provider for generating random strings based on regular expressions."""

    def generate_regex(self, pattern: str) -> str:
        """
        Generate a random string that matches the given regex pattern.

        Args:
            pattern: The regex pattern to generate a random string.

        Returns:
            str: A random string that matches the specified regex pattern.
        """
        return rstr.xeger(pattern)

    def username(self) -> str:
        """
        Generate a random username string.

        Returns:
            str: A random username string that matches the pattern '^[a-z0-9_.]{4,20}$'.
        """
        return self.generate_regex("^[a-z0-9_.]{4,20}$")


@pytest.fixture(scope="session", autouse=True)
def _setup_faker(faker: Faker) -> None:
    """
    Fixture to set up Faker with additional providers.

    Args:
        faker (Faker): Instance of Faker provided by pytest.
    """
    faker.add_provider(internet)
    faker.add_provider(RegexGeneratorProvider)


@pytest.fixture(scope="session")
def faker(_session_faker: Faker) -> Faker:
    """
    Fixture to provide a session-scoped Faker instance.

    Args:
        _session_faker: Instance of Faker provided by pytest.

    Returns:
        Faker: Session-scoped instance of Faker.
    """
    return _session_faker


@pytest.fixture(scope="session")
async def user_data(faker: Faker) -> dict[str, Any]:
    """
    Fixture to generate user data dictionary.

    Args:
        faker: Instance of Faker provided by pytest.

    Returns:
        dict[str, Any]: Dictionary containing generated user data.
    """
    birthday = faker.profile()["birthdate"]
    birthday_str = birthday.isoformat()
    return {
        "username": faker.username(),
        "password": faker.password(),
        "name": faker.name(),
        "surname": faker.name(),
        "birthday": birthday_str,
    }


@pytest.fixture(scope="session")
async def second_user_data(faker: Faker) -> dict[str, Any]:
    """
    Fixture to generate second user data dictionary.

    Args:
        faker: Instance of Faker provided by pytest.

    Returns:
        dict[str, Any]: Dictionary containing generated user data.
    """
    birthday = faker.profile()["birthdate"]
    birthday_str = birthday.isoformat()
    return {
        "username": faker.username(),
        "password": faker.password(),
        "name": faker.name(),
        "surname": faker.name(),
        "birthday": birthday_str,
    }


class CustomTestClient(TestClient):
    """Custom test client for delete responses."""

    def delete_with_payload(self, **kwargs):
        """
        Make a DELETE request with additional payload data.

        Args:
            kwargs: Keyword arguments to be passed to the request method.

        Returns:
            requests.Response: Response object returned by the DELETE request.
        """
        return self.request(method="DELETE", **kwargs)


client = CustomTestClient(app)
