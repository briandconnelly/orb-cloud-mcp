"""MCP tools and resources for Orb Cloud organizations."""

from typing import Any

from orb_cloud_client.models.server import OrganizationsResponse

from orb_cloud_mcp.cache import cache, cache_key
from orb_cloud_mcp.client import get_client

_CACHE_KEY = "list_organizations"


async def list_organizations() -> list[dict[str, Any]]:
    """List all Orb Cloud organizations accessible with the configured API key."""
    key = cache_key(_CACHE_KEY)
    if key in cache:
        return cache[key]

    async with get_client() as client:
        orgs = await client.get_organizations()
    result = [_serialize_org(o) for o in orgs]
    cache[key] = result
    return result


def _serialize_org(org: OrganizationsResponse) -> dict[str, Any]:
    plan = None
    if org.plan:
        limits = None
        if org.plan.limits:
            limits = {
                "devices": org.plan.limits.devices,
                "users": org.plan.limits.users,
                "deployment_tokens": org.plan.limits.deployment_tokens,
            }
        plan = {
            "name": org.plan.name,
            "features": org.plan.features,
            "limits": limits,
        }

    usage = None
    if org.usage:
        usage = {
            "devices": org.usage.devices,
            "users": org.usage.users,
            "deployment_tokens": org.usage.deployment_tokens,
        }

    return {
        "organization_id": org.organization_id,
        "name": org.name,
        "customer_id": org.customer_id,
        "subscription_id": org.subscription_id,
        "plan": plan,
        "usage": usage,
    }
