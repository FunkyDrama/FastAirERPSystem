import datetime as dt
import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.users_service.app.db.models.flight_ref import FlightRef, FlightStatus


class FlightRepository:
    """
    Handles operations related to flight data within the database.

    This class provides methods to interact with flight information stored in a database.
    It allows saving changes, retrieving flight details by ID, retrieving all flights,
    creating new flight records, searching for flights based on various criteria, deleting
    a flight record, and updating the details of an existing flight. All operations are
    performed asynchronously.

    :ivar session: The asynchronous database session used for executing queries and managing
                   transactional operations.
    :type session: AsyncSession
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self) -> None:
        await self.session.commit()

    async def get_flight_by_id(self, flight_id: uuid.UUID) -> FlightRef | None:
        res = await self.session.execute(
            select(FlightRef).where(FlightRef.flight_id == flight_id)
        )
        return res.scalar_one_or_none()

    async def get_all_flights(self) -> Sequence[FlightRef]:
        res = await self.session.execute(select(FlightRef))
        return res.scalars().all()

    async def create_flight(self, flight_data: dict) -> FlightRef:
        flight = FlightRef(**flight_data)
        self.session.add(flight)
        await self.session.flush()
        return flight

    async def search(
        self,
        *,
        origin: str | None = None,
        destination: str | None = None,
        date: dt.date | None = None,
        passengers: int = 1,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[FlightRef]:
        now = dt.datetime.now(tz=dt.timezone.utc)
        stmt = (
            select(FlightRef)
            .where(FlightRef.status == FlightStatus.SCHEDULED)
            .where(FlightRef.departure_time > now)
        )

        if origin:
            stmt = stmt.where(FlightRef.origin.ilike(origin))
        if destination:
            stmt = stmt.where(FlightRef.destination.ilike(destination))
        if date:
            day_start = dt.datetime.combine(date, dt.time.min).astimezone(
                dt.timezone.utc
            )
            day_end = dt.datetime.combine(date, dt.time.max).astimezone(dt.timezone.utc)
            stmt = stmt.where(
                FlightRef.departure_time >= day_start,
                FlightRef.departure_time <= day_end,
            )
        stmt = stmt.order_by(FlightRef.departure_time).limit(limit).offset(offset)
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def delete_flight(self, flight: FlightRef) -> None:
        await self.session.delete(flight)

    async def update_flight(self, flight: FlightRef, flight_data: dict) -> FlightRef:
        for key, value in flight_data.items():
            setattr(flight, key, value)
        await self.session.flush()
        return flight
