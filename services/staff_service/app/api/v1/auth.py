from fastapi import APIRouter, Response, Depends, Request, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from services.staff_service.app.core.deps import get_auth_service, get_current_user
from services.staff_service.app.schemas.auth import TokenPair, StaffUserLogin
from services.staff_service.app.services.auth import StaffAuthService

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=TokenPair)
async def login(
    staff_user_data: StaffUserLogin,
    response: Response,
    svc: StaffAuthService = Depends(get_auth_service),
) -> TokenPair:
    """
    Handles the login process for a user.

    This endpoint authenticates the user credentials, generates a token pair, and sets a
    secure cookie for the refresh token. The generated tokens are used for managing user
    authentication and session. The access token is returned in the response, while the
    refresh token is set as a browser cookie.

    :param staff_user_data: The login payload containing user credentials.
    :type staff_user_data: UserLogin
    :param response: The HTTP response object used to set the refresh token cookie.
    :type response: Response
    :param svc: The authentication service dependency used to handle the login process.
    :type svc: StaffAuthService
    :return: A token pair containing the access token and refresh token.
    :rtype: TokenPair
    """
    result = await svc.login_user(staff_user_data)
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
    svc: StaffAuthService = Depends(get_auth_service),
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
    :type svc: StaffAuthService
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
    svc: StaffAuthService = Depends(get_auth_service),
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
