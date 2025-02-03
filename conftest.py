from functools import wraps
import pytest

from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from httpx import AsyncClient
from moto import mock_aws


@pytest.fixture(autouse=True)
def mock_aws_services():
    # Ativa o mock para o Route53 (ou outros serviços AWS que você está usando)
    with mock_aws():
        # O mock permanece ativo durante o teste
        yield

from unittest import mock

def mock_cache(*args, **kwargs):
    def wrapper(func):
        @wraps(func)
        async def inner(*args, **kwargs):
            return await func(*args, **kwargs)
        return inner
    return wrapper

mock.patch("fastapi_cache.decorator.cache", mock_cache).start()    


@pytest.fixture(scope="module")
async def client():
    from dns_api.api import app # need to load app module after mock. otherwise, it would fail
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client