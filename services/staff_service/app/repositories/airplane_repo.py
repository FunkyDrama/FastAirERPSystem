import uuid
from collections.abc import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.staff_service.app.db.models.airplane import Airplane


class AirplaneRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_airplane(self, model: str, total_seats: int) -> Airplane:
        airplane = Airplane(
            airplane_id=uuid.uuid4(),
            model=model,
            total_seats=total_seats,
        )
        self.session.add(airplane)
        await self.session.flush()
        return airplane

    async def get_airplane(self, airplane_id: uuid.UUID) -> Airplane | None:
        res = await self.session.execute(
            select(Airplane).where(Airplane.airplane_id == airplane_id)
        )
        return res.scalar_one_or_none()

    async def list_airplanes(self) -> Sequence[Airplane]:
        res = await self.session.execute(select(Airplane))
        return res.scalars().all()

    async def delete_airplane(self, airplane_id: uuid.UUID) -> None:
        airplane = await self.get_airplane(airplane_id)
        if airplane:
            await self.session.delete(airplane)
            await self.session.flush()
