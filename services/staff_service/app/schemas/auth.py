from typing import Literal

from pydantic import BaseModel, EmailStr


class StaffUserLogin(BaseModel):
    email: str
    password: str


class StaffLogoutIn(BaseModel):
    """
    Represents the input data required for a logout operation.

    This class is used as a data model for logout-related input that may
    include an optional refresh token. It is intended to be utilized for
    handling logout requests or processing logout workflows.

    :ivar refresh_token: The optional refresh token provided to identify
        the session or token to be invalidated during the logout process.
    :type refresh_token: str | None
    """

    refresh_token: str | None = None


class StaffResponse(BaseModel):
    """
    Represents a user's response, including their email and a message.

    This class is designed to encapsulate the response data provided by a user,
    ensuring proper structure and validation. It includes an email field that
    adheres to a valid email format and a general message field as a text input.

    :ivar email: A valid email address provided by the user.
    :type email: EmailStr
    :ivar message: A general message or content provided by the user.
    :type message: str
    """

    email: EmailStr
    message: str


class TokenPair(BaseModel):
    """
    Represents a pair of tokens used for authentication and authorization.

    This class is a data model that stores the access token for immediate
    use and the refresh token to obtain a new access token once the current
    one expires. It ensures consistency in handling token-related data
    within the application.

    :ivar token_type: The type of token. Defaults to "bearer".
    :type token_type: Literal["bearer"]
    :ivar access_token: The token used for accessing protected resources.
    :type access_token: str
    :ivar refresh_token: The token used for obtaining a new access token
        after expiration of the current one.
    :type refresh_token: str
    """

    token_type: Literal["bearer"] = "bearer"
    access_token: str
    refresh_token: str
