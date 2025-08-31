from pydantic import BaseModel
from uuid import UUID


class PaymentStatusOut(BaseModel):
    """
    Represents the output of a payment status, with information about the booking,
    status of the payment, and related Stripe details.

    This class is used to encapsulate and validate the payment status, providing
    details like the booking ID, current payment status, the Stripe payment intent ID,
    and the status of the corresponding Stripe payment.

    :ivar booking_id: The unique identifier for the booking.
    :type booking_id: UUID
    :ivar status: The current status of the payment.
    :type status: str
    :ivar stripe_payment_intent_id: The unique identifier of the Stripe payment intent, if applicable.
    :type stripe_payment_intent_id: str | None
    :ivar stripe_payment_status: The current status of the Stripe payment, if applicable.
    :type stripe_payment_status: str | None
    """

    booking_id: UUID
    status: str
    stripe_payment_intent_id: str | None
    stripe_payment_status: str | None
