from datetime import datetime, timezone
from typing import Literal
from redis.asyncio import Redis

KeyType = Literal["access", "refresh"]


class TokenStore:
    """
    Manages token storage for validation and revocation.

    This class provides methods to allow, validate the allowance of, and revoke
    tokens using a Redis backend. It creates keys using a prefix and stores tokens
    with a time-to-live (TTL) for invalidation after a specific expiration time.

    :ivar r: Redis connection instance used for token operations.
    :type r: Redis
    :ivar prefix: Prefix used in the token keys stored in Redis. Default is 'auth'.
    :type prefix: str
    """

    def __init__(self, redis: Redis, prefix: str = "staff_auth"):
        self.r = redis
        self.prefix = prefix

    def _key(self, typ: str, jti: str) -> str:
        return f"{self.prefix}:{typ}:{jti}"

    async def allow(self, typ: str, jti: str, exp_ts: int) -> None:
        now = int(datetime.now(timezone.utc).timestamp())
        ttl = max(1, int(exp_ts) - now)
        await self.r.setex(self._key(typ, jti), ttl, "1")

    async def is_allowed(self, typ: str, jti: str) -> bool:
        return await self.r.exists(self._key(typ, jti)) == 1

    async def revoke(self, typ: str, jti: str) -> None:
        await self.r.delete(self._key(typ, jti))
