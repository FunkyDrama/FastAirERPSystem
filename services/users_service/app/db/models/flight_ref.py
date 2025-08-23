import enum
import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Enum, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from services.users_service.app.db.base import Base


class FlightStatus(str, enum.Enum):
    """
    Enum representing the various statuses a flight can have.

    This class contains the possible states indicating the current
    status of flights, such as scheduled, canceled, or completed.
    Designed to simplify flight status management within systems
    that handle flight-related operations.
    """

    SCHEDULED = "scheduled"
    CANCELED = "canceled"
    COMPLETED = "completed"


class FlightRef(Base):
    """
    Represents a reference to a flight.

    The FlightRef class is utilized to model flight information, including details such
    as flight number, origin, destination, departure and arrival times, status, and
    associated tickets. It is designed to manage flight scheduling and tracking while
    enforcing constraints such as uniqueness of flight number and departure time.

    :ivar flight_id: Unique identifier for the flight.
    :type flight_id: uuid.UUID
    :ivar flight_number: Flight number associated with the flight.
    :type flight_number: str
    :ivar origin: Airport code or city name representing the flight's origin.
    :type origin: str
    :ivar destination: Airport code or city name representing the flight's destination.
    :type destination: str
    :ivar departure_time: Scheduled departure time of the flight.
    :type departure_time: datetime
    :ivar arrival_time: Scheduled arrival time of the flight.
    :type arrival_time: datetime
    :ivar status: Status of the flight (e.g., scheduled, delayed).
    :type status: FlightStatus
    :ivar tickets: List of tickets associated with the flight.
    :type tickets: list[Ticket]
    """

    __tablename__ = "flights_ref"

    flight_id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    flight_number: Mapped[str] = mapped_column(String(16), index=True, nullable=False)
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
    tickets: Mapped[list["Ticket"]] = relationship("Ticket", back_populates="flight")

    __table_args__ = (
        UniqueConstraint(
            "flight_number", "departure_time", name="uq_flightref_number_departure"
        ),
        Index("ix_flightref_o_d_dt", "origin", "destination", "departure_time"),
    )
