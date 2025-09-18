import os
from typing import Optional

import redis
from dotenv import load_dotenv

load_dotenv()


class RedisClient:

    def __init__(self):
        self._client = redis.Redis(
            host=os.environ.get('REDIS_HOST'),
            port=int(os.environ.get('REDIS_PORT')),
            db=int(os.environ.get('REDIS_DB'))
        )

    def lpush(self, name, values):
        self._client.lpush(name, values)

    def brpop(self, keys, timeout):
        msg = self._client.brpop(keys, timeout)
        return msg

    def hset(self,
             name: str,
             key: Optional[str] = None,
             value: Optional[str] = None,
             mapping: Optional[dict] = None,
             items: Optional[list] = None,
             expire: int = 3600):
        self._client.hset(
            name=name,
            key=key,
            value=value,
            mapping=mapping,
            items=items
        )
        self._client.expire(name, expire, nx=True)

    def hmget(self, key, key_list):
        ans = {}
        data = self._client.hmget(key, key_list)
        for key_dict, value in zip(key_list, data):
            if isinstance(value, bytes):
                value = value.decode()
            if value and value.isdigit():
                value = int(value)
            ans[key_dict] = value
        return ans

    def close(self):
        self._client.close()
