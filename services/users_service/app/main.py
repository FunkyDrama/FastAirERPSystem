import asyncio
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from services.users_service.app.core.config import redis_settings
from services.users_service.app.core.init_redis import init_redis, close_redis
from services.users_service.app.core.token_store import TokenStore
from services.users_service.app.db.base import (
    make_engine,
    make_sessionmaker,
    ping,
    close_engine,
)
from services.users_service.app.api import router as api_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Manages the lifespan of the FastAPI application, initializing and cleaning up
    resources such as the database engine, session maker, and authentication services.

    This function ensures the application starts up and shuts down gracefully,
    handling essential setup and teardown processes.

    :param app: The FastAPI application instance on which the resources will
        be initialized and managed.
    :return: An asynchronous generator yielding `None` during the application's
        lifespan.

    :raises RuntimeError: If the database engine ping test fails during startup.
    """

    engine = make_engine()
    sessionmaker = make_sessionmaker(engine)
    app.state.engine = engine
    app.state.sessionmaker = sessionmaker

    await ping(engine)
    await init_redis(app)
    app.state.token_store = TokenStore(
        app.state.redis, prefix=redis_settings.REDIS_PREFIX
    )

    try:
        yield
    finally:
        await close_engine(engine)
        await close_redis(app)


def create_app() -> FastAPI:
    """
    Creates and configures an instance of the FastAPI application.

    Attempts to initialize the `uvloop` event loop policy for better performance.
    If `uvloop` is unavailable, logs a warning and falls back to the default
    event loop policy. The application includes predefined routers for authentication
    and user management, as well as two default routes:

    - The root route ("/") that returns a simple status message.
    - A health-check route ("/health") that reports the service status as healthy.

    :return: The configured FastAPI application instance
    :rtype: FastAPI
    """
    try:
        import uvloop

        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    except Exception as e:
        logger.warning("uvloop is not active: %s", e)

    app = FastAPI(
        title="FastAir",
        description="API for airline management system",
        version="1.0.0",
        lifespan=lifespan,
        swagger_ui_parameters={"persistAuthorization": True},
    )
    origins = [
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router)

    @app.get("/")
    async def root() -> dict[str, str]:
        return {"message": "App is running"}

    @app.get("/health")
    async def health_check() -> dict[str, str]:
        return {"status": "healthy"}

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
    )
