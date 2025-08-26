import uuid
from datetime import datetime, timedelta, timezone
from typing import Literal, TypedDict
import jwt
from services.users_service.app.core.config import jwt_settings


class TokenPayload(TypedDict, total=False):
    """
    Represents the payload of a token.

    This class is used as a TypedDict to define the structure and attributes
    for a token payload. It is primarily utilized for access and refresh token
    generation and validation processes in secure systems.

    :ivar sub: Subject identifier of the token, typically representing the
        user ID or unique entity linked to the token.
    :type sub: str
    :ivar typ: The type of token, restricted to either "access" or "refresh".
    :type typ: Literal["access", "refresh"]
    :ivar exp: Expiration time of the token, represented as a UNIX timestamp.
    :type exp: int
    :ivar iat: Issued-at time, represented as a UNIX timestamp indicating when
        the token was created.
    :type iat: int
    :ivar role: The role or permission level associated with the token, defining
        the scope of access.
    :type role: str
    """

    sub: str
    typ: Literal["access", "refresh"]
    jti: str
    exp: int
    iat: int
    role: str


def _encode(payload: TokenPayload) -> str:
    """
    Encodes the given payload into a JWT token.

    :param payload: The data to be encoded into the JWT token.
    :type payload: TokenPayload
    :return: A JWT token as a string.
    :rtype: str
    """
    return jwt.encode(
        payload,
        jwt_settings.JWT_SECRET.get_secret_value(),
        algorithm=jwt_settings.JWT_ALG,
    )


def _decode(token: str) -> TokenPayload:
    """
    Decodes a JWT token to extract its payload.

    This function takes a JWT token as input and decodes it using the
    given secret value and specified algorithm. It returns the token
    payload if the decoding is successful.

    :param token: A string representing the JWT token to decode.
    :type token: str
    :return: The decoded token payload.
    :rtype: TokenPayload
    """
    return jwt.decode(
        token,
        jwt_settings.JWT_SECRET.get_secret_value(),
        algorithms=[jwt_settings.JWT_ALG],
    )


def create_access_token(user_id: uuid.UUID, role: str) -> str:
    """
    Generate a JWT access token for a given user.

    This function creates an access token, encoding the provided user identifier
    and role, along with additional metadata such as token type, issued time, and
    expiration time.

    :param user_id: The unique identifier of the user for whom the token is being generated
    :param role: The role of the user, specifying access permissions or user type
    :return: A string representing the encoded JWT access token
    """
    now = datetime.now(timezone.utc)
    jti = str(uuid.uuid4())
    exp = now + timedelta(seconds=jwt_settings.ACCESS_TTL_SECONDS)
    return _encode(
        {
            "sub": str(user_id),
            "role": role,
            "typ": "access",
            "jti": jti,
            "iat": int(now.timestamp()),
            "exp": int(exp.timestamp()),
        }
    )


def create_refresh_token(user_id: uuid.UUID, role: str) -> str:
    """
    Generates a refresh token for a user based on their user ID and role. The token
    is configured to expire after the refresh token time-to-live (TTL) duration,
    specified in settings. The token contains information such as the `sub` (subject),
    `role`, its type, issuance timestamp (`iat`), and expiration timestamp (`exp`).

    :param user_id: The unique identifier of the user for whom the refresh token
        is being created.
    :param role: The role of the user, which determines their access level.
    :return: A string representing the encoded refresh token.
    """
    now = datetime.now(timezone.utc)
    jti = str(uuid.uuid4())
    exp = now + timedelta(seconds=jwt_settings.REFRESH_TTL_SECONDS)
    return _encode(
        {
            "sub": str(user_id),
            "role": role,
            "typ": "refresh",
            "jti": jti,
            "iat": int(now.timestamp()),
            "exp": int(exp.timestamp()),
        }
    )


def decode_token_or_raise(token: str) -> TokenPayload:
    """
    Decodes an input token and returns the payload. This function ensures that the
    given token is processed and transformed into its corresponding payload
    representation. If the decoding process encounters any issues, an exception
    might occur which should be handled by the calling code.

    :param token: A string representing the token that needs to be decoded.
    :type token: str
    :return: The payload extracted from the decoded token.
    :rtype: TokenPayload
    """
    return _decode(token)
