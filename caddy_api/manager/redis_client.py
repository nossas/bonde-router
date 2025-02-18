from redis import StrictRedis

from caddy_api import settings


# Inicializar Redis
client = StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)