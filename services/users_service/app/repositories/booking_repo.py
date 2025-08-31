from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from services.users_service.app.db.models.booking import Booking, BookingStatus
from services.users_service.app.db.models.flight_ref import FlightRef
from services.users_service.app.db.models.passenger import Passenger
from services.users_service.app.db.models.ticket import Ticket


class BookingRepository:
    """
    Handles database interactions for managing bookings, passengers, flights, and tickets.

    This class encapsulates methods to perform database operations such as creating
    and retrieving bookings, passengers, flights, and tickets. It relies on an asynchronous
    database session to interact with the database.

    :ivar session: The asynchronous database session used for executing queries.
    :type session: AsyncSession
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self) -> None:
        await self.session.commit()

    async def get_flight(self, flight_id: UUID) -> FlightRef | None:
        res = await self.session.execute(
            select(FlightRef).where(FlightRef.flight_id == flight_id)
        )
        return res.scalar_one_or_none()

    async def get_passenger(self, pid: UUID) -> Passenger | None:
        res = await self.session.execute(
            select(Passenger).where(Passenger.passenger_id == pid)
        )
        return res.scalar_one_or_none()

    async def create_passenger(
        self,
        *,
        owner_id: UUID,
        first_name: str,
        last_name: str,
        contact_info: str | None,
    ) -> Passenger:
        p = Passenger(
            owner_id=owner_id,
            first_name=first_name,
            last_name=last_name,
            contact_info=contact_info,
        )
        self.session.add(p)
        await self.session.flush()
        return p

    async def create_booking(
        self, *, user_id: UUID, total_amount, discount_code: str | None
    ) -> Booking:
        b = Booking(
            user_id=user_id,
            total_amount=total_amount,
            status=BookingStatus.RESERVED,
            discount_code=discount_code,
        )
        self.session.add(b)
        await self.session.flush()
        return b

    async def get_booking_for_owner(self, booking_id, owner_id):
        stmt = (
            select(Booking)
            .where(Booking.booking_id == booking_id, Booking.user_id == owner_id)
            .options(selectinload(Booking.tickets).selectinload(Ticket.flight))
        )
        res = await self.session.execute(stmt)
        return res.scalars().unique().one_or_none()

    async def list_bookings_for_owner(
        self, owner_id, *, limit: int = 50, offset: int = 0
    ):
        stmt = (
            select(Booking)
            .where(Booking.user_id == owner_id)
            .order_by(Booking.booking_date.desc())
            .limit(limit)
            .offset(offset)
            .options(selectinload(Booking.tickets).selectinload(Ticket.flight))
        )
        res = await self.session.execute(stmt)
        items = res.scalars().unique().all()

        total_stmt = select(func.count()).select_from(
            select(Booking.booking_id).where(Booking.user_id == owner_id).subquery()
        )
        total = (await self.session.execute(total_stmt)).scalar_one()

        return items, total

    async def create_ticket(self, ticket: Ticket) -> Ticket:
        self.session.add(ticket)
        await self.session.flush()
        return ticket

    async def get_booking_by_id(self, booking_id: UUID) -> Booking | None:
        res = await self.session.execute(
            select(Booking).where(Booking.booking_id == booking_id)
        )
        return res.scalar_one_or_none()

    async def get_booking_by_payment_intent(self, intent_id: str) -> Booking | None:
        stmt = (
            select(Booking)
            .where(Booking.stripe_payment_intent_id == intent_id)
            .options(
                selectinload(Booking.tickets).selectinload(Ticket.flight),
                joinedload(Booking.user),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalars().unique().one_or_none()

    async def load_booking_with_user_and_tickets(
        self, booking_id: UUID, owner_id: UUID
    ) -> Booking | None:
        stmt = (
            select(Booking)
            .where(Booking.booking_id == booking_id, Booking.user_id == owner_id)
            .options(
                selectinload(Booking.tickets).selectinload(Ticket.flight),
                joinedload(Booking.user),
            )
        )
        res = await self.session.execute(stmt)
        return res.scalars().unique().one_or_none()
