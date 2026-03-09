"""Tests for server wiring and resources."""

from unittest.mock import patch

import httpx
import pytest

from orb_cloud_mcp.server import mcp, main, resource_organizations, resource_devices
from tests.conftest import ORG_PAYLOAD, DEVICE_PAYLOAD


async def test_server_has_tools():
    tools = await mcp.list_tools()
    tool_names = {t.name for t in tools}
    assert "list_organizations" in tool_names
    assert "list_devices" in tool_names
    assert "get_device_telemetry" in tool_names
    assert "trigger_speedtest" in tool_names
    assert "configure_temp_datasets" in tool_names


async def test_server_has_resources():
    resources = await mcp.list_resources()
    uris = {str(r.uri) for r in resources}
    assert "orb://organizations" in uris


async def test_server_has_resource_templates():
    templates = await mcp.list_resource_templates()
    uris = {str(t.uri_template) for t in templates}
    assert "orb://organizations/{organization_id}/devices" in uris


async def test_resource_organizations(respx_mock):
    respx_mock.get("/api/v2/organizations").mock(
        return_value=httpx.Response(200, json=ORG_PAYLOAD)
    )

    result = await resource_organizations()
    assert len(result) == 1
    assert result[0]["organization_id"] == "org-123"


def test_main_calls_run():
    with patch.object(mcp, "run") as mock_run:
        main()
    mock_run.assert_called_once()


async def test_resource_devices(respx_mock):
    respx_mock.get("/api/v2/organization/org-123/devices").mock(
        return_value=httpx.Response(200, json=DEVICE_PAYLOAD)
    )

    result = await resource_devices("org-123")
    assert len(result) == 1
    assert result[0]["orb_id"] == "device-abc"
