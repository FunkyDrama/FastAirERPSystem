import uuid
from pydantic_core.core_schema import JsonSchema

from notifications_service.app.worker import celery_app


class StaffTaskManager:
    def __init__(self):
        self.celery = celery_app

    def cancel_flight(self, flight_id: uuid.UUID) -> None:
        self.celery.send_task("staff.cancel_flight", args=[str(flight_id)])

    def create_flight(self, flight_model: JsonSchema) -> None:
        self.celery.send_task("staff.create_flight", args=[flight_model])

    def update_ticket_status(
        self,
        ticket_number: str,
        ticket_status: str,
        seat_number: str = None,
    ) -> None:
        self.celery.send_task(
            "staff.update_ticket_status",
            args=[ticket_number, ticket_status, seat_number],
        )
