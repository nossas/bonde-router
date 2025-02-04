from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dns_api.route53 import Route53Client
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import asyncio as aioredis


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/healthcheck")
async def healthcheck():
    from dns_api.db import Healthcheck

    healthcheck_db = Healthcheck()
    return {"status": "ok", "checks": healthcheck_db.db.all()}


@app.get("/hosted-zones")
@cache(expire=60)
async def hosted_zones(external_group_id: str | None = None):
    hosted_zones = Route53Client().list_hosted_zones(
        external_group_id=external_group_id
    )
    return {"hosted_zones": hosted_zones}
