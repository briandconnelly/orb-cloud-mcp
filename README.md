# orb-cloud-mcp

An [MCP](https://modelcontextprotocol.io/) server for [Orb Cloud](https://orb.net/product/orb-cloud) device management. Exposes your Orb Cloud organizations and devices to any MCP-compatible client (Claude Desktop, Cursor, etc.).

## Features

**Tools**
- `list_organizations` — List all organizations accessible with your API key
- `list_devices` — List devices in an organization, including connectivity status and Orb scores
- `trigger_speedtest` — Run a `content` or `top` speed test on a device
- `configure_temp_datasets` — Enable temporary data push from a device to a custom endpoint

**Resources**
- `orb://organizations` — All accessible organizations
- `orb://organizations/{organization_id}/devices` — Devices in an organization

## Requirements

- Python 3.10+
- An Orb Cloud API token (Plus plan or above)

## Installation

```bash
uv tool install orb-cloud-mcp
```

## Configuration

Set your API token in the `ORB_CLOUD_API_KEY` environment variable:

```bash
export ORB_CLOUD_API_KEY=your-token-here
```

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

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

### Cursor / other MCP clients

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

## Development

```bash
git clone https://github.com/yourname/orb-cloud-mcp
cd orb-cloud-mcp
uv sync
uv run pytest
```
