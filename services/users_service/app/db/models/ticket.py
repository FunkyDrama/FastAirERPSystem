import enum
import uuid
from decimal import Decimal

from sqlalchemy import String, ForeignKey, Enum, Numeric, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from services.users_service.app.db.base import Base


class TicketStatus(str, enum.Enum):
    """
    Represents the status of a ticket as an enumeration.

    This enumeration is used to define and categorize the various possible states
    a ticket can be in during its lifecycle, such as booking, check-in, boarding, or
    after the process is complete. Each state is represented as a string value for
    easy comparison and handling.
    """

    BOOKED = "booked"
    CHECKED_IN = "checked_in"
    BOARDED = "boarded"
    CANCELED = "canceled"
    DONE = "done"


class Ticket(Base):
    """
    Represents a Ticket entity in the system.

    The Ticket class defines the structure of a ticket, including its attributes
    such as ticket number, seat number, status, price, and relationships with
    other entities like Booking, Passenger, FlightRef, and SeatType. This class
    is primarily used to associate passengers with bookings, flights, and seats
    while maintaining the status and options associated with each ticket. It
    supports operations for ticketing workflows within the corresponding system.

    :ivar ticket_number: Unique identifier for the ticket.
    :type ticket_number: str
    :ivar seat_number: Optional seat number assigned to the ticket, if available.
    :type seat_number: str | None
    :ivar status: Current status of the ticket, usually reflecting its booking state.
    :type status: TicketStatus
    :ivar price: Cost of the ticket.
    :type price: Decimal
    :ivar booking_id: ID of the associated booking.
    :type booking_id: uuid.UUID
    :ivar booking: Relationship to the Booking entity associated with the ticket.
    :type booking: Booking
    :ivar passenger_id: ID of the passenger who owns the ticket.
    :type passenger_id: uuid.UUID
    :ivar passenger: Relationship to the Passenger entity associated with the ticket.
    :type passenger: Passenger
    :ivar flight_id: ID of the associated flight.
    :type flight_id: uuid.UUID
    :ivar flight: Relationship to the FlightRef entity representing the specific flight.
    :type flight: FlightRef
    :ivar options: List of optional features or services tied to the ticket.
    :type options: list[Option]
    :ivar seat_type_name: Name of the seat type associated with the ticket.
    :type seat_type_name: str
    :ivar seat_type: Relationship to the SeatType entity representing the type of seat.
    :type seat_type: SeatType
    """

    __tablename__ = "tickets"

    ticket_number: Mapped[str] = mapped_column(String(32), primary_key=True)
    seat_number: Mapped[str | None] = mapped_column(String(10))
    status: Mapped[TicketStatus] = mapped_column(
        Enum(TicketStatus, name="ticket_status_enum", native_enum=False),
        nullable=False,
        default=TicketStatus.BOOKED,
    )
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    booking_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("bookings.booking_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    booking: Mapped["Booking"] = relationship("Booking", back_populates="tickets")

    passenger_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("passengers.passenger_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    passenger: Mapped["Passenger"] = relationship("Passenger", back_populates="tickets")
    flight_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("flights_ref.flight_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    flight: Mapped["FlightRef"] = relationship("FlightRef", back_populates="tickets")

    options: Mapped[list["Option"]] = relationship(
        "Option",
        secondary="ticket_options",
        back_populates="tickets",
    )

    seat_type_name: Mapped[str] = mapped_column(
        ForeignKey("seat_types.type_name", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    seat_type: Mapped["SeatType"] = relationship("SeatType", back_populates="tickets")

    __table_args__ = (
        Index("ix_ticket_booking", "booking_id"),
        Index("ix_ticket_passenger", "passenger_id"),
        Index("ix_ticket_flight", "flight_id"),
    )
