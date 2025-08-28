import datetime as dt
import uuid
from collections.abc import Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from services.users_service.app.repositories.flight_repo import FlightRepository
from services.users_service.app.repositories.catalog_repo import CatalogRepository
from services.users_service.app.db.models.flight_ref import FlightRef


class FlightQueryService:
    """
    Handles flight-related queries and operations.

    Provides methods to search for flights, retrieve flight details, and list
    various catalog options such as seat types, discounts, and flight-specific
    options.

    :ivar session: The asynchronous database session used for querying.
    :type session: AsyncSession
    :ivar flights: Repository for performing flight-related database operations.
    :type flights: FlightRepository
    :ivar catalog: Repository for retrieving catalog-related information.
    :type catalog: CatalogRepository
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.flights = FlightRepository(session)
        self.catalog = CatalogRepository(session)

    async def search(
        self,
        *,
        origin: str | None,
        destination: str | None,
        date: dt.date | None,
        passengers: int,
        limit: int,
        offset: int,
    ) -> Sequence[FlightRef]:
        return await self.flights.search(
            origin=origin,
            destination=destination,
            date=date,
            passengers=passengers,
            limit=limit,
            offset=offset,
        )

    async def get_flight(self, flight_id: uuid.UUID) -> FlightRef | None:
        return await self.flights.get_flight_by_id(flight_id)

    async def options_for_flight(self, flight_id: uuid.UUID):
        return await self.catalog.list_options()

    async def list_seat_types(self):
        return await self.catalog.list_seat_types()

    async def list_discounts(self):
        return await self.catalog.list_discounts()
