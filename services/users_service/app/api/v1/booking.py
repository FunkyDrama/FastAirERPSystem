from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from services.users_service.app.core.deps import get_booking_service
from services.users_service.app.schemas.booking import (
    QuoteIn,
    QuoteOut,
    CreateBookingIn,
    BookingOut,
    MyBookingsOut,
)
from services.users_service.app.services.booking import BookingService

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("/quotes", response_model=QuoteOut, status_code=status.HTTP_200_OK)
async def make_quote(
    payload: QuoteIn,
    svc: BookingService = Depends(get_booking_service),
) -> QuoteOut:
    """
    Creates a new quote using the provided payload and booking service.

    This endpoint is responsible for processing the input payload, interacting with
    the booking service to calculate or fetch the quote, and returning the
    result in the expected response format.

    :param payload: The input data required for generating the quote.
        Contains all necessary fields to calculate the quote.
    :type payload: QuoteIn
    :param svc: An instance of the `BookingService` used to process the quote.
        This service handles the business logic for creating quotes.
    :type svc: BookingService
    :return: The generated quote information, containing details as per
        `QuoteOut` response model.
    :rtype: QuoteOut
    """
    return await svc.quote(payload)


@router.post("", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
async def create_booking(
    payload: CreateBookingIn,
    svc: BookingService = Depends(get_booking_service),
) -> BookingOut:
    """
    Creates a new booking using the supplied data.

    This function handles the creation of a booking and integrates
    the booking service to complete the process. It uses dependency
    injection to obtain the booking service.

    :param payload: The input data for creating the booking.
    :param svc: The service responsible for handling the booking creation.
    :type svc: BookingService
    :return: The newly created booking.
    """
    return await svc.create(payload)


@router.get("/mine", response_model=MyBookingsOut)
async def list_my_bookings(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    svc: BookingService = Depends(get_booking_service),
) -> MyBookingsOut:
    """
    Fetches the list of bookings created by the currently authenticated user. The list
    is paginated based on the provided limit and offset. This endpoint allows users
    to manage and review their previous or upcoming bookings efficiently.

    :param limit: The maximum number of bookings to return. Value must be between 1
        and 200 (inclusive).
    :param offset: The number of bookings to skip before starting to collect the
        result set. Value must be 0 or greater.
    :param svc: The booking service dependency that handles logic related to fetching
        user's bookings.
    :return: A paginated list of user bookings with metadata describing the bookings.
    :rtype: MyBookingsOut
    """
    return await svc.list_mine(limit=limit, offset=offset)


@router.get("/{booking_id}", response_model=BookingOut)
async def get_booking(
    booking_id: UUID,
    svc: BookingService = Depends(get_booking_service),
) -> BookingOut:
    """
    Retrieve a booking by its unique identifier.

    This asynchronous endpoint is responsible for fetching and returning booking
    details based on the provided booking ID. The response is modeled as a
    `BookingOut` object. The booking service dependency is injected to perform
    the operational logic.

    :param booking_id: The unique identifier of the booking.
    :param svc: The service handling booking-related logic.
    :return: The booking details, encapsulated as a `BookingOut` object.
    """
    return await svc.get(booking_id)


@router.post("/{booking_id}/confirm", response_model=BookingOut)
async def confirm_booking(
    booking_id: UUID,
    svc: BookingService = Depends(get_booking_service),
) -> BookingOut:
    """
    Confirms a booking based on the provided booking ID and the booking service.

    This function allows the client to confirm a particular booking identified by
    its unique identifier. It uses the provided booking service to process the
    confirmation request asynchronously.

    :param booking_id: The unique identifier of the booking to be confirmed.
    :param svc: The booking service dependency used to handle the confirmation
        logic.
    :return: The confirmed booking details encapsulated in a `BookingOut` model.
    """
    return await svc.confirm(booking_id)


@router.post("/{booking_id}/cancel", response_model=BookingOut)
async def cancel_booking(
    booking_id: UUID,
    svc: BookingService = Depends(get_booking_service),
) -> BookingOut:
    """
    Cancels a booking based on the provided booking ID. This endpoint interacts
    with the BookingService to process the cancellation. It ensures the booking
    is properly handled and an updated booking object is returned.

    :param booking_id: The unique identifier for the booking to be canceled.
    :param svc: Dependency-injected instance of BookingService to handle the
        booking cancellation logic.
    :return: Updated booking information after cancellation.
    """
    return await svc.cancel(booking_id)
