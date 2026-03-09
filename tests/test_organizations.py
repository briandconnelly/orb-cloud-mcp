"""Tests for organization tools and resources."""

import httpx
import pytest

from orb_cloud_mcp.tools.organizations import list_organizations
from tests.conftest import ORG_PAYLOAD


async def test_list_organizations_success(respx_mock):
    respx_mock.get("/api/v2/organizations").mock(
        return_value=httpx.Response(200, json=ORG_PAYLOAD)
    )

    result = await list_organizations()

    assert len(result) == 1
    org = result[0]
    assert org["organization_id"] == "org-123"
    assert org["name"] == "Test Org"
    assert org["customer_id"] == "cust-456"
    assert org["subscription_id"] == "sub-789"


async def test_list_organizations_plan_serialized(respx_mock):
    respx_mock.get("/api/v2/organizations").mock(
        return_value=httpx.Response(200, json=ORG_PAYLOAD)
    )

    result = await list_organizations()
    plan = result[0]["plan"]

    assert plan["name"] == "Plus"
    assert plan["features"] == ["api_access"]
    assert plan["limits"]["devices"] == 10
    assert plan["limits"]["users"] == 5
    assert plan["limits"]["deployment_tokens"] == 3


async def test_list_organizations_usage_serialized(respx_mock):
    respx_mock.get("/api/v2/organizations").mock(
        return_value=httpx.Response(200, json=ORG_PAYLOAD)
    )

    result = await list_organizations()
    usage = result[0]["usage"]

    assert usage["devices"] == 2
    assert usage["users"] == 1


async def test_list_organizations_empty(respx_mock):
    respx_mock.get("/api/v2/organizations").mock(
        return_value=httpx.Response(200, json=[])
    )

    result = await list_organizations()
    assert result == []


async def test_list_organizations_no_plan(respx_mock):
    payload = [{**ORG_PAYLOAD[0], "plan": None, "usage": None}]
    respx_mock.get("/api/v2/organizations").mock(
        return_value=httpx.Response(200, json=payload)
    )

    result = await list_organizations()
    assert result[0]["plan"] is None
    assert result[0]["usage"] is None


async def test_list_organizations_http_error(respx_mock):
    respx_mock.get("/api/v2/organizations").mock(
        return_value=httpx.Response(401, json={"message": "Unauthorized"})
    )

    with pytest.raises(httpx.HTTPStatusError):
        await list_organizations()


async def test_list_organizations_server_error(respx_mock):
    respx_mock.get("/api/v2/organizations").mock(
        return_value=httpx.Response(500, json={"message": "Internal Server Error"})
    )

    with pytest.raises(httpx.HTTPStatusError):
        await list_organizations()


async def test_list_organizations_missing_api_key(monkeypatch):
    monkeypatch.delenv("ORB_CLOUD_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="ORB_CLOUD_API_KEY"):
        await list_organizations()
