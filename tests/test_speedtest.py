"""Tests for speedtest tool."""

import pytest
import httpx

from orb_cloud_mcp.tools.speedtest import trigger_speedtest


SPEEDTEST_RESPONSE = {"status": "triggered", "test_id": "test-xyz"}


async def test_trigger_speedtest_content(respx_mock):
    respx_mock.post("/api/v2/device/device-abc/trigger-speedtest/content").mock(
        return_value=httpx.Response(200, json=SPEEDTEST_RESPONSE)
    )

    result = await trigger_speedtest("device-abc", "content")
    assert result["status"] == "triggered"
    assert result["test_id"] == "test-xyz"


async def test_trigger_speedtest_top(respx_mock):
    respx_mock.post("/api/v2/device/device-abc/trigger-speedtest/top").mock(
        return_value=httpx.Response(200, json=SPEEDTEST_RESPONSE)
    )

    result = await trigger_speedtest("device-abc", "top")
    assert result["status"] == "triggered"


async def test_trigger_speedtest_http_401(respx_mock):
    respx_mock.post("/api/v2/device/device-abc/trigger-speedtest/content").mock(
        return_value=httpx.Response(401, json={"message": "Unauthorized"})
    )

    with pytest.raises(httpx.HTTPStatusError):
        await trigger_speedtest("device-abc", "content")


async def test_trigger_speedtest_http_404(respx_mock):
    respx_mock.post("/api/v2/device/device-abc/trigger-speedtest/content").mock(
        return_value=httpx.Response(404, json={"message": "Device not found"})
    )

    with pytest.raises(httpx.HTTPStatusError):
        await trigger_speedtest("device-abc", "content")


async def test_trigger_speedtest_http_500(respx_mock):
    respx_mock.post("/api/v2/device/device-abc/trigger-speedtest/top").mock(
        return_value=httpx.Response(500, json={"message": "Internal Server Error"})
    )

    with pytest.raises(httpx.HTTPStatusError):
        await trigger_speedtest("device-abc", "top")


async def test_trigger_speedtest_missing_api_key(monkeypatch):
    monkeypatch.delenv("ORB_CLOUD_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="ORB_CLOUD_API_KEY"):
        await trigger_speedtest("device-abc", "content")
