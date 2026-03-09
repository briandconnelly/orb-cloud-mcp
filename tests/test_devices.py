"""Tests for device tools."""

import pytest
import httpx

from orb_cloud_mcp.tools.devices import list_devices, get_device_telemetry
from tests.conftest import DEVICE_PAYLOAD


# ---------------------------------------------------------------------------
# list_devices — stable fields
# ---------------------------------------------------------------------------

async def test_list_devices_success(respx_mock):
    respx_mock.get("/api/v2/organization/org-123/devices").mock(
        return_value=httpx.Response(200, json=DEVICE_PAYLOAD)
    )

    result = await list_devices("org-123")

    assert len(result) == 1
    device = result[0]
    assert device["orb_id"] == "device-abc"
    assert device["name"] == "hardy-house"
    assert device["can_notify"] is False
    # live fields must not be present
    assert "is_connected" not in device
    assert "orb_score" not in device


async def test_list_devices_stable_info(respx_mock):
    respx_mock.get("/api/v2/organization/org-123/devices").mock(
        return_value=httpx.Response(200, json=DEVICE_PAYLOAD)
    )

    result = await list_devices("org-123")
    device = result[0]

    assert device["firmware_version"] == "0.1.0"
    assert device["geoip"]["city"] == "Kirkland"
    assert device["geoip"]["country_code"] == "US"
    assert device["geoip"]["isp_name"] == "Comcast Cable"
    assert device["device_info"]["version"] == "v1.2.3"
    assert device["device_info"]["cpu_count"] == 4
    assert device["network_interface"]["type"] == "Ethernet"
    assert device["network_interface"]["local_ip"] == "192.168.1.1"


async def test_list_devices_empty(respx_mock):
    respx_mock.get("/api/v2/organization/org-123/devices").mock(
        return_value=httpx.Response(200, json=[])
    )

    assert await list_devices("org-123") == []


async def test_list_devices_minimal_summary(respx_mock):
    payload = [{**DEVICE_PAYLOAD[0], "summary": {}}]
    respx_mock.get("/api/v2/organization/org-123/devices").mock(
        return_value=httpx.Response(200, json=payload)
    )

    result = await list_devices("org-123")
    device = result[0]
    assert device["firmware_version"] is None
    assert "geoip" not in device
    assert "device_info" not in device
    assert "network_interface" not in device


async def test_list_devices_partial_tags(respx_mock):
    """Only geoip present — device_info and network_interface omitted."""
    payload = [
        {
            **DEVICE_PAYLOAD[0],
            "summary": {
                **DEVICE_PAYLOAD[0]["summary"],
                "tags": {"geoip": DEVICE_PAYLOAD[0]["summary"]["tags"]["geoip"]},
            },
        }
    ]
    respx_mock.get("/api/v2/organization/org-123/devices").mock(
        return_value=httpx.Response(200, json=payload)
    )

    result = await list_devices("org-123")
    assert "geoip" in result[0]
    assert "device_info" not in result[0]
    assert "network_interface" not in result[0]


async def test_list_devices_http_401(respx_mock):
    respx_mock.get("/api/v2/organization/org-123/devices").mock(
        return_value=httpx.Response(401, json={"message": "Unauthorized"})
    )

    with pytest.raises(httpx.HTTPStatusError):
        await list_devices("org-123")


async def test_list_devices_http_404(respx_mock):
    respx_mock.get("/api/v2/organization/org-123/devices").mock(
        return_value=httpx.Response(404, json={"message": "Not Found"})
    )

    with pytest.raises(httpx.HTTPStatusError):
        await list_devices("org-123")


async def test_list_devices_missing_api_key(monkeypatch):
    monkeypatch.delenv("ORB_CLOUD_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="ORB_CLOUD_API_KEY"):
        await list_devices("org-123")


# ---------------------------------------------------------------------------
# get_device_telemetry — live fields
# ---------------------------------------------------------------------------

async def test_get_device_telemetry_all_devices(respx_mock):
    respx_mock.get("/api/v2/organization/org-123/devices").mock(
        return_value=httpx.Response(200, json=DEVICE_PAYLOAD)
    )

    result = await get_device_telemetry("org-123")

    assert len(result) == 1
    t = result[0]
    assert t["orb_id"] == "device-abc"
    assert t["name"] == "hardy-house"
    assert t["is_connected"] == 1
    assert t["is_connected_updated_at"] == 1757368500851
    # stable fields must not bleed through
    assert "firmware_version" not in t
    assert "geoip" not in t
    assert "config" not in t


async def test_get_device_telemetry_scores(respx_mock):
    respx_mock.get("/api/v2/organization/org-123/devices").mock(
        return_value=httpx.Response(200, json=DEVICE_PAYLOAD)
    )

    result = await get_device_telemetry("org-123")
    t = result[0]

    assert t["orb_score"]["display"] == 91
    assert t["orb_score"]["included"] is True
    assert t["orb_score"]["duration_ms"] == 60000
    assert t["summary_ts"] == DEVICE_PAYLOAD[0]["summary"]["created_ts"]


async def test_get_device_telemetry_filter_by_device_id(respx_mock):
    second = {**DEVICE_PAYLOAD[0], "orb_id": "device-xyz", "name": "other-device"}
    respx_mock.get("/api/v2/organization/org-123/devices").mock(
        return_value=httpx.Response(200, json=[*DEVICE_PAYLOAD, second])
    )

    result = await get_device_telemetry("org-123", device_id="device-abc")

    assert len(result) == 1
    assert result[0]["orb_id"] == "device-abc"


async def test_get_device_telemetry_filter_no_match(respx_mock):
    respx_mock.get("/api/v2/organization/org-123/devices").mock(
        return_value=httpx.Response(200, json=DEVICE_PAYLOAD)
    )

    result = await get_device_telemetry("org-123", device_id="nonexistent")

    assert result == []


async def test_get_device_telemetry_score_with_components(respx_mock):
    payload = [
        {
            **DEVICE_PAYLOAD[0],
            "summary": {
                **DEVICE_PAYLOAD[0]["summary"],
                "orb_score": {
                    "score": 0.9,
                    "display": 95,
                    "included": True,
                    "value": None,
                    "duration_ms": 60000,
                    "score_version": "1.2.0",
                    "components": {
                        "latency": {
                            "score": 0.95,
                            "display": 98,
                            "included": True,
                            "value": 12.5,
                            "duration_ms": 60000,
                            "score_version": "1.2.0",
                            "components": None,
                        }
                    },
                },
            },
        }
    ]
    respx_mock.get("/api/v2/organization/org-123/devices").mock(
        return_value=httpx.Response(200, json=payload)
    )

    result = await get_device_telemetry("org-123")
    components = result[0]["orb_score"]["components"]
    assert components["latency"]["display"] == 98


async def test_get_device_telemetry_orb_scores_list(respx_mock):
    payload = [
        {
            **DEVICE_PAYLOAD[0],
            "summary": {
                **DEVICE_PAYLOAD[0]["summary"],
                "orb_scores": [
                    {
                        "score": 0.75,
                        "display": 80,
                        "included": True,
                        "value": None,
                        "duration_ms": 3600000,
                        "score_version": "1.2.0",
                        "components": None,
                    }
                ],
            },
        }
    ]
    respx_mock.get("/api/v2/organization/org-123/devices").mock(
        return_value=httpx.Response(200, json=payload)
    )

    result = await get_device_telemetry("org-123")
    assert result[0]["orb_scores"][0]["display"] == 80


async def test_get_device_telemetry_minimal_summary(respx_mock):
    payload = [{**DEVICE_PAYLOAD[0], "summary": {}}]
    respx_mock.get("/api/v2/organization/org-123/devices").mock(
        return_value=httpx.Response(200, json=payload)
    )

    result = await get_device_telemetry("org-123")
    t = result[0]
    assert t["summary_ts"] is None
    assert "orb_score" not in t
    assert "orb_scores" not in t


async def test_get_device_telemetry_http_error(respx_mock):
    respx_mock.get("/api/v2/organization/org-123/devices").mock(
        return_value=httpx.Response(500, json={"message": "Internal Server Error"})
    )

    with pytest.raises(httpx.HTTPStatusError):
        await get_device_telemetry("org-123")


async def test_get_device_telemetry_missing_api_key(monkeypatch):
    monkeypatch.delenv("ORB_CLOUD_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="ORB_CLOUD_API_KEY"):
        await get_device_telemetry("org-123")
