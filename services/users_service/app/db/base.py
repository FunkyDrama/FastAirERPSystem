from sqlalchemy import text
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from services.users_service.app.db.settings import db_settings


class Base(DeclarativeBase):
    """
    Base class for database models using SQLAlchemy's DeclarativeBase.

    This class serves as the foundation for all database models in the
    application, utilizing SQLAlchemy's declarative base to provide table
    mappings and ORM capabilities. Subclass this to define specific database
    models for tables.

    """

    pass


def make_engine() -> AsyncEngine:
    """
    Create and configure an asynchronous database engine using SQLAlchemy.

    The function utilizes the database URL from the application db_settings to
    build an asynchronous engine. This engine handles establishing connections
    to the database efficiently, with features like future compatibility mode,
    connection pre-pinging to ensure connection health, and echoing disabled
    for less verbose logging.

    :return: An instance of AsyncEngine configured as per the application's
             database db_settings.
    :rtype: AsyncEngine
    """
    return create_async_engine(
        db_settings.DATABASE_URL,
        future=True,
        echo=False,
        pool_pre_ping=True,
    )


def make_sessionmaker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """
    Creates a sessionmaker instance for database operations.

    This function is used to create a sessionmaker, which serves as
    a factory for new `AsyncSession` instances. The generated
    sessionmaker is configured with options such as disabling the
    expiration of objects on commit.

    :param engine: The asynchronous database engine used to bind the sessionmaker.
    :type engine: AsyncEngine
    :return: A configured `async_sessionmaker` to create `AsyncSession` instances.
    :rtype: async_sessionmaker[AsyncSession]
    """
    return async_sessionmaker(engine, expire_on_commit=False)


async def close_engine(engine: AsyncEngine) -> None:
    """
    Closes the given asynchronous database engine.

    This function is used to properly dispose of the resources associated
    with an asynchronous database engine.

    :param engine: The asynchronous database engine to be closed.
    :type engine: AsyncEngine
    :return: None
    :rtype: None
    """
    await engine.dispose()


async def ping(engine: AsyncEngine) -> None:
    """
    Pings the database engine to verify connectivity.

    This function ensures that the provided asynchronous database engine is
    reachable by executing a simple query. It opens a connection, executes
    a SELECT statement, and then closes the connection.

    :param engine: The asynchronous database engine to be tested.
    :type engine: AsyncEngine
    :return: None
    """
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))



from .models import user, booking, discount, flight_ref, option, passenger, seat_type, ticket