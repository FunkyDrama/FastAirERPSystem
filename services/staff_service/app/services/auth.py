import asyncio
from datetime import datetime, timezone

import bcrypt
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from fastapi import Response

from services.staff_service.app.core.jwt import (
    create_access_token,
    create_refresh_token,
    decode_token_or_raise,
)
from services.staff_service.app.core.token_store import TokenStore
from services.staff_service.app.repositories.staff_repo import StaffUserRepository
from services.staff_service.app.schemas.auth import StaffUserLogin

REFRESH_COOKIE = "staff_refresh_token"
COOKIE_PATH = "/api/v1/staff/auth/refresh"
COOKIE_SAMESITE = "lax"
COOKIE_SECURE = True
COOKIE_HTTPONLY = True


class StaffAuthService:
    """
    StaffAuthService provides functionalities for managing user authentication and
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

    def __init__(
        self, sessionmaker: async_sessionmaker[AsyncSession], token_store: TokenStore
    ) -> None:
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

    async def login_user(self, staff_user_data: StaffUserLogin) -> dict[str, str]:
        try:
            async with self._sm() as session:
                repo = StaffUserRepository(session)
                staff_user = await repo.get_staff_by_email(str(staff_user_data.email))
                if not staff_user:
                    raise ValueError("Invalid email or password")

                ok = await self.verify_password(
                    staff_user_data.password, staff_user.password_hash
                )
                if not ok:
                    raise ValueError("Invalid email or password")
                access = create_access_token(
                    user_id=staff_user.user_id, role=staff_user.role.value
                )

                refresh = create_refresh_token(
                    user_id=staff_user.user_id, role=staff_user.role.value
                )

                a = decode_token_or_raise(access)
                r = decode_token_or_raise(refresh)

                await self._ts.allow("access", a["jti"], a["exp"])
                await self._ts.allow("refresh", r["jti"], r["exp"])

                return {
                    "email": staff_user.email,
                    "message": "Login successful",
                    "role": staff_user.role.value,
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
            repo = StaffUserRepository(session)
            staff_user = await repo.get_staff_by_id(uid)
            if not staff_user:
                raise ValueError("User not found")

            access = create_access_token(
                user_id=staff_user.user_id, role=staff_user.role.value
            )
            refresh = create_refresh_token(
                user_id=staff_user.user_id, role=staff_user.role.value
            )

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

    @staticmethod
    async def set_cookie(
        response: Response,
        token: str,
    ) -> None:
        payload = decode_token_or_raise(token)
        exp = int(payload["exp"])
        max_age = max(1, exp - int(datetime.now(timezone.utc).timestamp()))

        response.set_cookie(
            key=REFRESH_COOKIE,
            value=token,
            max_age=max_age,
            httponly=COOKIE_HTTPONLY,
            secure=COOKIE_SECURE,
            samesite=COOKIE_SAMESITE,
            path=COOKIE_PATH,
        )

    @staticmethod
    async def delete_cookie(response: Response) -> None:

        response.delete_cookie(
            key=REFRESH_COOKIE,
            path=COOKIE_PATH,
            httponly=COOKIE_HTTPONLY,
            secure=COOKIE_SECURE,
            samesite=COOKIE_SAMESITE,
        )
