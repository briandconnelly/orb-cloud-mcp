# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- MCP server for [Orb Cloud](https://orb.net/product/orb-cloud) device management
- `list_organizations` tool — list all organizations accessible with the API key (cached)
- `list_devices` tool — list devices in an organization with stable configuration details: hardware info, location, firmware, and tags (cached)
- `get_device_telemetry` tool — real-time connectivity status and Orb performance scores for devices in an organization, with optional filtering by device ID
- `trigger_speedtest` tool — trigger a `content` or `top` speed test on a device
- `configure_temp_datasets` tool — enable temporary data push from a device to a custom endpoint, with typed Pydantic input models for push, cloud push, and local API configuration
- `orb://organizations` MCP resource
- `orb://organizations/{organization_id}/devices` MCP resource template
- TTL cache for stable data (`list_organizations`, `list_devices`) keyed by hashed API token; configurable via `ORB_CLOUD_CACHE_TTL` (default: 300s)
- API key read from `ORB_CLOUD_API_KEY` environment variable
- 59 tests with 96% coverage
- Pre-commit hooks via [prek](https://github.com/j178/prek): trailing whitespace, end-of-file fixer, TOML validation, large file check, merge conflict check, `uv-lock`, ruff lint, and ruff format
- MIT license
