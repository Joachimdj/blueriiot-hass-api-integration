"""The Blueriot Blue Connect integration."""

from __future__ import annotations

import logging
import pathlib
from datetime import timedelta

from homeassistant.components.frontend import add_extra_js_url
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

_CARD_URL = f"/{DOMAIN}/blueriot-pool-card.js"
_CARD_PATH = pathlib.Path(__file__).parent / "www" / "blueriot-pool-card.js"


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Register the Lovelace card resource once at startup."""
    hass.http.register_static_path(_CARD_URL, str(_CARD_PATH), cache_headers=False)
    add_extra_js_url(hass, _CARD_URL)
    _LOGGER.debug("Registered Blueriot pool card at %s", _CARD_URL)
    return True


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
