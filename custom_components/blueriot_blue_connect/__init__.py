"""The Blueriot Blue Connect integration."""

from __future__ import annotations

import logging
import pathlib
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED, Platform
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
    """Register the Lovelace card JS resource."""
    # Serve the JS file from the www directory
    try:
        hass.http.register_static_path(_CARD_URL, str(_CARD_PATH), cache_headers=False)
    except Exception as err:  # pylint: disable=broad-except
        _LOGGER.warning("Could not register static path for pool card: %s", err)

    # Strategy 1: add_extra_js_url (HA < 2024.x)
    try:
        from homeassistant.components.frontend import add_extra_js_url  # noqa: PLC0415
        add_extra_js_url(hass, _CARD_URL)
        _LOGGER.debug("Registered pool card via add_extra_js_url")
        return True
    except Exception:  # pylint: disable=broad-except
        pass

    # Strategy 2: Lovelace storage resources API (HA 2024+)
    async def _register_lovelace(_event=None):
        await _async_register_lovelace_resource(hass, _CARD_URL)

    if hass.is_running:
        await _register_lovelace()
    else:
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, _register_lovelace)

    return True


async def _async_register_lovelace_resource(hass: HomeAssistant, url: str) -> None:
    """Add a JS module to Lovelace resources if not already present."""
    try:
        resources = hass.data.get("lovelace", {}).get("resources")
        if resources is None:
            _LOGGER.warning(
                "Could not auto-register pool card. "
                "Add '%s' as a Lovelace resource (type: module) manually "
                "via Settings → Dashboards → Resources.",
                url,
            )
            return
        await resources.async_load()
        current_urls = {r.get("url") for r in resources.data.values()}
        if url in current_urls:
            _LOGGER.debug("Pool card resource already registered")
            return
        await resources.async_create_item({"res_type": "module", "url": url})
        _LOGGER.info("Auto-registered Lovelace resource: %s", url)
    except Exception as err:  # pylint: disable=broad-except
        _LOGGER.warning(
            "Could not auto-register pool card. "
            "Add '%s' as a Lovelace resource (type: module) manually. Error: %s",
            url,
            err,
        )


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
