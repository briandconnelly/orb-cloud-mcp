"""MCP tool to configure temporary dataset push on Orb Cloud devices."""

from typing import Any

from pydantic import BaseModel, Field

from orb_cloud_mcp.client import get_client


class DataPushConfig(BaseModel):
    """Configuration for pushing data to a custom HTTP endpoint."""

    url: str = Field(..., description="Destination URL to push data to.")
    datasets: list[str] | None = Field(
        None,
        description="Dataset names to include (e.g. ['responsiveness_1s', 'speed_results']).",
    )
    enabled: bool | None = Field(None, description="Whether pushing is enabled.")
    identifiable: bool | None = Field(
        None, description="Whether to include identifiable data."
    )
    format: str | None = Field(None, description="Payload format (e.g. 'json').")
    interval_ms: int | None = Field(
        None, description="Push interval in milliseconds."
    )
    buffer_kb: int | None = Field(None, description="Buffer size in kilobytes.")


class DataAPIConfig(BaseModel):
    """Configuration for exposing a local data API on the device."""

    enabled: bool | None = Field(None, description="Whether the data API is enabled.")
    datasets: list[str] | None = Field(
        None, description="Dataset names to expose via the API."
    )
    identifiable: bool | None = Field(
        None, description="Whether to include identifiable data."
    )
    api_key: str | None = Field(None, description="API key for the local data API.")
    port: int | None = Field(None, description="Port for the local data API.")
    buffer: int | None = Field(None, description="Buffer size.")


class DatasetsConfig(BaseModel):
    """Top-level dataset configuration."""

    datasets: list[str] | None = Field(
        None, description="Dataset names to collect."
    )
    enabled: bool | None = Field(None, description="Whether data collection is enabled.")
    push: DataPushConfig | None = Field(
        None, description="Push data to a custom HTTP endpoint."
    )
    cloud_push: DataPushConfig | None = Field(
        None, description="Push data to Orb Cloud."
    )
    api: DataAPIConfig | None = Field(
        None, description="Expose data via a local API endpoint on the device."
    )


async def configure_temp_datasets(
    device_id: str,
    duration: str = Field(..., description="How long to enable (e.g. '30m', '1h', '2h')."),
    datasets_config: DatasetsConfig | None = None,
) -> dict[str, Any]:
    """Configure temporary dataset collection and push for an Orb Cloud device.

    Enables the device to push data to a custom endpoint or expose a local API
    for a fixed duration. After the duration expires, the device reverts to its
    default configuration.

    Args:
        device_id: The Orb device ID to configure.
        duration: How long to enable the configuration (e.g. '30m', '1h').
        datasets_config: Dataset collection and push configuration. If omitted,
            only the duration is updated.
    """
    from orb_cloud_client.models.generic import TempDatasetsRequest
    from orb_cloud_client.models.config import Datasets, DataPush, DataAPI

    def _to_data_push(cfg: DataPushConfig | None) -> DataPush | None:
        if cfg is None:
            return None
        return DataPush(**cfg.model_dump(exclude_none=True))

    def _to_data_api(cfg: DataAPIConfig | None) -> DataAPI | None:
        if cfg is None:
            return None
        return DataAPI(**cfg.model_dump(exclude_none=True))

    sdk_datasets: Datasets | None = None
    if datasets_config is not None:
        sdk_datasets = Datasets(
            datasets=datasets_config.datasets,
            enabled=datasets_config.enabled,
            push=_to_data_push(datasets_config.push),
            cloud_push=_to_data_push(datasets_config.cloud_push),
            api=_to_data_api(datasets_config.api),
        )

    request = TempDatasetsRequest(
        duration=duration,
        datasets_config=sdk_datasets,
    )

    async with get_client() as client:
        return await client.configure_temporary_datasets(device_id, request)
