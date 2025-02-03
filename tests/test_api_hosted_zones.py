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

    payload = {
        "ResourceType": "hostedzone",
        "ResourceId": response.get("HostedZone").get("Id").split("/")[-1],
        "AddTags": [{"Key": "ExternalGroupId", "Value": "1"}]
    }
    boto3.client("route53").change_tags_for_resource(**payload)

    yield {
        "CallerReference": response.get("HostedZone").get("CallerReference"),
        "Config": {"PrivateZone": False},
        "Id": response.get("HostedZone").get("Id"),
        "Name": response.get("HostedZone").get("Name"),
        "ResourceRecordSetCount": response.get("HostedZone").get(
            "ResourceRecordSetCount"
        ),
    }

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
    assert response.json() == {"hosted_zones": []}


def test_filter_list_hosted_zones(client, create_hosted_zone):
    """Testa retorno lista com item quando encontra a tag"""
    response = client.get("/hosted-zones?external_group_id=1")
    assert len(response.json().get("hosted_zones")) == 1


def test_filter_list_hosted_zones_fail(client, create_hosted_zone):
    """Testa retorno lista vazia quando não encontra a tag"""
    response = client.get("/hosted-zones?external_group_id=2")
    assert len(response.json().get("hosted_zones")) == 0