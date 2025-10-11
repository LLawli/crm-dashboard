import redis
from src.config import REDIS_DB, REDIS_HOST, REDIS_PORT
import hashlib
import json

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

def cache_get(key: str):
    cached = r.get(key)
    if cached:
        return json.loads(cached)
    return None

def cache_set(key: str, value, expire: int = 3600):
    r.set(key, json.dumps(value), ex=expire)

def generate_cache_key(**kwargs):
    key_string = json.dumps(kwargs, sort_keys=True)
    return hashlib.md5(key_string.encode("utf-8")).hexdigest()