import enum
import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Enum, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from services.staff_service.app.db.base import Base


class FlightStatus(str, enum.Enum):
    """
    Represents the status of a flight.

    This enumeration is used to define and manage the various states
    that a flight can have during its lifecycle, ensuring standardized
    status representation across the system.

    :cvar SCHEDULED: The flight is scheduled and yet to be completed or canceled.
    :cvar CANCELED: The flight has been canceled and will not take place.
    :cvar COMPLETED: The flight has been completed successfully.
    """

    SCHEDULED = "scheduled"
    CANCELED = "canceled"
    COMPLETED = "completed"


class Flight(Base):
    """
    Represents a flight entity, storing key details about a flight, including its
    schedule, status, origin, destination, and associated airplane.

    This class is designed to model flights in a relational database using SQLAlchemy.
    Each flight instance includes scheduling details such as departure and arrival times,
    as well as the status of the flight and its association to a specific airplane.
    The class also manages relationships to tickets shadowing the flight.

    :ivar flight_id: Unique identifier for the flight.
    :type flight_id: uuid.UUID
    :ivar flight_number: The flight number that uniquely identifies the flight for travelers.
    :type flight_number: str
    :ivar origin: The origin location's name or code of the flight.
    :type origin: str
    :ivar destination: The destination location's name or code of the flight.
    :type destination: str
    :ivar departure_time: The date and time when the flight is scheduled to depart.
    :type departure_time: datetime.datetime
    :ivar arrival_time: The date and time when the flight is scheduled to arrive.
    :type arrival_time: datetime.datetime
    :ivar status: Current status of the flight (e.g., Scheduled, In Progress, Completed).
    :type status: FlightStatus
    :ivar airplane_id: The identifier of the airplane assigned to the flight.
    :type airplane_id: uuid.UUID
    :ivar airplane: The Airplane entity related to this flight.
    :type airplane: Airplane
    :ivar tickets_shadow: The list of TicketShadow instances related to the flight.
    :type tickets_shadow: list[TicketShadow]
    """

    __tablename__ = "flights"

    flight_id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4, primary_key=True)
    flight_number: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    origin: Mapped[str] = mapped_column(String(64), nullable=False)
    destination: Mapped[str] = mapped_column(String(64), nullable=False)
    departure_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    arrival_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    status: Mapped[FlightStatus] = mapped_column(
        Enum(FlightStatus, name="flight_status_enum", native_enum=False),
        nullable=False,
        default=FlightStatus.SCHEDULED,
    )
    airplane_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("airplanes.airplane_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    airplane: Mapped["Airplane"] = relationship("Airplane", back_populates="flights")
    tickets_shadow: Mapped[list["TicketShadow"]] = relationship(
        "TicketShadow",
        back_populates="flight",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
        Index(
            "uq_flight_number_departure", "flight_number", "departure_time", unique=True
        ),
    )
