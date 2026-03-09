"""FastMCP server for Orb Cloud."""

from fastmcp import FastMCP

from orb_cloud_mcp.tools.datasets import configure_temp_datasets
from orb_cloud_mcp.tools.devices import get_device_telemetry, list_devices
from orb_cloud_mcp.tools.organizations import list_organizations
from orb_cloud_mcp.tools.speedtest import trigger_speedtest

mcp = FastMCP(
    name="orb-cloud",
    instructions="Manage Orb Cloud devices, organizations, and run diagnostics.",
)

# --- Tools ---

mcp.tool()(list_organizations)
mcp.tool()(list_devices)
mcp.tool()(get_device_telemetry)
mcp.tool()(trigger_speedtest)
mcp.tool()(configure_temp_datasets)

# --- Resources ---


@mcp.resource("orb://organizations")
async def resource_organizations() -> list:
    """All Orb Cloud organizations accessible with the configured API key."""
    return await list_organizations()


@mcp.resource("orb://organizations/{organization_id}/devices")
async def resource_devices(organization_id: str) -> list:
    """Stable configuration details for all devices in an Orb Cloud organization."""
    return await list_devices(organization_id)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
