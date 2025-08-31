import datetime as dt
from decimal import Decimal
from uuid import UUID
from typing import Literal

from pydantic import BaseModel, Field


SeatName = Literal["ECONOMY", "PREMIUM_ECONOMY", "BUSINESS"]


class OptionPick(BaseModel):
    """
    Represents a selectable option with a specified quantity.

    This class is used for representing options in a system where users can
    pick an option and specify a quantity for it. The quantity is constrained
    to ensure it's within a valid range.

    :ivar option_id: Unique identifier for the option.
    :type option_id: UUID
    :ivar qty: Quantity of the option selected by the user. Must be between 1 and 9.
    :type qty: int
    """

    option_id: UUID
    qty: int = Field(1, ge=1, le=9)


class PassengerRef(BaseModel):
    """
    Represents a reference to a passenger.

    This class is used to uniquely identify a passenger via their unique ID,
    typically for use in larger systems dealing with passenger data management
    or related functionality.

    :ivar passenger_id: The unique identifier for a passenger.
    :type passenger_id: UUID
    """

    passenger_id: UUID


class PassengerCreate(BaseModel):
    """
    Represents a model for creating a passenger entry.

    This class is designed to capture and validate the information necessary
    for creating a new passenger. It ensures the first and last names are
    provided and correctly formatted, while the contact information is
    optional.

    :ivar first_name: The first name of the passenger.
    :type first_name: str
    :ivar last_name: The last name of the passenger.
    :type last_name: str
    :ivar contact_info: The contact information of the passenger, which can
        be optional.
    :type contact_info: str or None
    """

    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    contact_info: str | None = None


PassengerRefOrCreate = PassengerRef | PassengerCreate


class QuoteIn(BaseModel):
    """
    Represents the input model for creating or processing a quote.

    This class is designed for use in scenarios where flight-based quotes,
    custom passenger and seating preferences, and additional options are
    provided. It supports creating detailed quotes for a specific flight
    with various options and configurations.

    :ivar flight_id: Unique identifier for the flight associated with
        the quote.
    :type flight_id: UUID
    :ivar passengers: List of passengers, either references or new
        passengers being created. Must include at least one passenger.
    :type passengers: list[PassengerRefOrCreate]
    :ivar seat_type_name: The requested seat type name (e.g., "economy",
        "business").
    :type seat_type_name: str
    :ivar options: List of additional options selected for this quote.
        Defaults to an empty list if no additional options are chosen.
    :type options: list[OptionPick]
    :ivar per_passenger_options: Indicates whether options are applied
        per passenger. Defaults to True.
    :type per_passenger_options: bool
    :ivar discount_code: Optional discount code applied to the quote.
        Defaults to None if no discount code is provided.
    :type discount_code: str | None
    """

    flight_id: UUID
    passengers: list[PassengerRefOrCreate] = Field(min_length=1)
    seat_type_name: SeatName
    options: list[OptionPick] = Field(default_factory=list)
    per_passenger_options: bool = True
    discount_code: str | None = None


class CreateBookingIn(QuoteIn):
    """
    Represents the input model for creating a booking.

    This class extends the functionality of the `QuoteIn` class, adding
    specific fields required for creating a booking. It is primarily used
    for transferring data related to booking creation operations.

    :ivar lock_price: Indicates whether the price should be locked during
        the booking process. Defaults to True.
    :type lock_price: bool
    """

    lock_price: bool = True


class DiscountInfo(BaseModel):
    """
    Represents information related to a discount.

    This class encapsulates data about a specific discount, including its
    code (if any), the percentage of discount offered, and the total
    amount of the discount.

    :ivar code: The discount code applied, or None if no code is set.
    :type code: str | None
    :ivar percent_off: Percentage of discount provided, represented
        as an integer.
    :type percent_off: int
    :ivar amount: The total amount of the discount.
    :type amount: Decimal
    """

    code: str | None
    percent_off: int
    amount: Decimal


class PriceBreakdownPerTicket(BaseModel):
    """
    Represents the price breakdown for a specific ticket associated with a passenger.

    This class provides details about the ticket pricing for an individual passenger,
    allowing for structured representation of pricing data. It is intended to be used
    to track and access pricing information related to specific passengers in a larger
    ticketing or billing system.

    :ivar passenger_index: Index of the passenger this ticket's pricing is associated with.
    :type passenger_index: int
    :ivar price: The price of the ticket for the passenger.
    :type price: Decimal
    """

    passenger_index: int
    price: Decimal


class QuoteOut(BaseModel):
    """
    Represents a quote output with detailed price calculation and breakdown per ticket.

    This model is primarily used for handling pricing information for tickets, including
    currency, base price, modifiers, totals, discounts, and breakdown per ticket in an
    organized and structured way.

    :ivar currency: The currency in which the pricing is expressed.
    :type currency: str
    :ivar base_price_per_ticket: The base price of a single ticket before any multipliers
        or options are applied.
    :type base_price_per_ticket: Decimal
    :ivar seat_type_multiplier: The multiplier applied based on the type of seat selected.
    :type seat_type_multiplier: Decimal
    :ivar options_total: The total cost of any additional options or add-ons selected.
    :type options_total: Decimal
    :ivar subtotal: The subtotal value calculated before any discounts are applied.
    :type subtotal: Decimal
    :ivar discount: An optional discount information object, if any discounts have been applied.
    :type discount: DiscountInfo or None
    :ivar total: The final total after applying discounts and calculating all components.
    :type total: Decimal
    :ivar breakdown_per_ticket: A list representing the price breakdown for each ticket.
    :type breakdown_per_ticket: list[PriceBreakdownPerTicket]
    """

    currency: str = "USD"
    base_price_per_ticket: Decimal
    seat_type_multiplier: Decimal
    options_total: Decimal
    subtotal: Decimal
    discount: DiscountInfo | None = None
    total: Decimal
    breakdown_per_ticket: list[PriceBreakdownPerTicket]


class FlightBrief(BaseModel):
    """
    Represents a brief summary of flight details.

    This class is used to encapsulate information about a flight, such as its
    unique identifier, flight number, origin, destination, departure and arrival
    times, and current status. It serves as a concise representation of flight
    data for use in applications requiring flight tracking or scheduling.

    :ivar flight_id: The unique identifier of the flight.
    :type flight_id: UUID
    :ivar flight_number: The assigned number of the flight.
    :type flight_number: str
    :ivar origin: The originating airport or location of the flight.
    :type origin: str
    :ivar destination: The destination airport or location of the flight.
    :type destination: str
    :ivar departure_time: The scheduled departure time of the flight.
    :type departure_time: datetime.datetime
    :ivar arrival_time: The scheduled arrival time of the flight.
    :type arrival_time: datetime.datetime
    :ivar status: The current status of the flight (e.g., scheduled, delayed,
        cancelled).
    :type status: str
    """

    flight_id: UUID
    flight_number: str
    origin: str
    destination: str
    departure_time: dt.datetime
    arrival_time: dt.datetime
    status: str


class TicketOut(BaseModel):
    """
    Represents a ticket issued for a passenger.

    Provides details about the ticket, including the ticket number, passenger
    associated with it, seat type, and the price of the ticket.

    :ivar ticket_number: Unique identifier of the ticket.
    :type ticket_number: str
    :ivar passenger_id: Identifier of the passenger who owns the ticket.
    :type passenger_id: UUID
    :ivar seat_type_name: Name of the seat type associated with the ticket.
    :type seat_type_name: str
    :ivar price: Cost of the ticket in a decimal format.
    :type price: Decimal
    """

    ticket_number: str
    passenger_id: UUID
    seat_type_name: SeatName
    price: Decimal


class BookingOut(BaseModel):
    """
    Represents the details of a booking entity.

    This class is designed to hold information about a booking, including
    its unique identifier, status, associated flight, tickets, and any applicable
    discounts. It encapsulates all data related to a single booking transaction.

    :ivar booking_id: Unique identifier for the booking.
    :type booking_id: UUID
    :ivar status: Current status of the booking (e.g., confirmed, canceled).
    :type status: str
    :ivar total_amount: Total monetary amount of the booking after applicable discounts.
    :type total_amount: Decimal
    :ivar discount_code: Discount code applied to the booking, if any.
    :type discount_code: str | None
    :ivar flight: Brief details of the associated flight.
    :type flight: FlightBrief
    :ivar tickets: A list of ticket details linked to this booking.
    :type tickets: list[TicketOut]
    """

    booking_id: UUID
    status: str
    total_amount: Decimal
    discount_code: str | None
    flight: FlightBrief
    tickets: list[TicketOut]


class BookingShortOut(BaseModel):
    """
    Represents a summary of a booking with essential details.

    This class contains attributes that summarize the details of a specific booking.
    It is designed to provide an overview of the booking status, related flight
    information, and other important metrics. Useful for displaying or transmitting
    a concise booking summary.

    :ivar booking_id: Unique identifier for the booking.
    :type booking_id: UUID
    :ivar status: Current status of the booking (e.g., confirmed, pending, canceled).
    :type status: str
    :ivar total_amount: Total monetary amount for the booking.
    :type total_amount: Decimal
    :ivar flight: Brief information about the related flight.
    :type flight: FlightBrief
    :ivar tickets_count: Number of tickets associated with the booking.
    :type tickets_count: int
    """

    booking_id: UUID
    status: str
    total_amount: Decimal
    flight: FlightBrief
    tickets_count: int


class MyBookingsOut(BaseModel):
    """
    Representation of the user's bookings and associated metadata.

    This class is used to encapsulate a list of bookings along with the total
    number of bookings. It provides a structured way to model and interact with
    this data in applications.

    :ivar items: List of user's bookings, represented by instances of the
        BookingShortOut class.
    :type items: list[BookingShortOut]
    :ivar total: Total number of bookings for the user.
    :type total: int
    """

    items: list[BookingShortOut]
    total: int
