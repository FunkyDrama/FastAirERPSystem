import uuid
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from services.users_service.app.db.base import Base


class Passenger(Base):
    """
    Represents a passenger in the system.

    This class models a passenger including their personal details, contact information,
    and relationships to other entities such as the user who owns this passenger record
    and tickets associated with them. It is mapped to the `passengers` table in the
    database.

    :ivar passenger_id: Unique identifier for the passenger.
    :type passenger_id: uuid.UUID
    :ivar first_name: The first name of the passenger.
    :type first_name: str
    :ivar last_name: The last name of the passenger.
    :type last_name: str
    :ivar contact_info: Contact details of the passenger (optional).
    :type contact_info: str or None
    :ivar owner_id: Foreign key referencing the user who owns the passenger record
        (optional). Defaults to NULL if the owner is removed.
    :type owner_id: uuid.UUID or None
    :ivar owner: Relationship to the user account that owns this passenger record.
    :type owner: UserAccount
    :ivar tickets: List of tickets associated with the passenger.
    :type tickets: list[Ticket]
    """

    __tablename__ = "passengers"

    passenger_id: Mapped[uuid.UUID] = mapped_column(
        default=uuid.uuid4, primary_key=True
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    contact_info: Mapped[str | None] = mapped_column(String(255))
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("user_accounts.user_id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    owner: Mapped["UserAccount"] = relationship(
        "UserAccount", back_populates="passengers"
    )
    tickets: Mapped[list["Ticket"]] = relationship("Ticket", back_populates="passenger")
