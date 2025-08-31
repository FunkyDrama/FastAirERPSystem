from __future__ import annotations
import datetime as dt
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel

from services.users_service.app.schemas.booking import BookingShortOut


class PassengerOut(BaseModel):
    """
    Represents a passenger entity with basic identification and personal
    details.

    This class is used to model the output data for a passenger, typically
    including their unique identification and associated personal
    information, such as first and last names.

    :ivar passenger_id: The unique identifier of the passenger.
    :type passenger_id: UUID
    :ivar first_name: The first name of the passenger.
    :type first_name: str
    :ivar last_name: The last name of the passenger.
    :type last_name: str
    """

    passenger_id: UUID
    first_name: str
    last_name: str


class MeOut(BaseModel):
    """
    Represents a user account overview, including personal information, account
    balance, and bookings.

    Provides a detailed overview of a user, consisting of contact details, financial
    information, and several categorized bookings (past, upcoming, passengers). Useful
    for displaying a comprehensive summary of user-related data in an application.

    :ivar email: The email address associated with the user account.
    :type email: str
    :ivar balance: The current account balance for the user, stored as a decimal.
    :type balance: Decimal
    :ivar passengers: A list of passengers linked to the user account.
    :type passengers: list[PassengerOut]
    :ivar upcoming: A list of upcoming bookings made by the user.
    :type upcoming: list[BookingShortOut]
    :ivar past: A list of previous bookings completed by the user.
    :type past: list[BookingShortOut]
    :ivar now_utc: The current UTC datetime.
    :type now_utc: datetime.datetime
    """

    email: str
    balance: Decimal
    passengers: list[PassengerOut]
    upcoming: list[BookingShortOut]
    past: list[BookingShortOut]
    now_utc: dt.datetime
