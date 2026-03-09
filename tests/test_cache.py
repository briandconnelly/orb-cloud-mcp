"""Tests for caching behaviour in list_organizations and list_devices."""

import httpx
import pytest

import orb_cloud_mcp.cache as cache_module
from orb_cloud_mcp.tools.devices import list_devices
from orb_cloud_mcp.tools.organizations import list_organizations
from tests.conftest import DEVICE_PAYLOAD, ORG_PAYLOAD


# ---------------------------------------------------------------------------
# list_organizations caching
# ---------------------------------------------------------------------------


async def test_list_organizations_cached_on_second_call(respx_mock):
    route = respx_mock.get("/api/v2/organizations").mock(
        return_value=httpx.Response(200, json=ORG_PAYLOAD)
    )

    await list_organizations()
    await list_organizations()

    assert route.call_count == 1


async def test_list_organizations_cache_keyed_by_token(respx_mock, monkeypatch):
    respx_mock.get("/api/v2/organizations").mock(
        return_value=httpx.Response(200, json=ORG_PAYLOAD)
    )

    monkeypatch.setenv("ORB_CLOUD_API_KEY", "token-a")
    await list_organizations()

    monkeypatch.setenv("ORB_CLOUD_API_KEY", "token-b")
    await list_organizations()

    assert len(cache_module.cache) == 2


async def test_list_organizations_cache_miss_after_clear(respx_mock):
    route = respx_mock.get("/api/v2/organizations").mock(
        return_value=httpx.Response(200, json=ORG_PAYLOAD)
    )

    await list_organizations()
    cache_module.cache.clear()
    await list_organizations()

    assert route.call_count == 2


# ---------------------------------------------------------------------------
# list_devices caching
# ---------------------------------------------------------------------------


async def test_list_devices_cached_on_second_call(respx_mock):
    route = respx_mock.get("/api/v2/organization/org-123/devices").mock(
        return_value=httpx.Response(200, json=DEVICE_PAYLOAD)
    )

    await list_devices("org-123")
    await list_devices("org-123")

    assert route.call_count == 1


async def test_list_devices_cache_keyed_by_org(respx_mock):
    respx_mock.get("/api/v2/organization/org-123/devices").mock(
        return_value=httpx.Response(200, json=DEVICE_PAYLOAD)
    )
    respx_mock.get("/api/v2/organization/org-456/devices").mock(
        return_value=httpx.Response(200, json=DEVICE_PAYLOAD)
    )

    await list_devices("org-123")
    await list_devices("org-456")

    assert len(cache_module.cache) == 2


async def test_list_devices_cache_keyed_by_token(respx_mock, monkeypatch):
    respx_mock.get("/api/v2/organization/org-123/devices").mock(
        return_value=httpx.Response(200, json=DEVICE_PAYLOAD)
    )

    monkeypatch.setenv("ORB_CLOUD_API_KEY", "token-a")
    await list_devices("org-123")

    monkeypatch.setenv("ORB_CLOUD_API_KEY", "token-b")
    await list_devices("org-123")

    assert len(cache_module.cache) == 2


async def test_list_devices_cache_miss_after_clear(respx_mock):
    route = respx_mock.get("/api/v2/organization/org-123/devices").mock(
        return_value=httpx.Response(200, json=DEVICE_PAYLOAD)
    )

    await list_devices("org-123")
    cache_module.cache.clear()
    await list_devices("org-123")

    assert route.call_count == 2


# ---------------------------------------------------------------------------
# get_device_telemetry — must NOT be cached
# ---------------------------------------------------------------------------


async def test_get_device_telemetry_not_cached(respx_mock):
    from orb_cloud_mcp.tools.devices import get_device_telemetry

    route = respx_mock.get("/api/v2/organization/org-123/devices").mock(
        return_value=httpx.Response(200, json=DEVICE_PAYLOAD)
    )

    await get_device_telemetry("org-123")
    await get_device_telemetry("org-123")

    assert route.call_count == 2
    assert len(cache_module.cache) == 0


# ---------------------------------------------------------------------------
# ORB_CLOUD_CACHE_TTL configuration
# ---------------------------------------------------------------------------


def test_cache_ttl_default():
    import orb_cloud_mcp.cache as m
    assert m._DEFAULT_TTL == 300


def test_cache_ttl_from_env(monkeypatch):
    monkeypatch.setenv("ORB_CLOUD_CACHE_TTL", "60")
    assert cache_module._ttl() == 60


def test_cache_ttl_default_when_unset(monkeypatch):
    monkeypatch.delenv("ORB_CLOUD_CACHE_TTL", raising=False)
    assert cache_module._ttl() == 300
