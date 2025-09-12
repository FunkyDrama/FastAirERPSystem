import redis.asyncio as redis
from fastapi import FastAPI
from .config import redis_settings


async def init_redis(app: FastAPI) -> None:
    """
    Initializes a Redis connection and sets it in the FastAPI application state.

    This asynchronous function connects to a Redis database using a URL specified
    in the application's settings. After successfully establishing the connection,
    it performs a health check by sending a 'PING' command. The connection is then
    stored in the FastAPI application state for shared use across the application
    lifecycle.

    :param app: FastAPI application instance to which the Redis connection
        will be bound.
    :type app: FastAPI
    :return: None
    """
    app.state.redis = redis.from_url(redis_settings.REDIS_URL, decode_responses=True)
    await app.state.redis.ping()


async def close_redis(app: FastAPI) -> None:
    """
    Close the Redis connection stored in the FastAPI application state.

    This function is responsible for cleaning up the Redis client instance
    stored in the application state. It retrieves the Redis instance, if it
    exists, and closes the connection gracefully. It is typically used during
    the shutdown of the application to ensure all resources are properly released.

    :param app: FastAPI application instance containing the Redis connection in its state.
    :type app: FastAPI
    :return: None
    :rtype: None
    """
    r = getattr(app.state, "redis", None)
    if r:
        await r.aclose()
