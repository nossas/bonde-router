import pytest

from dns_api.api import app
from fastapi.testclient import TestClient
from http import HTTPStatus


@pytest.fixture
def client():
    return TestClient(app)


def test_status_code_return_healthcheck_200(client):
    response = client.get("/healthcheck")
    assert response.status_code == HTTPStatus.OK


def test_json_return_healthcheck(client):
    response = client.get("/healthcheck")
    assert response.headers["Content-Type"] == "application/json"


def test_json_format_healthcheck(client):
    response = client.get("/healthcheck")
    assert response.json() == {"status": "ok"}
