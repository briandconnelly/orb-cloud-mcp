"""Orb Cloud client factory, reads credentials from environment."""

import os

from orb_cloud_client.client import OrbCloudClientAsync


def get_client() -> OrbCloudClientAsync:
    """Return an authenticated async Orb Cloud client.

    Raises:
        RuntimeError: If ORB_CLOUD_API_KEY is not set.
    """
    token = os.environ.get("ORB_CLOUD_API_KEY")
    if not token:
        raise RuntimeError(
            "ORB_CLOUD_API_KEY environment variable is not set. "
            "Set it to your Orb Cloud API token."
        )
    return OrbCloudClientAsync(token=token)
