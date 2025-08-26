import asyncio

import bcrypt

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from services.users_service.app.db.models.user import Role
from services.users_service.app.repositories.user_repo import UserRepository
from services.users_service.app.schemas.auth import (
    UserLogin,
    PasswordChange,
    UserRegistration,
)

from services.users_service.app.core.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token_or_raise,
)
from services.users_service.app.core.token_store import TokenStore


class AuthService:
    """
    AuthService provides functionalities for managing user authentication and
    authorization tasks within the system.

    This class includes several methods to handle user registration, login, token
    management, logout, and password modification. It is designed to work with an
    asynchronous context and utilizes session management and token handling for
    its operations.

    :ivar _sm: A factory function for creating asynchronous database
        sessions. Used to interact with the database during authentication
        operations.
    :type _sm: async_sessionmaker[AsyncSession]

    :ivar _ts: A storage engine for managing issued access and refresh
        tokens. Responsible for maintaining token validity and ensuring proper
        authorization.
    :type token_store: TokenStore
    """

    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession], token_store: TokenStore) -> None:
        self._sm = sessionmaker
        self._ts = token_store

    @staticmethod
    async def hash_password(password: str) -> str:
        try:

            def _hash() -> str:
                return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode(
                    "utf-8"
                )

            return await asyncio.to_thread(_hash)
        except Exception as e:
            raise ValueError(f"Error hashing password: {e!s}")

    @staticmethod
    async def verify_password(password: str, hashed: str) -> bool:
        try:

            def _check() -> bool:
                return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

            return await asyncio.to_thread(_check)
        except Exception as e:
            raise ValueError(f"Error verifying password: {e!s}")

    async def register_user(self, user_data: UserRegistration) -> dict[str, str]:
        try:
            async with self._sm() as session:
                repo = UserRepository(session)
                user = await repo.get_user_by_email(str(user_data.email))
                if user:
                    raise ValueError(
                        f"User with email {user_data.email} already exists"
                    )

                hashed = await self.hash_password(user_data.password)

                await repo.create_user(
                    {
                        "email": user_data.email,
                        "password_hash": hashed,
                        "role": Role.CUSTOMER,
                    }
                )
                await repo.save()
                return {
                    "email": user_data.email,
                    "message": "User registered successfully",
                }
        except Exception as e:
            raise RuntimeError(f"Registration failed: {e!s}")

    async def login_user(self, user_data: UserLogin) -> dict[str, str]:
        try:
            async with self._sm() as session:
                repo = UserRepository(session)
                user = await repo.get_user_by_email(str(user_data.email))
                if not user:
                    raise ValueError(
                        "Invalid email or password"
                    )

                ok = await self.verify_password(user_data.password, user.password_hash)
                if not ok:
                    raise ValueError(
                        "Invalid email or password"
                    )
                access = create_access_token(
                    user_id=user.user_id, role=user.role.value)

                refresh = create_refresh_token(
                    user_id=user.user_id, role=user.role.value)

                a = decode_token_or_raise(access)
                r = decode_token_or_raise(refresh)

                await self._ts.allow("access", a["jti"], a["exp"])
                await self._ts.allow("refresh", r["jti"], r["exp"])

                return {
                    "email": user.email,
                    "message": "Login successful",
                    "access_token": access,
                    "refresh_token": refresh,
                    "token_type": "bearer",
                }
        except Exception as e:
            raise ValueError(f"Login failed: {e!s}")


    async def refresh_tokens(self, refresh_token: str) -> dict[str, str]:
        try:
            payload = decode_token_or_raise(refresh_token)
        except Exception:
            raise ValueError("Invalid refresh token")

        if payload.get("typ") != "refresh":
            raise ValueError("Invalid refresh token")

        uid = payload.get("sub")
        jti = payload.get("jti")
        if not uid or not jti:
            raise ValueError("Invalid refresh token")

        allowed = await self._ts.is_allowed("refresh", jti)
        if not allowed:
            raise ValueError("Invalid refresh token")

        await self._ts.revoke("refresh", jti)

        async with self._sm() as session:
            repo = UserRepository(session)
            user = await repo.get_user_by_id(uid)
            if not user:
                raise ValueError("User not found")

            access = create_access_token(user_id=user.user_id, role=user.role.value)
            refresh = create_refresh_token(user_id=user.user_id, role=user.role.value)

            try:
                a = decode_token_or_raise(access)
                r = decode_token_or_raise(refresh)
            except Exception:
                raise RuntimeError("Failed to issue tokens")

            await self._ts.allow("access", a["jti"], a["exp"])
            await self._ts.allow("refresh", r["jti"], r["exp"])

            return {
                "access_token": access,
                "refresh_token": refresh,
                "token_type": "bearer",
            }

    async def logout_user(
        self,
        email: str,
        *,
        access_token: str | None = None,
        refresh_token: str | None = None,
    ) -> dict[str, str]:
        for raw in (access_token, refresh_token):
            if not raw:
                continue
            try:
                p = decode_token_or_raise(raw)
                typ = p.get("typ")
                jti = p.get("jti")
                if typ in ("access", "refresh") and jti:
                    await self._ts.revoke(typ, jti)
            except Exception:
                pass

        return {"email": email, "message": "Logout successful"}

    async def change_password(
        self, email: str, password_data: PasswordChange
    ) -> dict[str, str]:
        try:
            async with self._sm() as session:
                repo = UserRepository(session)
                user = await repo.get_user_by_email(email)
                if not user:
                    raise ValueError("User not found")

                ok = await self.verify_password(
                    password_data.current_password, user.password_hash
                )
                if not ok:
                    raise ValueError(
                        "Current password is incorrect"
                    )

                new_hash = await self.hash_password(password_data.new_password)
                await repo.update_user(user, {"password_hash": new_hash})
                await repo.save()

                return {"email": email, "message": "Password changed successfully"}
        except Exception as e:
            raise RuntimeError(f"Password change failed: {e!s}")
    #
    # async def list_users(
    #     self,
    #     *,
    #     id: int | None = None,
    #     first_name: str | None = None,
    #     last_name: str | None = None,
    #     is_blocked: bool | None = None,
    #     sort: Iterable[str] = (),
    # ) -> list[User]:
    #     async with self._sm() as session:
    #         stmt = select(User).where(User.deleted_at.is_(None))
    #         if id is not None:
    #             stmt = stmt.where(User.id == id)
    #         if first_name is not None:
    #             stmt = stmt.where(User.first_name == first_name)
    #         if last_name is not None:
    #             stmt = stmt.where(User.last_name == last_name)
    #         if is_blocked is not None:
    #             stmt = stmt.where(User.is_blocked == is_blocked)
    #
    #         sortmap = {
    #             "id": User.id,
    #             "balance": User.balance,
    #             "last_activity_at": User.last_activity_at,
    #         }
    #
    #         order_clauses = []
    #         for token in sort:
    #             if not token:
    #                 continue
    #             t = token.strip().lower()
    #
    #             if ":" in t:
    #                 field, direction = t.split(":", 1)
    #             else:
    #                 if t in ("asc", "desc"):
    #                     field, direction = "id", t
    #                 else:
    #                     field, direction = t, "asc"
    #
    #             col = sortmap.get(field)
    #             if not col or direction not in ("asc", "desc"):
    #                 continue
    #             order_clauses.append(asc(col) if direction == "asc" else desc(col))
    #
    #         if order_clauses:
    #             stmt = stmt.order_by(*order_clauses)
    #
    #         result = await session.scalars(stmt)
    #         return list(result.all())
    #
    # async def get_profile(self, user_id: int) -> User:
    #     async with self._sm() as session:
    #         user = await session.scalar(
    #             select(User).where(User.id == user_id, User.deleted_at.is_(None))
    #         )
    #         if not user:
    #             raise auth_exc.UserNotFoundException("User not found")
    #         if not user.first_name or not user.last_name:
    #             raise auth_exc.ForbiddenException(
    #                 "Profile is available only if first_name and last_name exist"
    #             )
    #         return user
    #
    # async def update_balance(
    #     self, user_id: int, *, amount: int, op: str
    # ) -> tuple[int, int]:
    #     async with self._sm() as session:
    #         res = await session.execute(
    #             select(User)
    #             .where(User.id == user_id, User.deleted_at.is_(None))
    #             .with_for_update(of=User)
    #         )
    #         user = res.scalar_one_or_none()
    #         if not user:
    #             raise auth_exc.UserNotFoundException("User not found")
    #         if getattr(user, "role", "user") == "admin":
    #             raise auth_exc.ForbiddenException("Admins cannot have balance")
    #         if not user.first_name or not user.last_name:
    #             raise auth_exc.ForbiddenException(
    #                 "Balance is available only if first_name and last_name exist"
    #             )
    #
    #         if op == "set":
    #             new_balance = amount
    #         elif op == "withdraw":
    #             new_balance = user.balance - amount
    #         elif op == "deposit":
    #             new_balance = user.balance + amount
    #         else:
    #             raise auth_exc.AuthException("Unsupported operation")
    #
    #         if new_balance < 0:
    #             raise auth_exc.ForbiddenException("Balance cannot be negative")
    #
    #         await session.execute(
    #             update(User)
    #             .where(User.id == user_id)
    #             .values(balance=new_balance, updated_at=func.now())
    #         )
    #         await session.commit()
    #
    #     return int(user.id), int(new_balance)
