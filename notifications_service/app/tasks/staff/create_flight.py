import asyncio
import uuid

from sqlalchemy import insert

from notifications_service.app.db.database import db_manager
from notifications_service.app.worker import celery_app
from services.users_service.app.db.models.flight_ref import FlightRef, FlightStatus


@celery_app.task(name="staff.create_flight")
def create_flight(flight_data: dict):
    async def _create():
        async with db_manager.get_session("users") as session:
            stmt = insert(FlightRef).values(
                flight_id=uuid.UUID(flight_data["flight_id"]),
                flight_number=flight_data["flight_number"],
                origin=flight_data["origin"],
                destination=flight_data["destination"],
                departure_time=flight_data["departure_time"],
                arrival_time=flight_data["arrival_time"],
                status=FlightStatus.SCHEDULED,
            )
            await session.execute(stmt)
            await session.commit()

    asyncio.run(_create())
