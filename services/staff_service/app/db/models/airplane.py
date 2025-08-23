import uuid
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from services.staff_service.app.db.base import Base


class Airplane(Base):
    """
    Represents an airplane entity.

    This class defines the structure of an airplane, including its unique identifier,
    model information, total number of seats, and its relationship to flights.

    :ivar airplane_id: Unique identifier for the airplane.
    :type airplane_id: uuid.UUID
    :ivar model: Model name or type of the airplane.
    :type model: str
    :ivar total_seats: Total number of seats in the airplane.
    :type total_seats: int
    :ivar flights: List of flights associated with this airplane.
    :type flights: list[Flight]
    """

    __tablename__ = "airplanes"

    airplane_id: Mapped[uuid.UUID] = mapped_column(
        default=uuid.uuid4,
        primary_key=True,
    )
    model: Mapped[str] = mapped_column(String(255), nullable=False)
    total_seats: Mapped[int] = mapped_column(Integer, nullable=False)

    flights: Mapped[list["Flight"]] = relationship(
        "Flight",
        back_populates="airplane",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
