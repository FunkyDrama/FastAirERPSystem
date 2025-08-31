import stripe
from uuid import UUID
from decimal import Decimal
from fastapi import HTTPException
from stripe import Event

from notifications_service.app.worker import celery_app
from services.users_service.app.db.models.booking import BookingStatus
from services.users_service.app.db.models.user import UserAccount
from services.users_service.app.repositories.booking_repo import BookingRepository
from services.users_service.app.core.config import stripe_settings


class PaymentService:
    """
    Handles payment processing and refunds using Stripe, including webhook handling.

    This service interacts with Stripe's API to create payment intents and process refunds
    associated with bookings. It also handles Stripe webhook events to update booking status,
    and can notify users on important booking updates via email. All operations are tied
    to a repository for booking data persistence.

    :ivar repo: Repository instance for accessing and manipulating booking data.
    :type repo: BookingRepository
    :ivar user: Current user performing operations on bookings.
    :type user: Any
    """

    def __init__(self, repo: BookingRepository, current_user: UserAccount | None) -> None:
        self.repo = repo
        self.user = current_user
        stripe.api_key = stripe_settings.STRIPE_SECRET_KEY.get_secret_value()

    async def create_intent(self, booking_id: UUID) -> dict:
        b = await self.repo.load_booking_with_user_and_tickets(
            booking_id, self.user.user_id
        )
        if not b:
            raise HTTPException(status_code=404, detail="Booking not found")
        if b.status != BookingStatus.RESERVED:
            raise HTTPException(status_code=400, detail="Booking not in RESERVED state")

        try:
            amount_cents = int(Decimal(b.total_amount) * 100)
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency="usd",
                automatic_payment_methods={
                    "enabled": True,
                    "allow_redirects": "never",
                },
                metadata={
                    "booking_id": str(b.booking_id),
                    "user_id": str(self.user.user_id),
                },
            )
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=502, detail=f"Stripe error: {e.user_message or str(e)}"
            )

        b.stripe_payment_intent_id = intent.id
        b.stripe_payment_status = intent.status
        await self.repo.save()
        return {"client_secret": intent.client_secret, "payment_intent_id": intent.id}

    async def refund(self, booking_id: UUID) -> dict:
        b = await self.repo.get_booking_for_owner(booking_id, self.user.user_id)
        if not b:
            raise HTTPException(status_code=404, detail="Booking not found")
        if b.status != BookingStatus.PAID:
            raise HTTPException(
                status_code=400, detail="Only PAID bookings can be refunded"
            )
        if not b.stripe_payment_intent_id:
            raise HTTPException(status_code=409, detail="No Stripe intent")

        try:
            r = stripe.Refund.create(payment_intent=b.stripe_payment_intent_id)
        except stripe.error.StripeError as e:
            raise HTTPException(
                status_code=502, detail=f"Stripe error: {e.user_message or str(e)}"
            )

        b.stripe_refund_id = r.id
        await self.repo.save()
        return {
            "status": "refund_submitted",
            "refund_id": r.id,
            "booking_id": str(b.booking_id),
        }

    @staticmethod
    def _booking_to_payload(b) -> dict:
        return {
            "booking_id": str(b.booking_id),
            "total_amount": str(b.total_amount),
            "currency": "USD",
            "flight": (
                {
                    "flight_id": (
                        str(b.tickets[0].flight.flight_id) if b.tickets else ""
                    ),
                    "flight_number": (
                        b.tickets[0].flight.flight_number if b.tickets else ""
                    ),
                    "origin": b.tickets[0].flight.origin if b.tickets else "",
                    "destination": b.tickets[0].flight.destination if b.tickets else "",
                    "departure_time": (
                        b.tickets[0].flight.departure_time.isoformat()
                        if b.tickets
                        else ""
                    ),
                    "arrival_time": (
                        b.tickets[0].flight.arrival_time.isoformat()
                        if b.tickets
                        else ""
                    ),
                    "status": (
                        b.tickets[0].flight.status.value if b.tickets else "scheduled"
                    ),
                }
                if b.tickets
                else {}
            ),
            "tickets": [
                {
                    "ticket_number": t.ticket_number,
                    "passenger_id": str(t.passenger_id),
                    "seat_type_name": t.seat_type_name,
                    "price": str(t.price),
                }
                for t in b.tickets
            ],
        }

    def _send_notification(self, recipient: str, payload: dict):
        tickets = payload.get("tickets", [])
        ticket_number = tickets[0]["ticket_number"] if tickets else ""

        celery_app.send_task(
            "notifications_service.app.tasks.send_email",
            args=[recipient, payload["booking_id"], ticket_number],
            queue="emails",
        )

    async def handle_webhook_event(self, event: Event) -> dict:
        typ = event["type"]
        data = event["data"]["object"]

        intent_id = (
            data.get("id") if "payment_intent." in typ else data.get("payment_intent")
        )
        if not intent_id:
            return {"ignored": True}

        b = await self.repo.get_booking_by_payment_intent(intent_id)
        if not b:
            return {"ignored": True}

        if typ == "payment_intent.succeeded":
            b.stripe_payment_status = data.get("status", "succeeded")
            b.status = BookingStatus.PAID
            await self.repo.save()

            if b.user and b.user.email:
                payload = self._booking_to_payload(b)
                self._send_notification(b.user.email, payload)

            return {"ok": True}

        if typ in ("charge.refunded", "refund.succeeded"):
            b.stripe_payment_status = "refunded"
            b.status = BookingStatus.REFUNDED
            await self.repo.save()
            return {"ok": True}

        if typ == "payment_intent.payment_failed":
            b.stripe_payment_status = "failed"
            await self.repo.save()
            return {"ok": True}

        return {"ignored": True}
