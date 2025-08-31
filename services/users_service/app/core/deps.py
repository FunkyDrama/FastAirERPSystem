from fastapi import Request, Depends, HTTPException, Security
from typing import cast
from collections.abc import AsyncGenerator

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from services.users_service.app.core.jwt import decode_token_or_raise
from services.users_service.app.core.token_store import TokenStore
from services.users_service.app.db.models.user import UserAccount
from services.users_service.app.repositories.booking_repo import BookingRepository
from services.users_service.app.repositories.user_repo import UserRepository
from services.users_service.app.services.auth import AuthService
from services.users_service.app.services.booking import BookingService
from services.users_service.app.services.flights import FlightQueryService
from services.users_service.app.services.me import MeService
from services.users_service.app.services.payment import PaymentService


def get_token_store(request: Request) -> TokenStore:
    """
    Retrieve the token store from the application state.

    This function extracts the token storage object from the application's
    state linked to the incoming request. The token store is used to
    manage and store authentication tokens.

    :param request: The incoming request object, providing access to the application's state.
    :type request: Request
    :return: The token store object used for authentication token management.
    :rtype: TokenStore
    """
    return request.app.state.token_store


def get_sessionmaker(request: Request) -> async_sessionmaker[AsyncSession]:
    try:
        return cast(async_sessionmaker[AsyncSession], request.app.state.sessionmaker)
    except AttributeError as e:
        raise RuntimeError(
            "Sessionmaker is not in app.state. Check lifespan init."
        ) from e


async def get_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    sm = get_sessionmaker(request)
    async with sm() as session:
        yield session


def get_auth_service(
    sm: async_sessionmaker[AsyncSession] = Depends(get_sessionmaker),
    ts: TokenStore = Depends(get_token_store),
) -> AuthService:
    return AuthService(sessionmaker=sm, token_store=ts)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(HTTPBearer(auto_error=False)),
    session: AsyncSession = Depends(get_session),
    store: TokenStore = Depends(get_token_store),
) -> UserAccount:
    """
    Retrieves the current authenticated user based on the provided bearer token. This
    function verifies the token's validity, ensures it is an access token, checks its
    validity against a token store, and loads the corresponding user from the database.
    If the user account is blocked or the token is invalid, appropriate HTTP exceptions
    are raised.

    :param credentials: HTTP authorization credentials, extracted as a bearer token.
    :type credentials: HTTPAuthorizationCredentials
    :param session: Database session used to perform database operations.
    :type session: AsyncSession
    :param store: A token store to verify the validity of the "access" token.
    :type store: TokenStore
    :return: The authenticated user retrieved from the database if all checks pass.
    :rtype: User
    """
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Missing bearer token")

    repo = UserRepository(session)
    token = credentials.credentials
    try:
        payload = decode_token_or_raise(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    if payload.get("typ") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")

    jti = payload.get("jti")
    if not jti or not await store.is_allowed("access", jti):
        raise HTTPException(status_code=401, detail="Invalid token")

    uid = payload.get("sub")
    if not uid:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await repo.get_user_by_id(uid)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user


def get_flight_service(
    session: AsyncSession = Depends(get_session),
) -> FlightQueryService:
    """
    Creates and returns an instance of the FlightQueryService.

    The service utilizes the provided database session to perform flight-related
    queries and operations.

    :param session: The asynchronous session instance for interacting with the
        database.
    :return: An initialized FlightQueryService instance.
    :rtype: FlightQueryService
    """
    return FlightQueryService(session)


def get_booking_service(
    session: AsyncSession = Depends(get_session),
    user: UserAccount = Depends(get_current_user),
) -> BookingService:
    """
    Retrieve an instance of BookingService by providing required dependencies.

    This factory function leverages dependency injection to create and return an
    instance of the BookingService. The session parameter provides access to the
    database session, while the user parameter represents the current authenticated
    user.

    :param session: The asynchronous database session used for interaction with the
        database.
    :type session: AsyncSession
    :param user: The current authenticated user.
    :type user: UserAccount
    :return: An instance of BookingService with the provided session and user.
    :rtype: BookingService
    """
    return BookingService(session=session, current_user=user)


def get_me_service(
    session: AsyncSession = Depends(get_session),
    user: UserAccount = Depends(get_current_user),
) -> MeService:
    """
    Creates and returns an instance of the MeService class.

    This function is responsible for creating a new `MeService` object, which includes
    the session and current user dependencies as its attributes. The session is used
    to interact with the database, and the user object represents the currently
    authenticated user.

    :param session: The asynchronous database session used for data access.
    :type session: AsyncSession
    :param user: The currently authenticated user object.
    :type user: UserAccount
    :return: An instance of the `MeService` class initialized with the session and user.
    :rtype: MeService
    """
    return MeService(session=session, current_user=user)


def get_payment_service(
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    """
    Provides an instance of the PaymentService class, which serves as the main
    service for handling payment-related functionality. This function is designed
    to inject the necessary dependencies, including the database session and the
    current authenticated user.

    :param session: An asynchronous database session instance, used for database
        operations.
    :param user: The currently authenticated user whose payment operations
        will be processed.
    :return: An instance of the PaymentService class, configured with the
        necessary dependencies.
    """
    return PaymentService(BookingRepository(session), user)
