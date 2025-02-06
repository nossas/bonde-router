import etcd3

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import asyncio as aioredis

from traefik_api.models import Router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}


@app.post("/create-router", status_code=status.HTTP_201_CREATED)
async def create_router(router: Router):
    client = etcd3.Client("127.0.0.1", 2379)

    router_key_name = router.domain_name.replace(".", "-")
    router_config_values = {
        "/entrypoints": "websecure",
        "/rule": f"Host(`{router.domain_name}`) || Host(`www.{router.domain_name}`)",
        "/service": f"{router.service}@docker",
        "/tls": "true",
        "/tls/certresolver": "myresolver",
    }
    
    for config_key_name, value in router_config_values.items():
        client.put(f"traefik/http/routers/{router_key_name}{config_key_name}", value)
    
    return {"status": "ok"}

@app.delete("/delete-router/{domain_name}")
async def delete_router(domain_name: str):
    client = etcd3.Client("127.0.0.1", 2379)

    router_key_name = domain_name.replace(".", "-")
    client.delete_range(f"traefik/http/routers/{router_key_name}", prefix=True)

    return {"status": "ok"}

# etcdctl put traefik/http/routers/foraderrite-org/entrypoints "websecure"
# etcdctl put traefik/http/routers/foraderrite-org/rule "HostRegexp(\`((www\.)?([a-z0-9-]+\.)?foraderrite\.(org))$\`)"
# etcdctl put traefik/http/routers/foraderrite-org/service "public@docker"
# etcdctl put traefik/http/routers/foraderrite-org/tls "true"
# etcdctl put traefik/http/routers/foraderrite-org/tls/certresolver "myresolver"
