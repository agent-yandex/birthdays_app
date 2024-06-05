import asyncio
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

from app.database.models import Base, User, Subscription
from app.database.connection import get_db_url

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", get_db_url())

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        version_table_schema=target_metadata.schema,
        include_schemas=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()


# def run_migrations_offline() -> None:
#     url = config.get_main_option("sqlalchemy.url")
#     context.configure(
#         url=url,
#         target_metadata=target_metadata,
#         literal_binds=True,
#         dialect_opts={"paramstyle": "named"},
#     )

#     with context.begin_transaction():
#         context.run_migrations()


# def run_migrations_online() -> None:
#     connectable = engine_from_config(
#         config.get_section(config.config_ini_section, {}),
#         prefix="sqlalchemy.",
#         poolclass=pool.NullPool,
#     )

#     with connectable.connect() as connection:
#         context.configure(
#             connection=connection, target_metadata=target_metadata
#         )

#         with context.begin_transaction():
#             context.run_migrations()


# def do_run_migrations(connection: Connection) -> None:
#     context.configure(
#         connection=connection,
#         target_metadata=target_metadata,
#         version_table_schema=target_metadata.schema,
#         include_schemas=True,
#     )

#     with context.begin_transaction():
#         context.run_migrations()


# async def run_async_migrations() -> None:
#     """In this scenario we need to create an Engine
#     and associate a connection with the context.

#     """

#     connectable = async_engine_from_config(
#         config.get_section(config.config_ini_section, {}),
#         prefix="sqlalchemy.",
#         poolclass=pool.NullPool,
#     )

#     async with connectable.connect() as connection:
#         await connection.run_sync(do_run_migrations)

#     await connectable.dispose()



# if context.is_offline_mode():
#     run_migrations_offline()
# else:
#     run_migrations_online()