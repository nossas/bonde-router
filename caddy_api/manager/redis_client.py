from redis import StrictRedis

REDIS_HOST = "localhost"
REDIS_PORT = 6379

# Inicializar Redis
client = StrictRedis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)