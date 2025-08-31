import enum
import uuid
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, func, String
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
    Represents a booking record in the system.

    The `Booking` class is responsible for maintaining booking information, including
    associated user, booking date, total amount, status, and relationships with other
    entities such as tickets, discounts, and payment details.

    :ivar booking_id: Unique identifier of the booking.
    :type booking_id: uuid.UUID
    :ivar booking_date: The date and time when the booking was created.
    :type booking_date: datetime.datetime
    :ivar total_amount: Total monetary amount for the booking.
    :type total_amount: Decimal
    :ivar status: Current status of the booking.
    :type status: BookingStatus
    :ivar user_id: Unique identifier of the user associated with the booking.
    :type user_id: uuid.UUID
    :ivar user: UserAccount instance related to the booking.
    :type user: UserAccount
    :ivar tickets: List of tickets associated with the booking.
    :type tickets: list[Ticket]
    :ivar discount_code: Discount code applied to the booking, if any.
    :type discount_code: str | None
    :ivar discount: Discount instance related to the booking.
    :type discount: Discount
    :ivar stripe_payment_intent_id: Stripe payment intent ID related to the booking, if any.
    :type stripe_payment_intent_id: str | None
    :ivar stripe_payment_status: Payment status for the booking in Stripe, if available.
    :type stripe_payment_status: str | None
    :ivar stripe_charge_id: Stripe charge ID linked to the payment for the booking, if any.
    :type stripe_charge_id: str | None
    :ivar stripe_refund_id: Stripe refund ID linked to the booking, if a refund exists.
    :type stripe_refund_id: str | None
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

    stripe_payment_intent_id: Mapped[str | None] = mapped_column(
        String(128), index=True, unique=True, nullable=True
    )
    stripe_payment_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    stripe_charge_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    stripe_refund_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
