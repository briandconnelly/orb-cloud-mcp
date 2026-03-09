"""MCP server for Orb Cloud device management."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("orb-cloud-mcp")
except PackageNotFoundError:
    __version__ = "unknown"
