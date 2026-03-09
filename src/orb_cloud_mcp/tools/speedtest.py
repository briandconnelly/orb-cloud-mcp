"""MCP tool to trigger speed tests on Orb Cloud devices."""

from typing import Any, Literal

from orb_cloud_mcp.client import get_client


async def trigger_speedtest(
    device_id: str,
    test_type: Literal["content", "top"],
) -> dict[str, Any]:
    """Trigger a speed test on an Orb Cloud device.

    Args:
        device_id: The Orb device ID to run the speed test on.
        test_type: The type of speed test — 'content' measures content delivery
            performance, 'top' measures peak throughput.
    """
    async with get_client() as client:
        return await client.trigger_speedtest(device_id, test_type)
