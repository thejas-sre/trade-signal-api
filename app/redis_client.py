import redis
import os
import logging

logger = logging.getLogger(__name__)

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_POOL_SIZE = int(os.getenv("REDIS_POOL_SIZE", 20))
SIGNAL_TTL = int(os.getenv("SIGNAL_TTL", 60))

pool = redis.ConnectionPool(
    host=REDIS_HOST,
    port=REDIS_PORT,
    max_connections=REDIS_POOL_SIZE,
    decode_responses=True
)

def get_client() -> redis.Redis:
    return redis.Redis(connection_pool=pool)

def set_signal(signal_id: str, payload: dict) -> bool:
    try:
        client = get_client()
        client.setex(signal_id, SIGNAL_TTL, str(payload))
        return True
    except redis.RedisError as e:
        logger.error(f"Redis SET failed: {e}")
        return False

def get_signal(signal_id: str) -> dict | None:
    try:
        client = get_client()
        data = client.get(signal_id)
        if data:
            return eval(data)
        return None
    except redis.RedisError as e:
        logger.error(f"Redis GET failed: {e}")
        return None

def batch_get(signal_ids: list) -> list:
    try:
        client = get_client()
        pipe = client.pipeline()
        for sid in signal_ids:
            pipe.get(sid)
        results = pipe.execute()
        return [eval(r) if r else None for r in results]
    except redis.RedisError as e:
        logger.error(f"Redis batch GET failed: {e}")
        return []

def is_connected() -> bool:
    try:
        get_client().ping()
        return True
    except redis.RedisError:
        return False
