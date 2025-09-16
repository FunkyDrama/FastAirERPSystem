from contextlib import contextmanager, asynccontextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker, Session

from services.users_service.app.db.settings import db_settings as users_db_settings
from services.staff_service.app.db.settings import db_settings as staff_db_settings


class DatabaseManager:

    def get_engine(self, db_name: str):
        url = self._get_db_url(db_name, async_=True)
        return create_async_engine(
            url,
            future=True,
            echo=False,
            pool_pre_ping=True,
            pool_recycle=3600,
        )

    def get_sessionmaker(self, db_name: str) -> async_sessionmaker[AsyncSession]:
        engine = self.get_engine(db_name)
        return async_sessionmaker(engine, expire_on_commit=False)

    @asynccontextmanager
    async def get_session(self, db_name: str):
        engine = self.get_engine(db_name)
        sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
        try:
            async with sessionmaker() as session:
                yield session
        finally:
            await engine.dispose()

    def get_sync_engine(self, db_name: str):
        url = self._get_db_url(db_name, async_=False)
        return create_engine(
            url,
            future=True,
            echo=False,
            pool_pre_ping=True,
            pool_recycle=3600,
        )

    @contextmanager
    def get_sync_session(self, db_name: str):
        engine = self.get_sync_engine(db_name)
        SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, class_=Session)
        try:
            with SessionLocal() as session:
                yield session
        finally:
            engine.dispose()

    @staticmethod
    def _get_db_url(db_name: str, async_: bool = True) -> str:
        url_map = {
            "users": users_db_settings.DATABASE_URL,
            "staff": staff_db_settings.DATABASE_URL,
        }

        if db_name not in url_map:
            raise ValueError(f"Unknown database: {db_name}")

        url = url_map[db_name]
        if not url:
            raise ValueError(f"Database URL not set for: {db_name}")

        if async_:
            return url
        else:
            return url.replace("+asyncpg", "+psycopg2")

    async def ping(self, db_name: str) -> bool:
        try:
            engine = self.get_engine(db_name)
            try:
                async with engine.connect() as conn:
                    await conn.execute(text("SELECT 1"))
                return True
            finally:
                await engine.dispose()
        except Exception:
            return False


db_manager = DatabaseManager()
