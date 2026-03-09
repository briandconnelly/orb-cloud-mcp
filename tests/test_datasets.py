"""Tests for configure_temp_datasets tool."""

import httpx
import pytest

from orb_cloud_mcp.tools.datasets import (
    DataAPIConfig,
    DataPushConfig,
    DatasetsConfig,
    configure_temp_datasets,
)

DATASETS_RESPONSE = {"status": "configured", "expires_at": "2024-01-01T01:00:00Z"}


async def test_configure_temp_datasets_minimal(respx_mock):
    respx_mock.post("/api/v1/device/device-abc/temp-datasets").mock(
        return_value=httpx.Response(200, json=DATASETS_RESPONSE)
    )

    result = await configure_temp_datasets("device-abc", duration="1h")
    assert result["status"] == "configured"


async def test_configure_temp_datasets_with_push(respx_mock):
    route = respx_mock.post("/api/v1/device/device-abc/temp-datasets").mock(
        return_value=httpx.Response(200, json=DATASETS_RESPONSE)
    )

    config = DatasetsConfig(
        datasets=["responsiveness_1s", "speed_results"],
        push=DataPushConfig(
            url="https://example.com/data",
            datasets=["responsiveness_1s"],
            enabled=True,
            identifiable=False,
            format="json",
            interval_ms=1000,
        ),
    )

    result = await configure_temp_datasets(
        "device-abc", duration="30m", datasets_config=config
    )
    assert result["status"] == "configured"

    # Verify the request body was sent
    sent = route.calls.last.request
    assert b"responsiveness_1s" in sent.content
    assert b"example.com" in sent.content


async def test_configure_temp_datasets_with_api(respx_mock):
    respx_mock.post("/api/v1/device/device-abc/temp-datasets").mock(
        return_value=httpx.Response(200, json=DATASETS_RESPONSE)
    )

    config = DatasetsConfig(
        api=DataAPIConfig(
            enabled=True,
            datasets=["speed_results"],
            port=8080,
            identifiable=True,
        )
    )

    result = await configure_temp_datasets(
        "device-abc", duration="2h", datasets_config=config
    )
    assert result["status"] == "configured"


async def test_configure_temp_datasets_with_cloud_push(respx_mock):
    respx_mock.post("/api/v1/device/device-abc/temp-datasets").mock(
        return_value=httpx.Response(200, json=DATASETS_RESPONSE)
    )

    config = DatasetsConfig(
        cloud_push=DataPushConfig(
            url="https://cloud.example.com/ingest",
            enabled=True,
        )
    )

    result = await configure_temp_datasets(
        "device-abc", duration="1h", datasets_config=config
    )
    assert result["status"] == "configured"


async def test_configure_temp_datasets_http_401(respx_mock):
    respx_mock.post("/api/v1/device/device-abc/temp-datasets").mock(
        return_value=httpx.Response(401, json={"message": "Unauthorized"})
    )

    with pytest.raises(httpx.HTTPStatusError):
        await configure_temp_datasets("device-abc", duration="1h")


async def test_configure_temp_datasets_http_404(respx_mock):
    respx_mock.post("/api/v1/device/device-abc/temp-datasets").mock(
        return_value=httpx.Response(404, json={"message": "Device not found"})
    )

    with pytest.raises(httpx.HTTPStatusError):
        await configure_temp_datasets("device-abc", duration="1h")


async def test_configure_temp_datasets_http_500(respx_mock):
    respx_mock.post("/api/v1/device/device-abc/temp-datasets").mock(
        return_value=httpx.Response(500, json={"message": "Internal Server Error"})
    )

    with pytest.raises(httpx.HTTPStatusError):
        await configure_temp_datasets("device-abc", duration="1h")


async def test_configure_temp_datasets_missing_api_key(monkeypatch):
    monkeypatch.delenv("ORB_CLOUD_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="ORB_CLOUD_API_KEY"):
        await configure_temp_datasets("device-abc", duration="1h")
