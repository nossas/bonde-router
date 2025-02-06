import datetime
import unittest.mock
import pytest

from traefik_api.api import app
from fastapi.testclient import TestClient
from http import HTTPStatus


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_etcd_client():
    with unittest.mock.patch("etcd3.Client") as etcd_client:
        yield etcd_client


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
    """Testar retorno e código de status no endpoint /create-router"""
    response = client.post(
        "/create-router", json={"service": "public", "domain_name": "test.custom.devel"}
    )

    assert response.status_code == 201
    assert response.json() == {"status": "ok"}


def test_etcdclient_called_when_create_router(client, mock_etcd_client):
    """Testar chamada no client etcd para o endpoint /create-router"""
    mock_etcd = unittest.mock.MagicMock()
    mock_etcd_client.return_value = mock_etcd

    response = client.post(
        "/create-router", json={"service": "public", "domain_name": "test.custom.devel"}
    )

    mock_etcd.put.assert_called()
    assert mock_etcd.put.call_count == 5


def test_etcdclient_called_format_when_create_router(client, mock_etcd_client):
    """Testar chamada no metódo put do etcd para o endpoint /create-router"""
    mock_etcd = unittest.mock.MagicMock()
    mock_etcd_client.return_value = mock_etcd

    response = client.post(
        "/create-router", json={"service": "public", "domain_name": "test.custom.devel"}
    )

    mock_etcd.put.assert_any_call(
        "traefik/http/routers/test-custom-devel/entrypoints", "websecure"
    )
    mock_etcd.put.assert_any_call(
        "traefik/http/routers/test-custom-devel/rule",
        "Host(`test.custom.devel`) || Host(`www.test.custom.devel`)",
    )
    mock_etcd.put.assert_any_call(
        "traefik/http/routers/test-custom-devel/service", "public@docker"
    )
    mock_etcd.put.assert_any_call("traefik/http/routers/test-custom-devel/tls", "true")
    mock_etcd.put.assert_any_call(
        "traefik/http/routers/test-custom-devel/tls/certresolver", "myresolver"
    )


def test_traefik_router_delete(client):
    """Testar formato e código de status para o endpoint /delete-router"""
    response = client.delete("/delete-router/test.custom.devel")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_etcdclient_called_to_delete_router(client, mock_etcd_client):
    """Testar chamada no client etcd para o endpoint /delete-router"""
    mock_etcd = unittest.mock.MagicMock()
    mock_etcd_client.return_value = mock_etcd

    client.delete("/delete-router/test.custom.devel")

    mock_etcd.delete_range.assert_called()


def test_etcdclient_format_to_delete_router(client, mock_etcd_client):
    """Testar chamada no client etcd para o endpoint /delete-router"""
    mock_etcd = unittest.mock.MagicMock()
    mock_etcd_client.return_value = mock_etcd

    client.delete("/delete-router/test.custom.devel")

    mock_etcd.delete_range.assert_called_once_with(
        "traefik/http/routers/test-custom-devel", prefix=True
    )
