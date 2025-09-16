from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from services.staff_service.app.db.models.ticket_shadow import TicketStatus
from services.staff_service.app.messaging.task_manager import StaffTaskManager
from services.staff_service.app.repositories.flight_repo import FlightRepository
from services.staff_service.app.repositories.ticket_repo import TicketRepository
from services.staff_service.app.schemas.ticket import (
    UpdateTicketStatus,
    PassengersOnFlight,
    PassengerOnFlight,
    QRScanOut,
)


class CheckInManagerService:
    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession]):
        self._sm = sessionmaker
        self.tm = StaffTaskManager()

    async def check_in_ticket(self, ticket_number: str) -> UpdateTicketStatus:
        async with self._sm() as session:
            repo = TicketRepository(session)
            ticket = await repo.get_ticket_by_number(ticket_number)
            if not ticket:
                raise ValueError(f"Ticket with number {ticket_number} not found")
            if ticket.status != TicketStatus.BOOKED:
                raise ValueError(
                    f"Ticket with number {ticket_number} cannot be checked in"
                )
            seat_number = await FlightRepository(session).assign_seat_number(
                ticket.flight_id
            )
            await repo.set_seat_number(ticket, seat_number)
            await repo.update_ticket_status(
                ticket, TicketStatus.CHECKED_IN, seat_number
            )
            await repo.save()
            self.tm.update_ticket_status(
                ticket_number, TicketStatus.CHECKED_IN.value, seat_number
            )

            return UpdateTicketStatus(
                ticket_number=ticket_number, status=TicketStatus.CHECKED_IN.value
            )

    async def get_all_passengers_on_flight(self, flight_id: str):
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
                    if ticket.status == TicketStatus.BOOKED
                ]
            )

    async def handle_qr_code(self, ticket_number: str) -> QRScanOut:
        async with self._sm() as session:
            repo = TicketRepository(session)
            ticket = await repo.get_ticket_by_number(ticket_number)
            if not ticket:
                raise ValueError(f"Ticket with number {ticket_number} not found")
            if ticket.status != TicketStatus.CHECKED_IN:
                raise ValueError(
                    f"Ticket with number {ticket_number} is not checked in"
                )
            return QRScanOut(
                flight_id=ticket.flight_id,
                passenger_name=ticket.passenger_name,
                seat_number=ticket.seat_number,
                seat_type=ticket.seat_type,
                status=TicketStatus.CHECKED_IN.value,
            )
