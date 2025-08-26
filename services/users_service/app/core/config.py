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
    REDIS_PREFIX: str = "auth"

    model_config = SettingsConfigDict(env_file=ROOT_DIR / ".env", extra="ignore")


redis_settings = RedisSettings()

jwt_settings = Settings()
