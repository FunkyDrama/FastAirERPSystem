import enum
import uuid
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from services.users_service.app.db.base import Base


class BookingStatus(str, enum.Enum):
    """
    Represents the statuses a booking can have during its lifecycle.

    Provides meaningful labels such as RESERVED, PAID, CANCELED, and REFUNDED
    to describe the state of a booking. These values could be used to manage
    and streamline workflows, reporting, or status-checking processes.
    """

    RESERVED = "reserved"
    PAID = "paid"
    CANCELED = "canceled"
    REFUNDED = "refunded"


class Booking(Base):
    """
    Represents a booking entity in the booking system.

    This class is used to manage and store information related to bookings,
    including booking details such as the booking date, total amount, status,
    associated user, tickets, and potential discount codes applied.

    :ivar booking_id: Unique identifier for the booking instance.
    :type booking_id: uuid.UUID
    :ivar booking_date: Date and time when the booking was created.
    :type booking_date: datetime.datetime
    :ivar total_amount: Total amount of the booking in fixed decimal format.
    :type total_amount: Decimal
    :ivar status: Status of the booking, e.g., reserved, completed, or cancelled.
    :type status: BookingStatus
    :ivar user_id: Identifier of the user associated with the booking.
    :type user_id: uuid.UUID
    :ivar user: User object representing the account of the user associated
        with the booking.
    :type user: UserAccount
    :ivar tickets: List of tickets associated with the booking.
    :type tickets: list[Ticket]
    :ivar discount_code: Discount code applied to the booking, if any.
    :type discount_code: str or None
    :ivar discount: Discount object associated with the booking, if any.
    :type discount: Discount
    """

    __tablename__ = "bookings"

    booking_id: Mapped[uuid.UUID] = mapped_column(
        default=uuid.uuid4,
        primary_key=True,
    )
    booking_date: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )
    status: Mapped[BookingStatus] = mapped_column(
        Enum(BookingStatus, name="booking_status_enum", native_enum=False),
        nullable=False,
        default=BookingStatus.RESERVED,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user_accounts.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user: Mapped["UserAccount"] = relationship(
        "UserAccount",
        back_populates="bookings",
    )
    tickets: Mapped[list["Ticket"]] = relationship(
        "Ticket",
        back_populates="booking",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    discount_code: Mapped[str | None] = mapped_column(
        ForeignKey("discounts.discount_code"),
        nullable=True,
        index=True,
    )
    discount: Mapped["Discount"] = relationship("Discount", back_populates="bookings")
