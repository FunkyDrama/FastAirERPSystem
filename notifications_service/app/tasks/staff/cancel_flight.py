from sqlalchemy import select

from notifications_service.app.db.database import db_manager
from notifications_service.app.worker import celery_app
from services.users_service.app.db.models.flight_ref import FlightRef, FlightStatus


@celery_app.task(name="staff.cancel_flight")
def cancel_flight(flight_id: str) -> None:
    with db_manager.get_sync_session("users") as session:
        stmt = (
            select(FlightRef)
            .where(FlightRef.flight_id == flight_id)
            .where(FlightRef.status != FlightStatus.CANCELED)
        )
        res = session.execute(stmt)
        flight = res.scalar_one_or_none()
        flight.status = FlightStatus.CANCELED
        session.commit()
