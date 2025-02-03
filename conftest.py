import pytest

from moto import mock_aws


@pytest.fixture(autouse=True)
def mock_aws_services():
    # Ativa o mock para o Route53 (ou outros serviços AWS que você está usando)
    with mock_aws():
        # O mock permanece ativo durante o teste
        yield