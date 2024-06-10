import redis

from core.config.settings import REDIS_CONN_STR


class CacheConnector():

    def __init__(self):
        self.cache_connector = redis.Redis(
            host=REDIS_CONN_STR,
            port=6379,
            charset="utf-8",
            decode_responses=True
        )

        self.cache_connector_byte = redis.Redis(
            host=REDIS_CONN_STR,
            port=6379,
            decode_responses=False
        )


    def set(self, key, volume, exp_time):
        self.cache_connector.set(key, volume, exp_time)

    def get(self, key):
        return self.cache_connector.get(key)

    def delete(self, key):
        self.cache_connector.delete(key)

    def set_b(self, key, volume, exp_time):
        self.cache_connector_byte.set(key, volume, exp_time)

    def get_b(self, key):
        return self.cache_connector_byte.get(key)

    def delete_b(self, key):
        self.cache_connector_byte.delete(key)
