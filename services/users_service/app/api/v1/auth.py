from fastapi import (
    APIRouter,
    Depends,
    status,
    Response,
    HTTPException,
    Request,
    Security,
)
from datetime import datetime, timezone
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from services.users_service.app.core.deps import get_auth_service, get_current_user
from services.users_service.app.core.jwt import decode_token_or_raise
from services.users_service.app.db.models.user import UserAccount
from services.users_service.app.schemas.auth import (
    UserRegistration,
    UserResponse,
    TokenPair,
    UserLogin,
    PasswordChange,
)
from services.users_service.app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_data: UserRegistration,
    svc: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """
    Registers a new user using the provided user data. This endpoint supports
    creating a new user account based on the details specified in the
    user_data parameter. It returns a representation of the newly created user
    as a response.

    :param user_data: The user registration data required for creating a new user.
    :type user_data: UserRegistration
    :param svc: The authentication service used to handle user registration.
                This service is injected using dependency injection.
    :type svc: AuthService
    :return: The newly created user details encapsulated in a UserResponse model.
    :rtype: UserResponse
    """
    result = await svc.register_user(user_data)
    return UserResponse(**result)


@router.post("/login", response_model=TokenPair)
async def login(
    user_data: UserLogin,
    response: Response,
    svc: AuthService = Depends(get_auth_service),
) -> TokenPair:
    """
    Handles the login process for a user.

    This endpoint authenticates the user credentials, generates a token pair, and sets a
    secure cookie for the refresh token. The generated tokens are used for managing user
    authentication and session. The access token is returned in the response, while the
    refresh token is set as a browser cookie.

    :param user_data: The login payload containing user credentials.
    :type user_data: UserLogin
    :param response: The HTTP response object used to set the refresh token cookie.
    :type response: Response
    :param svc: The authentication service dependency used to handle the login process.
    :type svc: AuthService
    :return: A token pair containing the access token and refresh token.
    :rtype: TokenPair
    """
    result = await svc.login_user(user_data)
    await svc.set_cookie(response, result["refresh_token"])
    return TokenPair(
        access_token=result["access_token"],
        refresh_token="",
        token_type="bearer",
    )


@router.post("/refresh", response_model=TokenPair)
async def refresh_tokens(
    request: Request,
    response: Response,
    svc: AuthService = Depends(get_auth_service),
) -> TokenPair:
    """
    Refresh user authentication tokens by validating a refresh token provided as a cookie.
    If the refresh token is missing or invalid, an HTTPException is raised. Upon successful
    refresh, the response will include an updated access token and modifications to the
    refresh token as a secure cookie.

    :param request: The HTTP request object containing the cookies.
    :type request: Request
    :param response: The HTTP response object used to set cookies.
    :type response: Response
    :param svc: Asynchronous dependency providing authentication service.
    :type svc: AuthService
    :return: An updated token pair containing the access token and refresh token.
    :rtype: TokenPair
    :raises HTTPException: If the refresh token cookie is missing or invalid.
    """
    raw = request.cookies.get("refresh_token")
    if not raw:
        raise HTTPException(status_code=401, detail="Missing refresh cookie")

    try:
        pair = await svc.refresh_tokens(raw)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

    await svc.set_cookie(response, pair["refresh_token"])
    return TokenPair(
        access_token=pair["access_token"],
        refresh_token="",
        token_type="bearer",
    )


@router.delete("/logout")
async def logout(
    request: Request,
    response: Response,
    current_user=Depends(get_current_user),
    creds: HTTPAuthorizationCredentials = Security(HTTPBearer(auto_error=False)),
    svc: AuthService = Depends(get_auth_service),
) -> dict:
    """
    Handles the logout process for the current user by invalidating provided tokens and
    removing the refresh token cookie.

    :param request: Used to access incoming HTTP request data, including cookies.
                    Expected to be of type Request.
    :param response: Allows modification of the outgoing HTTP response, such as
                     deleting cookies. Expected to be of type Response.
    :param current_user: Dependency injection for fetching the currently authenticated
                         user's details. Provided by the `get_current_user` dependency.
    :param creds: Optional authorization credentials provided in the request headers.
                  Expected to be resolved using the `HTTPBearer` security scheme.
    :param svc: Dependency injection for the authentication service. Responsible for
                processing logout logic. Provided by the `get_auth_service` dependency.
    :return: A dictionary containing the result of the logout operation, such as a
             status message or other relevant data.
    """
    access_token = creds.credentials if creds and creds.credentials else None
    refresh_token = request.cookies.get("refresh_token")

    result = await svc.logout_user(
        str(current_user.email),
        access_token=access_token,
        refresh_token=refresh_token,
    )
    await svc.delete_cookie(response)
    return result


@router.put("/password")
async def change_password(
    password_data: PasswordChange,
    current_user: UserAccount = Depends(get_current_user),
    svc: AuthService = Depends(get_auth_service),
) -> dict:
    """
    Changes the password for the currently authenticated user.

    This function is intended to allow a user to update their password by providing
    the necessary data. The current user's email is used to identify the account
    for which the password change is applied.

    :param password_data: Object containing the necessary data for changing the
        password, including the old password and the new password.
    :type password_data: PasswordChange
    :param current_user: The currently authenticated user for whom the password
        will be changed. This is resolved using a dependency to retrieve the
        authenticated user.
    :type current_user: UserAccount
    :param svc: The authentication service for handling password change logic.
        This is resolved using a dependency to inject the appropriate service.
    :type svc: AuthService
    :return: A dictionary containing the result of the password change operation.
    :rtype: dict
    """
    result = await svc.change_password(str(current_user.email), password_data)
    return result


@router.get("/google/url")
async def google_url(svc: AuthService = Depends(get_auth_service)):
    """Creates a URL for Google OAuth2 authentication.
    This endpoint generates a URL that initiates the Google OAuth2 flow,
    allowing users to authenticate using their Google accounts.

    :param svc: The authentication service for generating the Google auth URL.
        This is resolved using a dependency to inject the appropriate service.
    :type svc: AuthService
    :return: A dictionary containing the generated Google authentication URL.
    :rtype: dict
    """
    return await svc.generate_google_auth_url()


@router.get("/google/callback")
async def google_callback(
    code: str,
    svc: AuthService = Depends(get_auth_service),
):
    """Handles the callback from Google OAuth2 after successful authentication.
    This endpoint processes the callback received from Google after a user has a code after authenticated.

    :param code: The code that Google sends after authentication.
    :type: str,
    :param: svc: The authentication service for handling Google auth code and responses for token resolving.
        This is resolved using a dependency to inject the appropriate service.
    :type svc: AuthService
    :return: Returns redirecting response with tokens in cookie.
    :rtype: RedirectResponse
    """
    return await svc.handle_google_auth_callback(code)
