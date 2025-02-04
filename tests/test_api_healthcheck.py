import datetime
import unittest.mock
import pytest

from dns_api.api import app
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
    with unittest.mock.patch("tinydb.TinyDB") as mock_db:
        expected_value = [
            {
                "sync_name": "sync_hosted_zones",
                "updated_on": datetime.datetime.now().isoformat(),
            }
        ]
        mock_db.return_value.all.return_value = expected_value

        response = client.get("/healthcheck")

        assert response.json() == {"status": "ok", "checks": expected_value}
