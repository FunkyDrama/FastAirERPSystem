from decimal import Decimal
from sqlalchemy import String, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from services.users_service.app.db.base import Base


class SeatType(Base):
    """
    Representation of a Seat Type in the system.

    This class defines the structure and properties of a seat type in the system,
    including its name, description, and pricing multiplier. It also establishes
    the relationship between seat types and tickets. Each seat type is identified
    by its unique name.

    :ivar type_name: The unique name of the seat type.
    :type type_name: str
    :ivar description: A textual description of the seat type. Optional.
    :type description: str | None
    :ivar multiplier: The pricing multiplier associated with the seat type. This
        value is used to adjust the base ticket price according to the seat type.
    :type multiplier: Decimal
    :ivar tickets: A list of tickets that are associated with this seat type.
    :type tickets: list[Ticket]
    """

    __tablename__ = "seat_types"

    type_name: Mapped[str] = mapped_column(String(32), primary_key=True)
    description: Mapped[str | None] = mapped_column(String(255))
    multiplier: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), nullable=False, server_default="1.00"
    )
    tickets: Mapped[list["Ticket"]] = relationship("Ticket", back_populates="seat_type")
