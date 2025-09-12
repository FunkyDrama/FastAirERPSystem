import asyncio
from datetime import datetime, timezone
from urllib.parse import urlencode
import bcrypt
import httpx
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from fastapi import HTTPException
from fastapi.responses import RedirectResponse
from fastapi import Response

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
from services.users_service.app.core.config import google_auth_settings


REFRESH_COOKIE = "refresh_token"
COOKIE_PATH = "/"
COOKIE_SAMESITE = "lax"
COOKIE_SECURE = False
COOKIE_HTTPONLY = True


class AuthService:
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
                    raise ValueError("Invalid email or password")

                ok = await self.verify_password(user_data.password, user.password_hash)
                if not ok:
                    raise ValueError("Invalid email or password")
                access = create_access_token(user_id=user.user_id, role=user.role.value)

                refresh = create_refresh_token(
                    user_id=user.user_id, role=user.role.value
                )

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
                    raise ValueError("Current password is incorrect")

                new_hash = await self.hash_password(password_data.new_password)
                await repo.update_user(user, {"password_hash": new_hash})
                await repo.save()

                return {"email": email, "message": "Password changed successfully"}
        except Exception as e:
            raise RuntimeError(f"Password change failed: {e!s}")

    @staticmethod
    async def generate_google_auth_url() -> dict[str, str]:
        params = {
            "client_id": google_auth_settings.GOOGLE_CLIENT_ID,
            "redirect_uri": google_auth_settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "consent",
        }
        url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
        return {"url": url}

    async def handle_google_auth_callback(self, code: str) -> RedirectResponse:
        async with httpx.AsyncClient() as client:
            token_res = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": google_auth_settings.GOOGLE_CLIENT_ID,
                    "client_secret": google_auth_settings.GOOGLE_CLIENT_SECRET.get_secret_value(),
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": google_auth_settings.GOOGLE_REDIRECT_URI,
                },
            )
            token_res.raise_for_status()
            tokens = token_res.json()

        async with httpx.AsyncClient() as client:
            userinfo_res = await client.get(
                "https://www.googleapis.com/oauth2/v3/userinfo",
                headers={"Authorization": f"Bearer {tokens['access_token']}"},
            )
            userinfo_res.raise_for_status()
            profile = userinfo_res.json()
        email = profile.get("email")
        if not email:
            raise HTTPException(400, "Email not found from Google")
        async with self._sm() as session:
            repo = UserRepository(session)
            user = await repo.get_user_by_email(email)
            if not user:
                user = await repo.create_user(
                    {"email": email, "password_hash": "", "role": Role.CUSTOMER}
                )
                await repo.save()

        access = create_access_token(user_id=user.user_id, role=user.role.value)
        refresh = create_refresh_token(user_id=user.user_id, role=user.role.value)

        a = decode_token_or_raise(access)
        r = decode_token_or_raise(refresh)

        await self._ts.allow("access", a["jti"], a["exp"])
        await self._ts.allow("refresh", r["jti"], r["exp"])

        resp = RedirectResponse("http://localhost:5173/dashboard")
        await self.set_cookie(resp, refresh)
        return resp

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
