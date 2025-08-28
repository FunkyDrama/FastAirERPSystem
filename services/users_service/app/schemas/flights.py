import datetime as dt
import uuid
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict


class FlightRefOut(BaseModel):
    """
    Represents detailed information about a flight reference including unique
    identifier, flight number, origin, destination, schedule, and status.

    This class is primarily used to store and manage the core information
    related to a flight, such as its ID, departure and arrival details, and
    its current status.

    :ivar flight_id: Unique identifier of the flight.
    :type flight_id: uuid.UUID
    :ivar flight_number: The flight number assigned to the flight.
    :type flight_number: str
    :ivar origin: The departure location of the flight.
    :type origin: str
    :ivar destination: The arrival location of the flight.
    :type destination: str
    :ivar departure_time: Scheduled departure time of the flight.
    :type departure_time: dt.datetime
    :ivar arrival_time: Scheduled arrival time of the flight.
    :type arrival_time: dt.datetime
    :ivar status: Current status of the flight (e.g., on-time, delayed).
    :type status: str
    """

    model_config = ConfigDict(from_attributes=True)
    flight_id: uuid.UUID
    flight_number: str
    origin: str
    destination: str
    departure_time: dt.datetime
    arrival_time: dt.datetime
    status: str


class FlightSearchQuery(BaseModel):
    """
    Represents a query for searching flights.

    This class defines a model for structuring data related to a flight search query.
    It includes attributes for specifying the origin, destination, travel date, number
    of passengers, and pagination parameters. The purpose of this class is to provide
    a clear and validated way to manage flight search parameters.

    :ivar origin: IATA code of the origin airport. Optional.
    :type origin: str | None
    :ivar destination: IATA code of the destination airport. Optional.
    :type destination: str | None
    :ivar date: Travel date in the YYYY-MM-DD format. Optional.
    :type date: dt.date | None
    :ivar passengers: Number of passengers for the flight. Defaults to 1.
    :type passengers: int
    :ivar limit: Maximum number of flight results to return per query. Defaults to 50.
    :type limit: int
    :ivar offset: Number of skipped results for pagination. Defaults to 0.
    :type offset: int
    """

    origin: str | None = Field(None, description="IATA code, e.g. KBP")
    destination: str | None = Field(None, description="IATA code, e.g. WAW")
    date: dt.date | None = Field(
        None, description="YYYY-MM-DD format, e.g. 2025-12-31)"
    )
    passengers: int = Field(1, ge=1, le=9)
    limit: int = Field(50, ge=1, le=200)
    offset: int = Field(0, ge=0)


class OptionOut(BaseModel):
    """
    Represents an option with specific details, such as an identifier, name, and price.

    This class models an option entity including its unique identifier, descriptive
    name, and associated price. It's designed to serve as a structured representation
    of options within a broader application or system.

    :ivar option_id: The unique identifier of the option.
    :type option_id: uuid.UUID
    :ivar name: The name of the option.
    :type name: str
    :ivar price: The price associated with the option.
    :type price: Decimal
    """

    model_config = ConfigDict(from_attributes=True)
    option_id: uuid.UUID
    name: str
    price: Decimal


class SeatTypeOut(BaseModel):
    """
    Represents the output data for a seat type.

    This class is designed to encapsulate the details about a specific type of seat
    including its name and an optional description. It serves as a model for data
    that is output or transferred in the context of seat-related information for systems
    that interpret or consume such configurations.

    :ivar type_name: The name of the seat type.
    :type type_name: str
    :ivar description: An optional description of the seat type. It may contain details
        or additional information about the seat type. Defaults to None.
    :type description: str | None
    """

    model_config = ConfigDict(from_attributes=True)
    type_name: str
    description: str | None = None


class DiscountOut(BaseModel):
    """
    Represents a discount entity with associated details.

    The DiscountOut class is used to model a discount offering. It includes
    information about the discount code, a description (if available), and
    the percentage off. This class supports configurations allowing its
    fields to be populated from attributes.

    :ivar discount_code: The code representing the discount offered.
    :type discount_code: str
    :ivar description: A textual description of the discount, or None if
        not provided.
    :type description: str | None
    :ivar percent_off: The percentage off provided by the discount.
    :type percent_off: int
    """

    model_config = ConfigDict(from_attributes=True)
    discount_code: str
    description: str | None = None
    percent_off: int
