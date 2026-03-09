"""Tests for client factory."""

import pytest

from orb_cloud_mcp.client import get_client


def test_get_client_returns_client(set_api_key):
    client = get_client()
    assert client is not None


def test_get_client_missing_key(monkeypatch):
    monkeypatch.delenv("ORB_CLOUD_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="ORB_CLOUD_API_KEY"):
        get_client()


def test_get_client_uses_env_token(monkeypatch):
    monkeypatch.setenv("ORB_CLOUD_API_KEY", "my-secret-token")
    client = get_client()
    assert "Bearer my-secret-token" in client.headers.get("Authorization", "")
