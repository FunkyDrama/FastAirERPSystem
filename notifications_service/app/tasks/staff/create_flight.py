import uuid

from sqlalchemy import insert

from notifications_service.app.db.database import db_manager
from notifications_service.app.worker import celery_app
from services.users_service.app.db.models.flight_ref import FlightRef, FlightStatus


@celery_app.task(name="staff.create_flight")
def create_flight(flight_data: dict) -> None:
    with db_manager.get_sync_session("users") as session:
        stmt = insert(FlightRef).values(
            **flight_data,
            flight_id=uuid.UUID(flight_data["flight_id"]),
            status=FlightStatus.SCHEDULED,
        )
        session.execute(stmt)
        session.commit()
