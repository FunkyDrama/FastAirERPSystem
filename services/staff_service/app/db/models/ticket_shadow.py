import enum
from sqlalchemy import String, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from services.staff_service.app.db.base import Base


class TicketStatus(str, enum.Enum):
    """
    Represents the status of a ticket.

    This class is an enumeration of possible states that a ticket can have during
    its lifecycle. It provides a set of predefined constants representing these
    statuses, which can be used to track and manage ticket states effectively.

    :ivar BOOKED: Indicates that the ticket has been booked.
    :type BOOKED: str
    :ivar CHECKED_IN: Indicates that the ticket holder has checked in.
    :type CHECKED_IN: str
    :ivar BOARDED: Indicates that the ticket holder has boarded.
    :type BOARDED: str
    :ivar CANCELED: Indicates that the ticket has been canceled.
    :type CANCELED: str
    :ivar DONE: Indicates that the ticketing process is completed.
    :type DONE: str
    """

    BOOKED = "booked"
    CHECKED_IN = "checked_in"
    BOARDED = "boarded"
    CANCELED = "canceled"
    DONE = "done"


class TicketShadow(Base):
    """
    Represents a shadow ticket model used to manage ticket data and their relationships
    with other entities in the system.

    The class defines the attributes of a shadow ticket, including its number,
    passenger information, seat details, status, and associated flight. It is designed
    to integrate with a database table and establish relationships with other tables.

    :ivar ticket_number: The unique identifier for the ticket.
    :type ticket_number: str
    :ivar passenger_name: The name of the passenger who owns the ticket.
    :type passenger_name: str
    :ivar seat_number: The seat number assigned to the ticket. It may be None if
        the seat is not assigned.
    :type seat_number: str | None
    :ivar seat_type: The type of the seat (e.g., economy, business).
    :type seat_type: str
    :ivar status: The current status of the ticket (e.g., booked, cancelled).
    :type status: TicketStatus
    :ivar flight_id: The unique identifier of the flight associated with this ticket.
    :type flight_id: uuid.UUID
    :ivar flight: The flight object associated with this ticket.
    :type flight: Flight
    """

    __tablename__ = "ticket_shadows"

    ticket_number: Mapped[str] = mapped_column(String(32), primary_key=True)
    passenger_name: Mapped[str] = mapped_column(String(255), nullable=False)
    seat_number: Mapped[str | None] = mapped_column(String(10))
    seat_type: Mapped[str] = mapped_column(String(32), nullable=False)

    status: Mapped[TicketStatus] = mapped_column(
        Enum(TicketStatus, name="ticket_status_enum", native_enum=False),
        nullable=False,
        default=TicketStatus.BOOKED,
    )

    flight_id: Mapped["uuid.UUID"] = mapped_column(
        ForeignKey("flights.flight_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    flight: Mapped["Flight"] = relationship("Flight", back_populates="tickets_shadow")
