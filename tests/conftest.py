"""Shared test fixtures."""

import pytest
import respx

import orb_cloud_mcp.cache as _cache_module


@pytest.fixture(autouse=True)
def set_api_key(monkeypatch):
    """Set a fake API key for all tests."""
    monkeypatch.setenv("ORB_CLOUD_API_KEY", "test-api-key")


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear the shared TTL cache before every test."""
    _cache_module.cache.clear()
    yield
    _cache_module.cache.clear()


@pytest.fixture
def respx_mock():
    with respx.mock(base_url="https://panel.orb.net", assert_all_called=False) as mock:
        yield mock


# --- Shared sample data ---

ORG_PAYLOAD = [
    {
        "organization_id": "org-123",
        "name": "Test Org",
        "customer_id": "cust-456",
        "subscription_id": "sub-789",
        "plan": {
            "name": "Plus",
            "features": ["api_access"],
            "limits": {"devices": 10, "users": 5, "deployment_tokens": 3},
        },
        "usage": {"devices": 2, "users": 1, "deployment_tokens": 0},
    }
]

DEVICE_PAYLOAD = [
    {
        "orb_id": "device-abc",
        "name": "hardy-house",
        "is_connected": 1,
        "is_connected_updated_at": 1757368500851,
        "can_notify": False,
        "tags": ["dt=Default Configuration"],
        "config": None,
        "created_ts": 1757368560803,
        "summary": {
            "version": "0.1.0",
            "created_ts": 1757391432134,
            "orb_score": {
                "score": 0.83,
                "display": 91,
                "included": True,
                "value": None,
                "duration_ms": 60000,
                "score_version": "1.2.0",
                "components": {},
            },
            "orb_scores": [],
            "tags": {
                "geoip": {
                    "city": "Kirkland",
                    "state": "Washington",
                    "country": "United States",
                    "country_code": "US",
                    "isp_name": "Comcast Cable",
                    "latitude": 47.6784,
                    "longitude": -122.1857,
                },
                "device_info": {
                    "name": "hardy-house",
                    "full_name": "hardy-house",
                    "version": "v1.2.3",
                    "cpu_count": 4,
                    "operating_system": "linux",
                },
                "network_interface": {
                    "name": "",
                    "type": "Ethernet",
                    "local_ip": "192.168.1.1",
                    "mac_address": "00:90:0b:a5:de:2a",
                },
            },
        },
    }
]
