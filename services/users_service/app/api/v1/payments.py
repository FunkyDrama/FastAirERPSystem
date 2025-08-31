from fastapi import APIRouter, Depends, Header, Request, HTTPException
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
import stripe

from services.users_service.app.core.config import stripe_settings
from services.users_service.app.core.deps import (
    get_payment_service,
    get_current_user,
    get_session,
)
from services.users_service.app.repositories.booking_repo import BookingRepository
from services.users_service.app.services.payment import PaymentService
from services.users_service.app.schemas.payment import PaymentStatusOut

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/{booking_id}/intent")
async def create_payment_intent(
    booking_id: UUID, svc: PaymentService = Depends(get_payment_service)
):
    """
    Creates a payment intent for the specified booking ID.

    This endpoint is responsible for generating a payment intent using the
    PaymentService for a booking identified by the provided booking ID.

    :param booking_id: The unique identifier of the booking for which the payment intent is to be created.
    :type booking_id: UUID
    :param svc: The PaymentService dependency that handles the process of creating payment intents.
    :type svc: PaymentService
    :return: A payment intent object created for the given booking ID.
    :rtype: Any
    """
    return await svc.create_intent(booking_id)


@router.post("/{booking_id}/refund")
async def request_refund(
    booking_id: UUID, svc: PaymentService = Depends(get_payment_service)
):
    """
    Handles refund requests for a specific booking by ID. The provided booking ID is
    used to identify the transaction for which the refund is initiated. This method
    relies on the injected `PaymentService` for handling the actual refund logic.

    :param booking_id: The unique identifier of the booking to be refunded.
    :type booking_id: UUID
    :param svc: The injected dependency representing the payment service used to
        process the refund.
    :type svc: PaymentService
    :return: The result of the refund operation as handled by the payment service.
    :rtype: Any
    """
    return await svc.refund(booking_id)


@router.get("/{booking_id}/status", response_model=PaymentStatusOut)
async def get_payment_status(
    booking_id: UUID,
    session: AsyncSession = Depends(get_session),
    user=Depends(get_current_user),
):
    """
    Fetches the payment status for a specific booking for the authenticated user.

    This endpoint retrieves the payment status information associated with a booking
    based on the provided booking ID. The authenticated user must be the owner of the
    booking. If the booking is not found or does not belong to the authenticated user,
    an HTTP 404 error will be raised.

    :param booking_id: The unique identifier of the booking for which payment status
                       is being retrieved.
    :type booking_id: UUID
    :param session: Async database session used to perform operations.
    :type session: AsyncSession
    :param user: The currently authenticated user.
    :return: An object containing the booking ID, payment status, Stripe payment intent ID,
             and Stripe payment status.
    :rtype: PaymentStatusOut
    :raises HTTPException: If the booking is not found or does not belong to the authenticated user.
    """
    repo = BookingRepository(session)
    b = await repo.get_booking_for_owner(booking_id, user.user_id)
    if not b:

        raise HTTPException(status_code=404, detail="Booking not found")
    return PaymentStatusOut(
        booking_id=b.booking_id,
        status=b.status.value,
        stripe_payment_intent_id=b.stripe_payment_intent_id,
        stripe_payment_status=b.stripe_payment_status,
    )


@router.post("/stripe/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str | None = Header(default=None, alias="Stripe-Signature"),
    session: AsyncSession = Depends(get_session),
):
    """
    Handles incoming webhook events from Stripe, allowing the application to process
    notifications related to payment events such as subscriptions, invoices, and
    other payment-related updates.

    This function listens for HTTP POST requests at the specified `/stripe/webhook`
    endpoint. Stripe sends signed payloads containing event details, and this
    function verifies the signature using the configured webhook secret. Upon
    successful verification, the event is routed to the payment service for
    further processing.

    :param request: The FastAPI Request object containing the complete HTTP request
        details, including the webhook event payload sent from Stripe.
    :param stripe_signature: An optional header containing the Stripe signature of
        the webhook payload used to validate its authenticity.
    :param session: Dependency-injected asynchronous session used for database
        operations within the `PaymentService`.
    :return: The result of handling the Stripe webhook event, as processed by the
        `PaymentService`.
    """
    payload = await request.body()
    event = stripe.Webhook.construct_event(
        payload,
        sig_header=stripe_signature,
        secret=stripe_settings.STRIPE_WEBHOOK_SECRET.get_secret_value(),
    )
    svc = PaymentService(BookingRepository(session), current_user=None)
    return await svc.handle_webhook_event(event)
