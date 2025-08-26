import re
from typing import Literal
from pydantic import BaseModel, EmailStr, Field, field_validator


class UserRegistration(BaseModel):
    """
    Represents a user registration model.

    This class is used to model the data needed for user registration. It includes
    validation for a secure password and optional user details like `first_name`
    and `last_name`.

    :ivar email: The email address of the user.
    :type email: EmailStr
    :ivar password: The user's password, which must meet specific security
        requirements, including length and character criteria.
    :type password: str
    """

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=24)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8 or len(v) > 24:
            raise ValueError("Password must be between 8 and 24 characters")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        special_chars = r"[!#$%&*+\-/=?^_`{|}~]"
        if not re.search(special_chars, v):
            raise ValueError(
                "Password must contain at least one special character (!#$%&*+-/=?^_`{|}~)"
            )
        forbidden_chars = r'[@"\'<>]'
        if re.search(forbidden_chars, v):
            raise ValueError("Password cannot contain @, \", ', <, > characters")
        return v


class UserLogin(BaseModel):
    """
    Represents a user login model.

    This class is used for validating and handling user login information. It ensures
    that the email address provided follows the proper format and that a password is
    provided as a string. It can be utilized in scenarios where user authentication
    is required.

    :ivar email: The email address of the user. Must follow a valid email format.
    :type email: EmailStr
    :ivar password: The password of the user.
    :type password: str
    """

    email: EmailStr
    password: str


class LogoutIn(BaseModel):
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


class PasswordChange(BaseModel):
    """
    Represents a model for changing passwords.

    This class is used to handle password change requests, including validation
    of the new password to ensure compliance with specific security requirements.

    :ivar current_password: The user's current password.
    :type current_password: str
    :ivar new_password: The new password that the user wants to set. This password
        must meet the required criteria, including length, character types,
        and restrictions on forbidden characters.
    :type new_password: str
    """

    current_password: str
    new_password: str = Field(..., min_length=8, max_length=24)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        if len(v) < 8 or len(v) > 24:
            raise ValueError("Password must be between 8 and 24 characters")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        special_chars = r"[!#$%&*+\-/=?^_`{|}~]"
        if not re.search(special_chars, v):
            raise ValueError(
                "Password must contain at least one special character (!#$%&*+-/=?^_`{|}~)"
            )
        forbidden_chars = r'[@"\'<>]'
        if re.search(forbidden_chars, v):
            raise ValueError("Password cannot contain @, \", ', <, > characters")
        return v


class UserResponse(BaseModel):
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
