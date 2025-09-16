from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from services.staff_service.app.db.models.ticket_shadow import TicketStatus
from services.staff_service.app.messaging.task_manager import StaffTaskManager
from services.staff_service.app.repositories.ticket_repo import TicketRepository
from services.staff_service.app.schemas.ticket import (
    UpdateTicketStatus,
    PassengersOnFlight,
    PassengerOnFlight,
)


class GateManagerService:

    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession]):
        self._sm = sessionmaker
        self.tm = StaffTaskManager()

    async def registry_ticket_boarding(self, ticket_number: str):
        async with self._sm() as session:
            repo = TicketRepository(session)
            ticket = await repo.get_ticket_by_number(ticket_number)
            if not ticket:
                raise ValueError(f"Ticket with number {ticket_number} not found")
            if ticket.status != TicketStatus.CHECKED_IN:
                raise ValueError(
                    f"Ticket {ticket_number} must be checked-in before boarding"
                )
            await repo.update_ticket_status(ticket, TicketStatus.BOARDED)
            await repo.save()
            self.tm.update_ticket_status(ticket_number, TicketStatus.BOARDED.value)
            return UpdateTicketStatus(
                ticket_number=ticket_number, status=TicketStatus.BOARDED.value
            )

    async def list_passengers_on_flight(self, flight_id: str):
        async with self._sm() as session:
            repo = TicketRepository(session)
            tickets = await repo.get_all_tickets(flight_id)
            return PassengersOnFlight(
                passengers=[
                    PassengerOnFlight(
                        passenger_name=ticket.passenger_name,
                        ticket_number=ticket.ticket_number,
                        flight_number=flight_id,
                        seat_number=ticket.seat_number,
                        seat_type=ticket.seat_type,
                    )
                    for ticket in tickets
                    if ticket.status == TicketStatus.CHECKED_IN
                ]
            )
