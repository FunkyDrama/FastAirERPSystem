import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.staff_service.app.db.models.flight import Flight, FlightStatus
from services.staff_service.app.db.models.ticket_shadow import (
    TicketStatus,
    TicketShadow,
)


class FlightRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def cancel_flight(self, flight_id: uuid.UUID):
        stmt = (
            select(Flight)
            .where(Flight.flight_id == flight_id)
            .where(Flight.status != FlightStatus.CANCELED)
        )
        res = await self.session.execute(stmt)
        flight = res.scalar_one_or_none()
        flight.status = FlightStatus.CANCELED
        await self.session.flush()

    async def get_all_flights(self) -> Sequence[Flight]:
        res = await self.session.execute(select(Flight))
        return res.scalars().all()

    async def get_flight_by_id(self, flight_id: uuid.UUID) -> Flight | None:
        res = await self.session.execute(
            select(Flight).where(Flight.flight_id == flight_id)
        )
        return res.scalar_one_or_none()

    async def get_passengers_on_flight(
        self,
        flight_id: str,
        status: TicketStatus | None = None,
    ) -> Sequence[TicketShadow]:
        stmt = select(TicketShadow).where(TicketShadow.flight_id == flight_id)
        if status:
            stmt = stmt.where(TicketShadow.status == status)

        res = await self.session.execute(stmt)
        return res.scalars().all()
