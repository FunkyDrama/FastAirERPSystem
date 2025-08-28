from fastapi import Request, Depends, HTTPException, Security
from typing import cast
from collections.abc import AsyncGenerator

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from services.users_service.app.core.jwt import decode_token_or_raise
from services.users_service.app.core.token_store import TokenStore
from services.users_service.app.db.models.user import UserAccount
from services.users_service.app.repositories.user_repo import UserRepository
from services.users_service.app.services.auth import AuthService
from services.users_service.app.services.flights import FlightQueryService


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
