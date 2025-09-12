from decimal import Decimal

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from collections.abc import Sequence

from services.staff_service.app.db.models.ticket_shadow import (
    TicketShadow,
    TicketStatus,
)


SUCCESS_TICKETS_STATUSES = [
    TicketStatus.BOOKED,
    TicketStatus.CHECKED_IN,
    TicketStatus.BOARDED,
    TicketStatus.DONE,
]


class TicketRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_ticket_by_number(self, ticket_number: str) -> TicketShadow | None:
        res = await self.session.execute(
            select(TicketShadow).where(TicketShadow.ticket_number == ticket_number)
        )
        return res.scalar_one_or_none()

    async def update_ticket_status(
        self, ticket: TicketShadow, status: str
    ) -> TicketShadow:
        ticket.status = status
        await self.session.flush()
        return ticket

    async def get_all_tickets(self) -> Sequence[TicketShadow]:
        res = await self.session.execute(select(TicketShadow))
        return res.scalars().all()

    async def set_seat_number(
        self, ticket: TicketShadow, seat_number: str
    ) -> TicketShadow:
        if ticket.seat_number:
            raise ValueError(f"Seat {ticket.seat_number} already assigned")

        ticket.seat_number = seat_number
        await self.session.flush()
        return ticket

    async def get_total_revenue(self) -> Decimal:
        res = await self.session.execute(
            select(func.sum(TicketShadow.price)).where(
                TicketShadow.status.in_(SUCCESS_TICKETS_STATUSES)
            )
        )
        return res.scalar() or Decimal("0.00")

    async def get_revenue_by_flight(self, flight_id: str) -> Decimal:
        res = await self.session.execute(
            select(func.sum(TicketShadow.price)).where(
                TicketShadow.flight_id == flight_id,
                TicketShadow.status.in_(SUCCESS_TICKETS_STATUSES),
            )
        )
        return res.scalar() or Decimal("0.00")
