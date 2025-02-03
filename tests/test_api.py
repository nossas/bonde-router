import boto3
import pytest
import datetime

from dns_api.api import app
from fastapi.testclient import TestClient
from http import HTTPStatus


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def create_hosted_zone():
    name = "testdomain.devel"
    caller_reference = datetime.datetime.now().isoformat()
    payload = {"Name": name, "CallerReference": caller_reference}

    response = boto3.client("route53").create_hosted_zone(**payload)

    yield {
        "CallerReference": response.get("HostedZone").get("CallerReference"),
        "Config": {"PrivateZone": False},
        "Id": response.get("HostedZone").get("Id"),
        "Name": response.get("HostedZone").get("Name"),
        "ResourceRecordSetCount": response.get("HostedZone").get(
            "ResourceRecordSetCount"
        ),
    }


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


def test_status_code_return_hosted_zones_200(client):
    """Testa código de status 200 para o endpoint /hosted-zones"""
    response = client.get("/hosted-zones")
    assert response.status_code == HTTPStatus.OK


def test_json_return_hosted_zones(client):
    """Testa retorno JSON para o endpoint /hosted-zones"""
    response = client.get("/hosted-zones")
    assert response.headers["Content-Type"] == "application/json"


def test_json_format_hosted_zones(client, create_hosted_zone):
    """Testa retorno JSON para o endpoint /hosted-zones"""
    response = client.get("/hosted-zones")
    assert response.json() == {"hosted_zones": [create_hosted_zone]}


def test_call_boto3_to_list_hosted_zones(client, create_hosted_zone):
    """Testa chamada da lib boto3 para listar Zonas de Hospedagem"""
    response = client.get("/hosted-zones")
    assert len(response.json().get("hosted_zones")) == 1
