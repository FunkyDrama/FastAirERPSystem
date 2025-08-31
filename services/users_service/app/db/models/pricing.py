from decimal import Decimal
from sqlalchemy import Numeric, String
from sqlalchemy.orm import Mapped, mapped_column
from services.users_service.app.db.base import Base


class PricingConfig(Base):
    """
    Represents the configuration for pricing, including base price and currency.

    The PricingConfig class is a model used to define and manage the pricing
    configuration. This includes attributes for storing the base price and its
    associated currency. The class is designed to be used in database operations,
    allowing effective and efficient management of pricing configurations.

    :ivar id: The unique identifier for the pricing configuration.
    :type id: int
    :ivar base_price: The base price associated with the pricing configuration.
    :type base_price: Decimal
    :ivar currency: The currency code (ISO 4217) for the base price.
    :type currency: str
    """

    __tablename__ = "pricing_config"

    id: Mapped[int] = mapped_column(primary_key=True, default=1)
    base_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
