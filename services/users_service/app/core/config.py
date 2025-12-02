from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

ROOT_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """
    Handles application settings and configuration management.

    This class is responsible for defining and managing the settings
    required for secure and efficient operation of the application.
    It provides mechanisms for environment variable configuration
    and defines default values for various operational parameters.

    :ivar JWT_SECRET: A secret key used for signing and verifying JWT tokens.
    :type JWT_SECRET: SecretStr
    :ivar JWT_ALG: The algorithm used for token signing and verification. Default: "HS256".
    :type JWT_ALG: str
    :ivar ACCESS_TTL_SECONDS: The time-to-live for access tokens in seconds. Default: 900 (15 minutes).
    :type ACCESS_TTL_SECONDS: int
    :ivar REFRESH_TTL_SECONDS: The time-to-live for refresh tokens in seconds. Default: 604800 (7 days).
    :type REFRESH_TTL_SECONDS: int
    """

    JWT_SECRET: SecretStr
    JWT_ALG: str = "HS256"
    ACCESS_TTL_SECONDS: int = 900
    REFRESH_TTL_SECONDS: int = 60 * 60 * 24 * 7

    model_config = SettingsConfigDict(env_file=ROOT_DIR / ".env", extra="ignore")


class RedisSettings(BaseSettings):
    """
    Handles settings configuration for Redis.

    This class is used to define and manage Redis connection configuration and
    related settings. It extends from BaseSettings to utilize pydantic's
    settings management capabilities.

    :ivar REDIS_URL: The URL for the Redis server connection.
    :type REDIS_URL: str
    :ivar REDIS_PREFIX: The prefix used for all Redis keys.
    :type REDIS_PREFIX: str
    """

    REDIS_URL: str = "redis://redis:6379/0"
    REDIS_PREFIX: str = "users_auth"

    model_config = SettingsConfigDict(env_file=ROOT_DIR / ".env", extra="ignore")


class StripeSettings(BaseSettings):
    """
    Handles configuration for Stripe API integration.

    This class encapsulates all the necessary settings required for communicating
    with the Stripe API. It is designed to handle sensitive information such as
    keys and secrets, and loads configuration from environment variables or an
    environment file. The primary purpose of this class is to provide a structured
    and secure way to manage Stripe-related settings within the application.

    :ivar STRIPE_PUBLISHABLE_KEY: The publishable key provided by Stripe for
        identifying the merchant's account publicly.
    :type STRIPE_PUBLISHABLE_KEY: str
    :ivar STRIPE_SECRET_KEY: The secret key provided by Stripe for server-side
        authentication and operations.
    :type STRIPE_SECRET_KEY: SecretStr
    :ivar STRIPE_WEBHOOK_SECRET: The secret used by Stripe to verify webhook
        payloads sent to your server.
    :type STRIPE_WEBHOOK_SECRET: SecretStr
    :ivar STRIPE_API_VERSION: Specifies the version of Stripe's API this application
        is intended to use. Defaults to "2022-08-01".
    :type STRIPE_API_VERSION: str
    """

    STRIPE_PUBLISHABLE_KEY: str
    STRIPE_SECRET_KEY: SecretStr
    STRIPE_WEBHOOK_SECRET: SecretStr
    STRIPE_API_VERSION: str = "2022-08-01"

    model_config = SettingsConfigDict(env_file=ROOT_DIR / ".env", extra="ignore")


class GoogleAuthSettings(BaseSettings):
    """
    Handles settings configuration for Google OAuth2 authentication.

    This class is used to define and manage Google OAuth2 authentication
    settings. It extends from BaseSettings to utilize pydantic's
    settings management capabilities.

    :ivar GOOGLE_CLIENT_ID: The client ID provided by Google for OAuth2 authentication.
    :type GOOGLE_CLIENT_ID: str
    :ivar GOOGLE_CLIENT_SECRET: The client secret provided by Google for OAuth2 authentication.
    :type GOOGLE_CLIENT_SECRET: SecretStr
    :ivar GOOGLE_REDIRECT_URI: The redirect URI provided by Google for OAuth2 authentication.
    :type GOOGLE_REDIRECT_URI: str
    """

    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: SecretStr
    GOOGLE_REDIRECT_URI: str
    FRONTEND_URL: str

    model_config = SettingsConfigDict(env_file=ROOT_DIR / ".env", extra="ignore")


stripe_settings = StripeSettings()
redis_settings = RedisSettings()
jwt_settings = Settings()
google_auth_settings = GoogleAuthSettings()
