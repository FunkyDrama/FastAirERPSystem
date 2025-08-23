"""Settings for the database connection."""

from pathlib import Path

from pydantic import SecretStr, PrivateAttr
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """
    Settings management for database connections and configuration.

    This class provides attributes for configuring PostgreSQL database connection
    db_settings, including secure handling of sensitive information such as database
    user credentials. It ensures proper management of environment variables and
    allows for overriding the generated database URL.

    :ivar POSTGRES_USER: The username for the PostgreSQL database.
    :type POSTGRES_USER: SecretStr
    :ivar POSTGRES_PASSWORD: The password for the PostgreSQL database.
    :type POSTGRES_PASSWORD: SecretStr
    :ivar POSTGRES_DB: The name of the PostgreSQL database.
    :type POSTGRES_DB: str
    :ivar POSTGRES_HOST: The hostname for the PostgreSQL database, defaulting to "db".
    :type POSTGRES_HOST: str
    :ivar POSTGRES_PORT: The port number for the PostgreSQL database, defaulting to 5432.
    :type POSTGRES_PORT: int
    """

    POSTGRES_USER: SecretStr
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_DB: str
    POSTGRES_HOST: str = "users_db"
    POSTGRES_PORT: int = 5432

    model_config = SettingsConfigDict(env_file=ROOT_DIR / ".env", extra="ignore")
    _db_url_override: str | None = PrivateAttr(default=None)

    @property
    def DATABASE_URL(self) -> str:
        if self._db_url_override:
            return self._db_url_override
        return (
            "postgresql+asyncpg://"
            f"{self.POSTGRES_USER.get_secret_value()}:"
            f"{self.POSTGRES_PASSWORD.get_secret_value()}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/"
            f"{self.POSTGRES_DB}"
        )

    @DATABASE_URL.setter
    def DATABASE_URL(self, value: str) -> None:
        self._db_url_override = value


db_settings = Settings()
