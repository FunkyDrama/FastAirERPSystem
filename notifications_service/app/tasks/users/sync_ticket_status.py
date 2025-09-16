import logging

from sqlalchemy import update
from notifications_service.app.db.database import db_manager
from notifications_service.app.worker import celery_app
from services.staff_service.app.db.models.ticket_shadow import (
    TicketShadow,
    TicketStatus,
)

logger = logging.getLogger(__name__)


@celery_app.task(name="staff.mark_tickets_paid")
def mark_tickets_paid(booking_id: str, ticket_numbers: list[str]) -> None:
    with db_manager.get_sync_session("staff") as session:
        session.execute(
            update(TicketShadow)
            .where(TicketShadow.ticket_number.in_(ticket_numbers))
            .values(status=TicketStatus.BOOKED)
        )
        session.commit()
        logger.info(
            f"Tickets {ticket_numbers} for booking {booking_id} marked as paid in staff_db"
        )


@celery_app.task(name="staff.mark_tickets_refunded")
def mark_tickets_refunded(booking_id: str, ticket_numbers: list[str]) -> None:
    with db_manager.get_sync_session("staff") as session:
        session.execute(
            update(TicketShadow)
            .where(TicketShadow.ticket_number.in_(ticket_numbers))
            .values(status=TicketStatus.CANCELED)
        )
        session.commit()
        logger.info(
            f"Tickets {ticket_numbers} for booking {booking_id} refunded in staff_db"
        )
