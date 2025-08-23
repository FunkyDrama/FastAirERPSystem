import uuid
from decimal import Decimal

from sqlalchemy import (
    String,
    Numeric,
    ForeignKey,
    Table,
    Column,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from services.users_service.app.db.base import Base


ticket_options = Table(
    "ticket_options",
    Base.metadata,
    Column(
        "ticket_number",
        ForeignKey("tickets.ticket_number", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "option_id",
        ForeignKey("options.option_id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column("qty", Integer, nullable=False, server_default="1"),
    Column("price_override", Numeric(12, 2)),
    UniqueConstraint("ticket_number", "option_id", name="uq_ticket_option"),
)


class Option(Base):
    """
    Represents an Option entity in the database.

    The class models an option with a unique ID, name, price, and its relationship
    to tickets. It enables the persistence of such options and their connections
    to tickets in a relational database, allowing for functionality like querying,
    updating, and maintaining data integrity.

    :ivar option_id: Unique identifier for the option.
    :type option_id: uuid.UUID
    :ivar name: Name of the option with a maximum of 100 characters. Must be
        unique and cannot be null.
    :type name: str
    :ivar price: Monetary value associated with the option. Stored as a decimal
        value with up to 12 digits and 2 decimal places. Cannot be null.
    :type price: Decimal
    :ivar tickets: A list of tickets associated with this option. Represents a
        many-to-many relationship between options and tickets.
    :type tickets: list[Ticket]
    """

    __tablename__ = "options"

    option_id: Mapped[uuid.UUID] = mapped_column(default=uuid.uuid4, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    tickets: Mapped[list["Ticket"]] = relationship(
        "Ticket",
        secondary=ticket_options,
        back_populates="options",
    )
