import pytest
import unittest

from dns_api.api import app
from fastapi.testclient import TestClient
from http import HTTPStatus


@pytest.fixture
def client():
    return TestClient(app)


# @pytest.fixture
# def mock_db():
#     with unittest.mock.patch("tinydb.TinyDB") as mock_db:
#         yield mock_db


def test_status_code_return_hosted_zones_200(client):
    """Testa código de status 200 para o endpoint /hosted-zones"""
    response = client.get("/hosted-zones")
    assert response.status_code == HTTPStatus.OK


def test_json_return_hosted_zones(client):
    """Testa retorno JSON para o endpoint /hosted-zones"""
    response = client.get("/hosted-zones")
    assert response.headers["Content-Type"] == "application/json"


def test_json_format_hosted_zones(client):
    """Testa retorno JSON para o endpoint /hosted-zones"""
    # mock_db.search.return_value = []

    response = client.get("/hosted-zones")
    assert response.json() == {"hosted_zones": []}


def test_filter_list_hosted_zones(client):
    """Testa retorno lista com item quando encontra a tag"""
    # from dns_api.db import HostedZone

    # obj = HostedZone()
    # obj.db.insert_multiple([
    #     {
    #         "id": "zzz",
    #         "name": "zzz.com.",
    #         "caller_reference": "8CFFEB3C-FD1B-E00D-877A-9F5DE7D079A0",
    #         "tags": [{"ExternalGroupId": "1"}],
    #         "last_sync_on": "2025-02-04T16:32:00.600970",
    #     },
    #     {
    #         "id": "aaa",
    #         "name": "aaa.com.",
    #         "caller_reference": "",
    #         "tags": [{"ExternalGroupId": "2"}],
    #         "last_sync_on": "",
    #     },
    # ])

    response = client.get("/hosted-zones?external_group_id=1")
    assert len(response.json().get("hosted_zones")) == 1


def test_filter_list_hosted_zones_fail(client):
    """Testa retorno lista vazia quando não encontra a tag"""
    response = client.get("/hosted-zones?external_group_id=2")
    assert len(response.json().get("hosted_zones")) == 0
