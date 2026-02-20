import uuid
from collections.abc import Sequence
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from services.staff_service.app.db.models.flight import Flight, FlightStatus
from services.staff_service.app.db.models.ticket_shadow import (
    TicketStatus,
    TicketShadow,
)


class FlightRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self) -> None:
        await self.session.commit()

    async def create_flight(self, flight: Flight) -> Flight:
        self.session.add(flight)
        await self.session.flush()
        return flight

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

    async def complete_overdue_flights(self) -> list[uuid.UUID]:
        """Mark scheduled flights whose departure time has passed as COMPLETED.

        Returns list of flight_ids that were updated.
        """
        now = datetime.now(timezone.utc)
        id_stmt = (
            select(Flight.flight_id)
            .where(Flight.status == FlightStatus.SCHEDULED)
            .where(Flight.departure_time < now)
        )
        res = await self.session.execute(id_stmt)
        flight_ids = list(res.scalars().all())
        if flight_ids:
            upd_stmt = (
                update(Flight)
                .where(Flight.flight_id.in_(flight_ids))
                .values(status=FlightStatus.COMPLETED)
            )
            await self.session.execute(upd_stmt)
            await self.session.flush()
        return flight_ids

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

    async def assign_seat_number(self, flight_id: uuid.UUID) -> str:
        result = await self.session.execute(
            select(TicketShadow.seat_number)
            .where(TicketShadow.flight_id == flight_id)
            .where(TicketShadow.seat_number.isnot(None))
        )
        occupied_seats = {row[0] for row in result}

        for row in range(1, 31):
            for seat_letter in ["A", "B", "C", "D", "E", "F"]:
                seat = f"{row}{seat_letter}"
                if seat not in occupied_seats:
                    return seat
        raise ValueError("No available seats")
