import uuid
from sqlalchemy import insert
from notifications_service.app.db.database import db_manager
from notifications_service.app.worker import celery_app
from services.users_service.app.db.models.flight_ref import FlightRef, FlightStatus


@celery_app.task(name="staff.create_flight")
def create_flight(flight_data: dict) -> None:
    values = dict(flight_data)
    values.pop("airplane_id", None)
    fid = values.get("flight_id")
    if fid is not None and not isinstance(fid, uuid.UUID):
        values["flight_id"] = uuid.UUID(str(fid))

    values["status"] = FlightStatus.SCHEDULED

    with db_manager.get_sync_session("users") as session:
        stmt = insert(FlightRef).values(values)
        session.execute(stmt)
        session.commit()
