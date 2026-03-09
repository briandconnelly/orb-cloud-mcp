"""MCP tools for Orb Cloud devices."""

from typing import Any

from orb_cloud_client.models.generic import Device, OrbScore

from orb_cloud_mcp.cache import cache, cache_key
from orb_cloud_mcp.client import get_client

_CACHE_KEY = "list_devices"


async def list_devices(organization_id: str) -> list[dict[str, Any]]:
    """List devices in an Orb Cloud organization with stable configuration details.

    Returns device identity, hardware info, location, and configuration — data
    that changes rarely. For real-time connectivity and performance scores, use
    get_device_telemetry instead.

    Args:
        organization_id: The organization ID to list devices for.
    """
    key = cache_key(_CACHE_KEY, organization_id)
    if key in cache:
        return cache[key]

    async with get_client() as client:
        devices = await client.get_organization_devices(organization_id)
    result = [_serialize_stable(d) for d in devices]
    cache[key] = result
    return result


async def get_device_telemetry(
    organization_id: str,
    device_id: str | None = None,
) -> list[dict[str, Any]]:
    """Get live telemetry for devices in an Orb Cloud organization.

    Returns real-time connectivity status and Orb performance scores. If
    device_id is provided, returns telemetry for that device only.

    Args:
        organization_id: The organization ID to query devices for.
        device_id: Optional Orb device ID to filter to a single device.
    """
    async with get_client() as client:
        devices = await client.get_organization_devices(organization_id)

    if device_id is not None:
        devices = [d for d in devices if d.orb_id == device_id]

    return [_serialize_telemetry(d) for d in devices]


def _serialize_score(score: OrbScore | None) -> dict[str, Any] | None:
    if score is None:
        return None
    result: dict[str, Any] = {
        "score": score.score,
        "display": score.display,
        "included": score.included,
        "value": score.value,
        "duration_ms": score.duration_ms,
        "score_version": score.score_version,
    }
    if score.components:
        result["components"] = {k: _serialize_score(v) for k, v in score.components.items()}
    return result


def _serialize_stable(device: Device) -> dict[str, Any]:
    """Serialize the stable, slowly-changing fields of a device."""
    info: dict[str, Any] = {}
    if device.summary:
        s = device.summary
        info["firmware_version"] = s.version
        if s.tags:
            if s.tags.geoip:
                g = s.tags.geoip
                info["geoip"] = {
                    "city": g.city,
                    "state": g.state,
                    "country": g.country,
                    "country_code": g.country_code,
                    "isp_name": g.isp_name,
                    "latitude": g.latitude,
                    "longitude": g.longitude,
                }
            if s.tags.device_info:
                di = s.tags.device_info
                info["device_info"] = {
                    "name": di.name,
                    "full_name": di.full_name,
                    "version": di.version,
                    "cpu_count": di.cpu_count,
                    "operating_system": di.operating_system,
                }
            if s.tags.network_interface:
                ni = s.tags.network_interface
                info["network_interface"] = {
                    "name": ni.name,
                    "type": ni.type,
                    "local_ip": ni.local_ip,
                    "mac_address": ni.mac_address,
                }

    return {
        "orb_id": device.orb_id,
        "name": device.name,
        "can_notify": device.can_notify,
        "tags": device.tags,
        "config": device.config,
        "created_ts": device.created_ts,
        **info,
    }


def _serialize_telemetry(device: Device) -> dict[str, Any]:
    """Serialize the live, frequently-changing fields of a device."""
    scores: dict[str, Any] = {}
    if device.summary:
        s = device.summary
        scores["summary_ts"] = s.created_ts
        if s.orb_score:
            scores["orb_score"] = _serialize_score(s.orb_score)
        if s.orb_scores:
            scores["orb_scores"] = [_serialize_score(sc) for sc in s.orb_scores]

    return {
        "orb_id": device.orb_id,
        "name": device.name,
        "is_connected": device.is_connected.value,
        "is_connected_updated_at": device.is_connected_updated_at,
        **scores,
    }
