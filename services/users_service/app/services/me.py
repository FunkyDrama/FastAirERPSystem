import datetime as dt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from services.users_service.app.db.models.user import UserAccount
from services.users_service.app.db.models.passenger import Passenger
from services.users_service.app.db.models.booking import Booking
from services.users_service.app.db.models.flight_ref import FlightRef
from services.users_service.app.schemas.me import MeOut, PassengerOut
from services.users_service.app.schemas.booking import BookingShortOut, FlightBrief


class MeService:
    """
    Handles the management and retrieval of personal data and associated details for the currently
    authenticated user.

    This service includes functionality for retrieving a user's personal details, passenger records,
    upcoming and past bookings, and associated data. The purpose of this class is to serve as a
    facilitator between the data layer and higher-level application components, providing aggregated
    data in the required formats. Usage of this service is generally tailored for authenticated user
    scenarios.

    :param session: The asynchronous database session used to query and retrieve data.
    :type session: AsyncSession
    :param current_user: The authenticated user for whom data will be retrieved.
    :type current_user: UserAccount
    """

    def __init__(self, session: AsyncSession, current_user: UserAccount):
        self.session = session
        self.user = current_user

    async def get_me(self) -> MeOut:
        passengers = list(
            (
                await self.session.execute(
                    select(Passenger)
                    .where(Passenger.owner_id == self.user.user_id)
                    .order_by(Passenger.last_name, Passenger.first_name)
                )
            )
            .scalars()
            .all()
        )

        bookings = list(
            (
                await self.session.execute(
                    select(Booking)
                    .options(selectinload(Booking.tickets))
                    .where(Booking.user_id == self.user.user_id)
                    .order_by(Booking.booking_date.desc())
                )
            )
            .scalars()
            .all()
        )

        now = dt.datetime.now(dt.timezone.utc)
        upcoming: list[BookingShortOut] = []
        past: list[BookingShortOut] = []

        for b in bookings:
            first_ticket = b.tickets[0] if b.tickets else None
            if not first_ticket:
                continue
            f = (
                await self.session.execute(
                    select(FlightRef).where(
                        FlightRef.flight_id == first_ticket.flight_id
                    )
                )
            ).scalar_one_or_none()
            if not f:
                continue
            short = BookingShortOut(
                booking_id=b.booking_id,
                status=b.status.value,
                total_amount=b.total_amount,
                tickets_count=len(b.tickets),
                flight=self._brief(f),
            )
            if f.departure_time >= now:
                upcoming.append(short)
            else:
                past.append(short)

        return MeOut(
            email=self.user.email,
            balance=self.user.balance,
            passengers=[
                PassengerOut(
                    passenger_id=p.passenger_id,
                    first_name=p.first_name,
                    last_name=p.last_name,
                )
                for p in passengers
            ],
            upcoming=upcoming,
            past=past,
            now_utc=now,
        )

    @staticmethod
    def _brief(f: FlightRef) -> FlightBrief:
        return FlightBrief(
            flight_id=f.flight_id,
            flight_number=f.flight_number,
            origin=f.origin,
            destination=f.destination,
            departure_time=f.departure_time,
            arrival_time=f.arrival_time,
            status=f.status.value if hasattr(f.status, "value") else str(f.status),
        )
