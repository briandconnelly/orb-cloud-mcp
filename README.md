# orb-cloud-mcp

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/orb-cloud-mcp)
![PyPI - License](https://img.shields.io/pypi/l/orb-cloud-mcp)
![PyPI - Version](https://img.shields.io/pypi/v/orb-cloud-mcp)

An [MCP](https://modelcontextprotocol.io/) server for [Orb Cloud](https://orb.net/product/orb-cloud) device management. Exposes your Orb Cloud organizations and devices to any MCP-compatible client (Claude Desktop, Cursor, etc.).

## Tools and resources

**Tools**

| Tool | Description |
|------|-------------|
| `list_organizations` | List all organizations accessible with your API key |
| `list_devices` | List devices in an organization — hardware info, location, firmware, and configuration (cached) |
| `get_device_telemetry` | Real-time connectivity status and Orb performance scores for devices in an organization |
| `trigger_speedtest` | Trigger a `content` or `top` speed test on a device |
| `configure_temp_datasets` | Enable temporary data push from a device to a custom endpoint |

**Resources**

| URI | Description |
|-----|-------------|
| `orb://organizations` | All accessible organizations (cached) |
| `orb://organizations/{organization_id}/devices` | Stable device info for an organization (cached) |

`list_devices` and `list_organizations` results are cached for 5 minutes by default (see [Configuration](#configuration)).

## Requirements

- Python 3.10+
- An Orb Cloud API token — requires a [Plus plan or above](https://orb.net/product/orb-cloud). Generate a token in the Orb Cloud panel under **Settings → API Keys**.

## Installation

```bash
pip install orb-cloud-mcp
```

## Configuration

| Environment variable | Required | Default | Description |
|----------------------|----------|---------|-------------|
| `ORB_CLOUD_API_KEY` | Yes | — | Your Orb Cloud API token |
| `ORB_CLOUD_CACHE_TTL` | No | `300` | Cache TTL in seconds for stable data. Set to `0` to disable caching. |

### Claude Desktop

The config file location varies by platform:

- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "orb-cloud": {
      "command": "uvx",
      "args": ["orb-cloud-mcp"],
      "env": {
        "ORB_CLOUD_API_KEY": "your-token-here"
      }
    }
  }
}
```

### Cursor and other MCP clients

```json
{
  "mcpServers": {
    "orb-cloud": {
      "command": "uvx",
      "args": ["orb-cloud-mcp"],
      "env": {
        "ORB_CLOUD_API_KEY": "your-token-here"
      }
    }
  }
}
```

## Disclaimer

This tool is not officially affiliated with Orb. For official support, visit [orb.net](https://orb.net).
