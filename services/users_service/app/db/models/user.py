import enum
import uuid
from decimal import Decimal

from sqlalchemy import String, Enum, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from services.users_service.app.db.base import Base


class Role(str, enum.Enum):
    """
    Represents various roles that can be assigned to entities, providing
    a set of predefined string values for easier role management and
    validation.

    This class serves as an enumeration of user roles in a system. It
    inherits both from `str` and `enum.Enum`, allowing it to function as
    a string while also being limited to the predefined set of values.
    """

    CUSTOMER = "customer"


class UserAccount(Base):
    """
    Represents a user account in the system.

    Provides the structure and information related to a user account, such as their email,
    hashed password, role, balance, and associations with bookings and passengers.

    :ivar user_id: Unique identifier for the user account.
    :type user_id: uuid.UUID
    :ivar email: Email address associated with the user account. Must be unique and not null.
    :type email: str
    :ivar password_hash: Hashed representation of the user's password. Must not be null.
    :type password_hash: str
    :ivar role: Role assigned to the user from the Role enumeration.
    :type role: Role
    :ivar balance: Monetary balance associated with the user account. Uses Decimal for precision.
    :type balance: Decimal
    :ivar bookings: List of bookings associated with the user account. Relationships are
        cascaded, and orphaned entities are deleted when the user account is deleted.
    :type bookings: list[Booking]
    :ivar passengers: List of passengers associated with the user account. Similar cascading
        deletion behavior as bookings.
    :type passengers: list[Passenger]
    """

    __tablename__ = "user_accounts"

    user_id: Mapped[uuid.UUID] = mapped_column(
        default=uuid.uuid4,
        primary_key=True,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Role] = mapped_column(
        Enum(Role, name="role_enum", native_enum=False),
        nullable=False,
        default=Role.CUSTOMER,
    )
    balance: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
    )
    bookings: Mapped[list["Booking"]] = relationship(
        "Booking",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    passengers: Mapped[list["Passenger"]] = relationship(
        "Passenger",
        back_populates="owner",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
