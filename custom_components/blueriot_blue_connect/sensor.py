"""Sensor platform for Blueriot Blue Connect."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_ISSUER,
    ATTR_LAST_UPDATE,
    ATTR_OK_MAX,
    ATTR_OK_MIN,
    ATTR_TREND,
    ATTR_WARNING_HIGH,
    ATTR_WARNING_LOW,
    DOMAIN,
    MANUFACTURER,
    MODEL,
    SENSOR_TYPES,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    measurements = coordinator.data.get("measurements", [])
    pool = coordinator.data.get("pool", {})
    pool_id = pool.get("id", entry.entry_id)
    pool_name = pool.get("name", "Blue Connect Pool")

    entities: list[BlueriotMeasurementSensor] = []
    for measurement in measurements:
        measurement_name = measurement.get("name")
        if measurement_name not in SENSOR_TYPES:
            continue
        entities.append(
            BlueriotMeasurementSensor(
                coordinator,
                entry,
                pool_id,
                pool_name,
                measurement_name,
            )
        )

    async_add_entities(entities)


class BlueriotMeasurementSensor(CoordinatorEntity, SensorEntity):
    """Blueriot cloud measurement sensor."""

    def __init__(
        self,
        coordinator: Any,
        entry: ConfigEntry,
        pool_id: str,
        pool_name: str,
        measurement_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._pool_id = pool_id
        self._measurement_name = measurement_name

        sensor_config = SENSOR_TYPES[measurement_name]

        self._attr_unique_id = f"{entry.entry_id}_{pool_id}_{measurement_name}"
        self._attr_name = f"{pool_name} {measurement_name.title()}"
        self._attr_icon = sensor_config.get("icon", "mdi:water")
        
        # Set native unit of measurement
        unit = sensor_config["unit"]
        if unit == "°C":
            self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
            self._attr_device_class = SensorDeviceClass.TEMPERATURE
        else:
            self._attr_native_unit_of_measurement = unit
            if sensor_config.get("device_class") is not None:
                self._attr_device_class = sensor_config["device_class"]

        # Set state class for proper history tracking
        self._attr_state_class = SensorStateClass.MEASUREMENT

        # Set device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, pool_id)},
            name=pool_name,
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    def _get_measurement(self) -> dict[str, Any] | None:
        """Return measurement payload for this entity."""
        for measurement in self.coordinator.data.get("measurements", []):
            if measurement.get("name") == self._measurement_name:
                return measurement
        return None

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        measurement = self._get_measurement()
        if measurement is None:
            return None

        value = measurement.get("value")
        if value is None:
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            _LOGGER.warning(
                "Invalid value for %s: %s", self._measurement_name, value
            )
            return None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return measurement metadata."""
        measurement = self._get_measurement()
        if measurement is None:
            return None

        return {
            ATTR_LAST_UPDATE: measurement.get("timestamp"),
            ATTR_TREND: measurement.get("trend"),
            ATTR_OK_MIN: measurement.get("ok_min"),
            ATTR_OK_MAX: measurement.get("ok_max"),
            ATTR_WARNING_LOW: measurement.get("warning_low"),
            ATTR_WARNING_HIGH: measurement.get("warning_high"),
            ATTR_ISSUER: measurement.get("issuer"),
        }

    @property
    def available(self) -> bool:
        """Return entity availability."""
        return super().available and self._get_measurement() is not None

    @property
    def suggested_display_precision(self) -> int | None:
        """Return suggested precision for common measurements."""
        if self._measurement_name in {"ph", "temperature", "chlorine"}:
            return 1
        if self._measurement_name in {"orp", "conductivity", "salinity"}:
            return 0
        return None
