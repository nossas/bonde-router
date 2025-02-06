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
    return {"status": "ok"}