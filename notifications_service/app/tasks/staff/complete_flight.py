from sqlalchemy import select

from notifications_service.app.db.database import db_manager
from notifications_service.app.worker import celery_app
from services.users_service.app.db.models.flight_ref import FlightRef, FlightStatus


@celery_app.task(name="staff.complete_flight")
def complete_flight(flight_id: str) -> None:
    with db_manager.get_sync_session("users") as session:
        stmt = (
            select(FlightRef)
            .where(FlightRef.flight_id == flight_id)
            .where(FlightRef.status == FlightStatus.SCHEDULED)
        )
        res = session.execute(stmt)
        flight = res.scalar_one_or_none()
        if flight:
            flight.status = FlightStatus.COMPLETED
            session.commit()
