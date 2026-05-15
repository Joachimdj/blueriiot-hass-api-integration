"""Cloud API client for Blueriot Blue Connect."""

from __future__ import annotations

import aiohttp
from dataclasses import dataclass
import logging
from typing import Any

from blueconnect import BlueConnectApi

_LOGGER = logging.getLogger(__name__)

_LOGIN_URL = "https://api.riiotlabs.com/prod/user/login"
_LOGIN_HEADERS = {"User-Agent": "BlueConnect/3.2.1", "Accept": "*/*"}


class BlueriotBlueConnectAPIError(Exception):
    """Exception for connectivity / server errors."""


class BlueriotBlueConnectInvalidAuth(BlueriotBlueConnectAPIError):
    """Exception raised when credentials are rejected by the cloud."""


@dataclass
class BlueriotMeasurement:
    """Normalized measurement payload."""

    name: str
    value: float | int | None
    timestamp: str | None
    trend: str | None
    ok_min: float | int | None
    ok_max: float | int | None
    warning_low: float | int | None
    warning_high: float | int | None
    issuer: str | None


class BlueriotBlueConnectCloudAPI:
    """Cloud API wrapper for Blue Connect data retrieval."""

    def __init__(self, username: str, password: str, language: str = "en") -> None:
        """Initialize the cloud API client wrapper."""
        self._username = username
        self._password = password
        self._language = language
        self._api = BlueConnectApi(username, password)

    @staticmethod
    def _safe_attr(value: Any, attr: str, default: Any = None) -> Any:
        """Read from object attr or dict key."""
        if isinstance(value, dict):
            return value.get(attr, default)
        return getattr(value, attr, default)

    @staticmethod
    def _normalize_timestamp(value: Any) -> str | None:
        """Convert timestamp object to ISO string."""
        if value is None:
            return None
        if hasattr(value, "isoformat"):
            return value.isoformat()
        return str(value)

    def _normalize_measurement(self, measurement: Any) -> BlueriotMeasurement:
        """Normalize SDK measurement model to a stable shape."""
        trend = self._safe_attr(measurement, "trend")
        trend_value = self._safe_attr(trend, "value") if trend is not None else None

        return BlueriotMeasurement(
            name=str(self._safe_attr(measurement, "name", "unknown")),
            value=self._safe_attr(measurement, "value"),
            timestamp=self._normalize_timestamp(self._safe_attr(measurement, "timestamp")),
            trend=str(trend_value) if trend_value is not None else None,
            ok_min=self._safe_attr(measurement, "ok_min"),
            ok_max=self._safe_attr(measurement, "ok_max"),
            warning_low=self._safe_attr(measurement, "warning_low"),
            warning_high=self._safe_attr(measurement, "warning_high"),
            issuer=self._safe_attr(measurement, "issuer"),
        )

    @staticmethod
    async def async_validate_credentials(username: str, password: str) -> bool:
        """Validate cloud credentials by calling the login endpoint directly.

        Avoids blueconnect model parsing which breaks when the API omits
        optional user preference fields (display_temperature_unit, etc.).

        Raises BlueriotBlueConnectInvalidAuth if credentials are rejected.
        Raises BlueriotBlueConnectAPIError for network/server problems.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    _LOGIN_URL,
                    json={"email": username, "password": password},
                    headers=_LOGIN_HEADERS,
                    ssl=False,
                ) as response:
                    if response.status == 200:
                        return True
                    body = await response.text()
                    _LOGGER.warning(
                        "Blue Connect login rejected (HTTP %s): %s", response.status, body
                    )
                    raise BlueriotBlueConnectInvalidAuth(
                        f"Login rejected (HTTP {response.status}): {body}"
                    )
        except BlueriotBlueConnectInvalidAuth:
            raise
        except Exception as err:
            _LOGGER.warning("Blue Connect credential validation failed: %s", err)
            raise BlueriotBlueConnectAPIError(str(err)) from err

    async def async_fetch_data(self) -> dict[str, Any]:
        """Fetch latest pool and measurement data from cloud.

        Uses BlueConnectApi directly to avoid BlueConnectSimpleAPI.fetch_data()
        which internally calls get_user() and fails on missing UserPreferences fields.
        """
        try:
            pools = await self._api.get_swimming_pools()
            if not pools:
                raise BlueriotBlueConnectAPIError("No swimming pools found on this account")

            pool = pools[0]
            pool_id = pool.swimming_pool_id
            pool_name = pool.name

            blue_devices = await self._api.get_swimming_pool_blue_devices(pool_id)
            blue_device = blue_devices[0] if blue_devices else None

            raw_measurements: list[Any] = []
            if blue_device:
                result = await self._api.get_last_measurements(pool_id, blue_device.serial)
                raw_measurements = result.measurements or []

        except BlueriotBlueConnectAPIError:
            raise
        except Exception as err:  # pylint: disable=broad-except
            raise BlueriotBlueConnectAPIError(f"Cloud fetch failed: {err}") from err

        measurements = [self._normalize_measurement(m) for m in raw_measurements]

        return {
            "pool": {
                "id": str(pool_id),
                "name": str(pool_name),
            },
            "measurements": [m.__dict__ for m in measurements],
            "battery_low": getattr(blue_device, "battery_low", None),
            "device_serial": getattr(blue_device, "serial", None),
        }

    async def async_close(self) -> None:
        """Close underlying async clients."""
        await self._api.close_async()
