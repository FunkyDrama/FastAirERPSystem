import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from services.users_service.app.db.models.user import UserAccount


class UserRepository:
    """
    Handles interactions with the database for user-related operations.

    This repository class is responsible for managing database interactions for
    user entities, including saving, creating, updating, deleting, and retrieving
    user data. It uses an asynchronous session for these operations and provides
    a way to handle all user-related persistence logic.

    :ivar session: The asynchronous database session used for executing and
        committing queries.
    :type session: AsyncSession
    """
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self) -> None:
        await self.session.commit()

    async def get_user_by_email(self, email: str) -> UserAccount | None:
        res = await self.session.execute(
            select(UserAccount).where(UserAccount.email == email)
        )
        return res.scalar_one_or_none()

    async def get_user_by_id(self, user_id: uuid.UUID) -> UserAccount | None:
        res = await self.session.execute(
            select(UserAccount).where(UserAccount.user_id == user_id)
        )
        return res.scalar_one_or_none()

    async def create_user(self, user_data: dict) -> UserAccount:
        user = UserAccount(**user_data)
        self.session.add(user)
        await self.session.flush()
        return user

    async def update_user(self, user: UserAccount, user_data: dict) -> UserAccount:
        for key, value in user_data.items():
            setattr(user, key, value)
        await self.session.flush()
        return user

    async def delete_user(self, user: UserAccount) -> None:
        await self.session.delete(user)

    async def get_all_users(self) -> Sequence[UserAccount]:
        result = await self.session.execute(select(UserAccount))
        return result.scalars().all()
