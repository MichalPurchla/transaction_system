import pytest


@pytest.fixture
def auth_client(client):
    client.defaults["HTTP_AUTHORIZATION"] = "Bearer 1a9b7f47c9454e4fb8d1e2aa9013f6d4"
    return client
