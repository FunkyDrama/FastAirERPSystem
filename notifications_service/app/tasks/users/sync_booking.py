import logging
from decimal import Decimal
import uuid

from sqlalchemy import select, exists
from notifications_service.app.db.database import db_manager
from notifications_service.app.worker import celery_app
from services.staff_service.app.db.models.ticket_shadow import (
    TicketShadow,
    TicketStatus,
)

logger = logging.getLogger(__name__)


@celery_app.task(name="staff.sync_booking")
def sync_booking(payload: dict) -> None:
    with db_manager.get_sync_session("staff") as session:
        for t in payload["tickets"]:
            query = select(
                exists().where(TicketShadow.ticket_number == t["ticket_number"])
            )
            already_exists = session.scalar(query)
            if already_exists:
                continue

            shadow = TicketShadow(
                ticket_number=t["ticket_number"],
                passenger_name=t["passenger_name"],
                seat_number=None,
                seat_type=t["seat_type_name"],
                price=Decimal(t["price"]),
                status=TicketStatus.BOOKED,
                flight_id=uuid.UUID(payload["flight_id"]),
            )
            session.add(shadow)

        session.commit()
        logger.info(
            f"Synced booking {payload['booking_id']} with {len(payload['tickets'])} tickets into staff_db"
        )
