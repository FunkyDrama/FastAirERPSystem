import logging

from sqlalchemy import update
from notifications_service.app.db.database import db_manager
from notifications_service.app.worker import celery_app
from services.users_service.app.db.models.ticket import Ticket

logger = logging.getLogger(__name__)


@celery_app.task(name="staff.update_ticket_status")
def update_ticket_status(
    ticket_number: str, status: str, seat_number: str = None
) -> None:
    with db_manager.get_sync_session("users") as session:
        update_values = {"status": status}
        if seat_number:
            update_values["seat_number"] = seat_number

        session.execute(
            update(Ticket)
            .where(Ticket.ticket_number == ticket_number)
            .values(**update_values)
        )
        session.commit()
        logger.info(
            f"Updated ticket {ticket_number} status to {status} in users_db",
        )
