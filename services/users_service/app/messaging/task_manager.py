import uuid

from notifications_service.app.worker import celery_app


class UserTaskManager:
    def __init__(self):
        self.celery = celery_app

    @staticmethod
    def _serialize_ticket(ticket, passenger) -> dict:
        return {
            "ticket_number": ticket.ticket_number,
            "seat_type_name": ticket.seat_type_name,
            "price": str(ticket.price),
            "passenger_name": f"{passenger.first_name} {passenger.last_name}",
        }

    def sync_booking(self, booking, flight, tickets, passengers) -> None:
        payload = {
            "booking_id": str(booking.booking_id),
            "flight_id": str(flight.flight_id),
            "tickets": [
                self._serialize_ticket(t, p) for t, p in zip(tickets, passengers)
            ],
        }

        self.celery.send_task("staff.sync_booking", args=[payload])

    def mark_tickets_paid(
        self, booking_id: uuid.UUID, ticket_numbers: list[str]
    ) -> None:
        self.celery.send_task(
            "staff.mark_tickets_paid",
            args=[str(booking_id), ticket_numbers],
        )

    def mark_tickets_refunded(
        self, booking_id: uuid.UUID, ticket_numbers: list[str]
    ) -> None:
        self.celery.send_task(
            "staff.mark_tickets_refunded",
            args=[str(booking_id), ticket_numbers],
        )

    def send_notification(self, recipient: str, payload: dict) -> None:
        tickets = payload.get("tickets", [])

        for ticket in tickets:
            self.celery.send_task(
                "users.send_email",
                args=[
                    recipient,
                    payload["booking_id"],
                    ticket["ticket_number"],
                    ticket.get("passenger_name", ""),
                ],
            )
