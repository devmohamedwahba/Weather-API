import json
import logging
from redis import Redis
from app.core.config import config

logger = logging.getLogger(__name__)


class CacheService:
    def __init__(self, url: str = config.REDIS_URL, ttl: int = config.CACHE_TTL):
        self.ttl = ttl
        self._redis = Redis.from_url(url, decode_responses=True)

    def get(self, key: str) -> dict | None:
        try:
            data = self._redis.get(key)
            if data:
                logger.info(f"Cache hit: {key}")
                return json.loads(data)
            logger.info(f"Cache miss: {key}")
        except Exception as e:
            logger.warning(f"Redis get failed: {e}")
        return None

    def set(self, key: str, value: dict, ttl: int | None = None) -> None:
        try:
            self._redis.setex(key, ttl or self.ttl, json.dumps(value))
            logger.info(f"Cache set: {key} (ttl={ttl or self.ttl}s)")
        except Exception as e:
            logger.warning(f"Redis set failed: {e}")

    def delete(self, key: str) -> None:
        try:
            self._redis.delete(key)
            logger.info(f"Cache deleted: {key}")
        except Exception as e:
            logger.warning(f"Redis delete failed: {e}")


cache = CacheService()
