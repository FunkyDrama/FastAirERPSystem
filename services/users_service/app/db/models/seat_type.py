from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from services.users_service.app.db.base import Base


class SeatType(Base):
    """
    Represents a type of seat with its attributes and relationships, used for managing
    seat specifications and related ticketing information.

    This class defines the attributes for seat types, including a unique identifier,
    description, and a relationship to associated tickets.

    :ivar type_name: Unique name for the seat type, used as the primary key.
    :type type_name: str
    :ivar description: Description of the seat type, providing additional
        details. Can be None if not provided.
    :type description: str or None
    :ivar tickets: List of tickets associated with the seat type, conveying
        relationships between seat types and tickets.
    :type tickets: list["Ticket"]
    """

    __tablename__ = "seat_types"

    type_name: Mapped[str] = mapped_column(String(32), primary_key=True)
    description: Mapped[str | None] = mapped_column(String(255))
    tickets: Mapped[list["Ticket"]] = relationship("Ticket", back_populates="seat_type")
