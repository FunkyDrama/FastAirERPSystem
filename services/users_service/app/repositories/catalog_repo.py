from collections.abc import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.users_service.app.db.models.option import Option
from services.users_service.app.db.models.seat_type import SeatType
from services.users_service.app.db.models.discount import Discount


class CatalogRepository:
    """
    Repository class for handling operations related to catalog entities.

    This class provides methods to interact with the database asynchronously for
    retrieving lists of various catalog-related entities such as options, seat
    types, and discounts. It serves as the data access layer and abstracts execution
    of SQLAlchemy queries.

    :ivar session: The asynchronous database session used for executing SQL queries.
    :type session: AsyncSession
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_options(self) -> Sequence[Option]:
        res = await self.session.execute(select(Option).order_by(Option.name))
        return res.scalars().all()

    async def list_seat_types(self) -> Sequence[SeatType]:
        res = await self.session.execute(select(SeatType).order_by(SeatType.type_name))
        return res.scalars().all()

    async def list_discounts(self) -> Sequence[Discount]:
        res = await self.session.execute(
            select(Discount).order_by(Discount.discount_code)
        )
        return res.scalars().all()
