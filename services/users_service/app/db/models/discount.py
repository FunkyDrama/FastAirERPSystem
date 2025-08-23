from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from services.users_service.app.db.base import Base


class Discount(Base):
    """
    Represents a discount that can be applied to bookings.

    This class contains information about discounts, including the discount code,
    description, and the percentage of discount provided. It also includes the
    relationship with bookings that are associated with the discount.

    :ivar discount_code: The unique code identifying the discount.
    :type discount_code: str
    :ivar description: A brief description of the discount.
    :type description: str | None
    :ivar percent_off: The discount percentage to be applied.
    :type percent_off: int
    :ivar bookings: A list of bookings associated with this discount.
    :type bookings: list["Booking"]
    """

    __tablename__ = "discounts"

    discount_code: Mapped[str] = mapped_column(String(32), primary_key=True)
    description: Mapped[str | None] = mapped_column(String(255))
    percent_off: Mapped[int] = mapped_column(Integer, nullable=False)

    bookings: Mapped[list["Booking"]] = relationship(
        "Booking", back_populates="discount"
    )
