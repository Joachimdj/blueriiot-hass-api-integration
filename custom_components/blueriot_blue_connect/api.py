"""Cloud API client for Blueriot Blue Connect."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any

from blueconnect import BlueConnectApi, BlueConnectSimpleAPI

_LOGGER = logging.getLogger(__name__)


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
        self._simple_api = BlueConnectSimpleAPI(username, password, language)

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
        """Validate cloud credentials using the official API.

        Returns True on success.
        Raises BlueriotBlueConnectInvalidAuth if credentials are rejected.
        Raises BlueriotBlueConnectAPIError for network/server problems.
        """
        api = BlueConnectApi(username, password)
        try:
            user_info = await api.get_user()
            return user_info is not None
        except Exception as err:  # pylint: disable=broad-except
            err_str = str(err)
            _LOGGER.warning("Blue Connect credential validation failed: %s", err_str)
            # The library raises a plain Exception whose message starts with
            # "Error logging in user:" when the HTTP login returns non-200.
            # Treat that as an auth failure; everything else is a connectivity problem.
            if "Error logging in user" in err_str or "login" in err_str.lower():
                raise BlueriotBlueConnectInvalidAuth(err_str) from err
            raise BlueriotBlueConnectAPIError(err_str) from err
        finally:
            await api.close_async()

    async def async_fetch_data(self) -> dict[str, Any]:
        """Fetch latest pool and measurement data from cloud."""
        try:
            await self._simple_api.fetch_data()
        except Exception as err:  # pylint: disable=broad-except
            raise BlueriotBlueConnectAPIError(f"Cloud fetch failed: {err}") from err

        pool = self._simple_api.pool
        pool_id = self._safe_attr(pool, "swimming_pool_id", "unknown_pool")
        pool_name = self._safe_attr(pool, "name", "Blue Connect Pool")

        measurements = [
            self._normalize_measurement(measurement)
            for measurement in (self._simple_api.measurements or [])
        ]

        return {
            "pool": {
                "id": str(pool_id),
                "name": str(pool_name),
            },
            "measurements": [measurement.__dict__ for measurement in measurements],
            "battery_low": self._safe_attr(self._simple_api.blue_device, "battery_low", None),
            "device_serial": self._safe_attr(self._simple_api.blue_device, "serial", None),
        }

    async def async_close(self) -> None:
        """Close underlying async clients."""
        await self._simple_api.close_async()
