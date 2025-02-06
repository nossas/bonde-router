import datetime
import unittest.mock
import pytest

from traefik_api.api import app
from fastapi.testclient import TestClient
from http import HTTPStatus


@pytest.fixture
def client():
    return TestClient(app)


def test_status_code_return_healthcheck_200(client):
    """Testa código de status 200 para o endpoint /healthcheck"""
    response = client.get("/healthcheck")
    assert response.status_code == HTTPStatus.OK


def test_json_return_healthcheck(client):
    """Testa retorno JSON para o endpoint /healthcheck"""
    response = client.get("/healthcheck")
    assert response.headers["Content-Type"] == "application/json"


def test_json_format_healthcheck(client):
    """Testa formato de retorno JSON para o endpoint /healthcheck"""
    response = client.get("/healthcheck")
    assert response.json() == {"status": "ok"}


def test_traefik_router_create(client):
    """Testar criar uma rota no """
    response = client.post("/create-router", json={"service": "public", "domain_name": "test.custom.devel"})
    
    assert response.status_code == 201
    assert response.json() == {"status": "ok"}
