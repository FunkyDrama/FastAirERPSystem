import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
import datetime as dt
from services.users_service.app.core.deps import get_flight_service, get_current_user
from services.users_service.app.schemas.flights import (
    FlightRefOut,
    FlightSearchQuery,
    OptionOut,
    SeatTypeOut,
    DiscountOut,
)
from services.users_service.app.services.flights import FlightQueryService

router = APIRouter(
    prefix="/flights", tags=["flights"], dependencies=[Depends(get_current_user)]
)


@router.get("/search", response_model=list[FlightRefOut])
async def flights_search(
    origin: str | None = Query(None),
    destination: str | None = Query(None),
    date: str | None = Query(None, description="YYYY-MM-DD"),
    passengers: int = Query(1, ge=1, le=9),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    svc: FlightQueryService = Depends(get_flight_service),
):
    """
    Search for available flights that match the specified query parameters.

    This endpoint provides a way to search for flights based on origin, destination,
    travel date, number of passengers, and pagination options.

    :param origin: The IATA code of the origin airport. Example "LAX" or "JFK".
    :param destination: The IATA code of the destination airport.
    :param date: Travel date in the format "YYYY-MM-DD". If omitted, no date filtering is
      applied.
    :param passengers: The number of passengers for the flight, ranging between 1 and 9.
    :param limit: The maximum number of flights returned in the result set,
      restricted between 1 and 200.
    :param offset: The number of items to skip before starting to collect the
      result set, useful for pagination.
    :param svc: An instance of FlightQueryService used to handle flight search logic.

    :return: A list of flights matching the search criteria with their summarized
      details wrapped in FlightRefOut.
    """
    q = FlightSearchQuery(
        origin=origin,
        destination=destination,
        date=None if not date else dt.date.fromisoformat(date),
        passengers=passengers,
        limit=limit,
        offset=offset,
    )
    flights = await svc.search(
        origin=q.origin,
        destination=q.destination,
        date=q.date,
        passengers=q.passengers,
        limit=q.limit,
        offset=q.offset,
    )
    return [FlightRefOut.model_validate(f) for f in flights]


@router.get("/{flight_id}", response_model=FlightRefOut)
async def flight_by_id(
    flight_id: uuid.UUID,
    svc: FlightQueryService = Depends(get_flight_service),
):
    """
    Handles HTTP GET requests for retrieving flight information by flight ID.

    This function retrieves flight details based on the provided flight ID.
    It uses a dependency-injected flight service to query the flight data.
    If the flight is not found, it raises a 404 HTTP exception with an appropriate
    message.

    :param flight_id: The UUID of the flight to be retrieved.
    :type flight_id: uuid.UUID
    :param svc: The flight query service dependency for retrieving flight details.
    :type svc: FlightQueryService
    :return: An instance of `FlightRefOut` containing the flight details.
    :rtype: FlightRefOut
    :raises HTTPException: If the flight with the given ID cannot be found.
    """
    f = await svc.get_flight(flight_id)
    if not f:
        raise HTTPException(status_code=404, detail="Flight not found")
    return FlightRefOut.model_validate(f)


@router.get("/options/{flight_id}", response_model=list[OptionOut])
async def flight_options(
    flight_id: uuid.UUID,
    svc: FlightQueryService = Depends(get_flight_service),
):
    """
    Fetches a list of options associated with a given flight.

    This asynchronous endpoint retrieves available options for a specific flight
    based on the provided flight ID. It queries the flight options through the
    FlightQueryService dependency and returns the options in a validated response
    model.

    :param flight_id: The unique identifier of the flight.
    :type flight_id: uuid.UUID
    :param svc: The FlightQueryService dependency providing flight query
        operations.
    :type svc: FlightQueryService
    :return: A list of validated option models representing the options available
        for the specified flight.
    :rtype: list[OptionOut]
    """
    options = await svc.options_for_flight(flight_id)
    return [OptionOut.model_validate(o) for o in options]


@router.get("/catalog/seat-types", response_model=list[SeatTypeOut])
async def list_seat_types(svc: FlightQueryService = Depends(get_flight_service)):
    """
    Retrieves a list of seat types available in the catalog.

    The function interacts with the `FlightQueryService` to fetch available
    seat types. It ensures the output model validation and returns a list
    of seat types.

    :param svc: The flight query service dependency that provides access
                to methods for fetching seat types from the catalog.
    :type svc: FlightQueryService
    :return: A list of validated seat type representations.
    :rtype: list[SeatTypeOut]
    """
    items = await svc.list_seat_types()
    return [SeatTypeOut.model_validate(x) for x in items]


@router.get("/catalog/discounts", response_model=list[DiscountOut])
async def list_discounts(svc: FlightQueryService = Depends(get_flight_service)):
    """
    Handles GET requests to retrieve a list of available discounts.

    This endpoint fetches all discounts by utilizing the provided
    FlightQueryService. The resulting data is validated against the
    DiscountOut schema before being returned in the response.

    :param svc: An instance of FlightQueryService, injected via dependency
        injection, used to fetch the list of discounts.
    :return: A list of validated DiscountOut objects.
    """
    items = await svc.list_discounts()
    return [DiscountOut.model_validate(x) for x in items]
