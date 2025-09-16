import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.staff_service.app.db.models.staff_user import StaffUser


class StaffUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self) -> None:
        await self.session.commit()

    async def create_staff(self, staff_data: dict) -> StaffUser:
        staff_user = StaffUser(**staff_data)
        self.session.add(staff_user)
        await self.session.flush()
        return staff_user

    async def get_staff_by_id(self, staff_id: uuid.UUID) -> StaffUser | None:
        res = await self.session.execute(
            select(StaffUser).where(StaffUser.user_id == staff_id)
        )
        return res.scalar_one_or_none()

    async def get_staff_by_email(self, email: str) -> StaffUser | None:
        res = await self.session.execute(
            select(StaffUser).where(StaffUser.email == email)
        )
        return res.scalar_one_or_none()

    async def get_all_staff(self) -> Sequence[StaffUser]:
        res = await self.session.execute(select(StaffUser))
        return res.scalars().all()

    async def delete_staff(self, staff: StaffUser) -> None:
        await self.session.delete(staff)

    async def update_staff(self, staff: StaffUser, staff_data: dict) -> StaffUser:
        for key, value in staff_data.items():
            setattr(staff, key, value)
        await self.session.flush()
        return staff

    async def get_staff_by_role(self, role: str) -> Sequence[StaffUser]:
        res = await self.session.execute(
            select(StaffUser).where(StaffUser.role == role)
        )
        return res.scalars().all()
