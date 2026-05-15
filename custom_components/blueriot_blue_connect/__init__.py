"""The Blueriot Blue Connect integration."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .api import BlueriotBlueConnectCloudAPI
from .const import (
    CONF_LANGUAGE,
    CONF_PASSWORD,
    CONF_POLLING_INTERVAL,
    CONF_USERNAME,
    DEFAULT_LANGUAGE,
    DEFAULT_POLLING_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Blueriot Blue Connect from a config entry."""

    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]
    language = entry.data.get(CONF_LANGUAGE, DEFAULT_LANGUAGE)
    polling_interval = entry.data.get(CONF_POLLING_INTERVAL, DEFAULT_POLLING_INTERVAL)

    # Initialize the API client
    api = BlueriotBlueConnectCloudAPI(username, password, language)

    # Create the data update coordinator
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="Blueriot Blue Connect",
        update_method=api.async_fetch_data,
        update_interval=timedelta(seconds=polling_interval),
    )

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    # Store the coordinator and API in hass data
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "api": api,
    }

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        await hass.data[DOMAIN][entry.entry_id]["api"].async_close()
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
