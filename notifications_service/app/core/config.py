from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parent.parent.parent


class EmailSettings(BaseSettings):
    """
    Configuration class for email settings.

    This class defines the configuration for email services, allowing you to
    specify details such as the email host, port, authentication details, and
    whether TLS should be used. The purpose is to provide a structured way of
    managing email-related settings.

    :ivar EMAIL_HOST: The SMTP host address for the email service.
    :type EMAIL_HOST: str
    :ivar EMAIL_HOST_USER: The username for authenticating with the email host.
    :type EMAIL_HOST_USER: str
    :ivar EMAIL_HOST_PASSWORD: The password for authenticating with the email host.
    :type EMAIL_HOST_PASSWORD: str
    :ivar EMAIL_PORT: The port number used for connecting to the email host.
    :type EMAIL_PORT: int
    :ivar EMAIL_USE_TLS: Indicates whether TLS encryption is used.
    :type EMAIL_USE_TLS: bool
    :ivar EMAIL_FROM: The default sender email address.
    :type EMAIL_FROM: str
    """

    EMAIL_HOST: str = "smtp.gmail.com"
    EMAIL_HOST_USER: str
    EMAIL_HOST_PASSWORD: str
    EMAIL_PORT: int = 587
    EMAIL_USE_TLS: bool = True
    EMAIL_FROM: str

    model_config = SettingsConfigDict(env_file=ROOT_DIR / ".env", extra="ignore")


email_settings = EmailSettings()
