"""The Blueriot Blue Connect integration."""

from __future__ import annotations

import logging
import pathlib
import shutil
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED, Platform
from homeassistant.core import HomeAssistant, callback
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

_CARD_SOURCE = pathlib.Path(__file__).parent / "www" / "blueriot-pool-card.js"
_CARD_LOCAL_URL = "/local/blueriot-pool-card.js"


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Copy the Lovelace card to config/www and register it as a resource."""
    # 1. Copy JS → config/www/ (always served at /local/ by HA)
    www_dir = pathlib.Path(hass.config.path("www"))

    def _copy_card() -> None:
        www_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(_CARD_SOURCE), str(www_dir / "blueriot-pool-card.js"))

    try:
        await hass.async_add_executor_job(_copy_card)
        _LOGGER.debug("Copied pool card to %s", www_dir)
    except Exception as err:  # pylint: disable=broad-except
        _LOGGER.warning("Could not copy pool card to www: %s", err)
        return True

    # 2. Defer resource registration until after HA is fully started so that
    #    hass.data["lovelace"] is guaranteed to be populated.
    @callback
    def _on_hass_started(event) -> None:  # noqa: ANN001
        hass.async_create_task(
            _async_register_lovelace_resource(hass, _CARD_LOCAL_URL)
        )

    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, _on_hass_started)
    return True


async def _async_register_lovelace_resource(hass: HomeAssistant, url: str) -> None:
    """Add a JS module to Lovelace resources if not already present."""
    try:
        lovelace = hass.data.get("lovelace")
        if lovelace is None:
            _LOGGER.warning(
                "Lovelace not found in hass.data — pool card not auto-registered. "
                "Add manually: Settings → Dashboards → Resources → URL: %s  "
                "Type: JavaScript module",
                url,
            )
            return

        resources = getattr(lovelace, "resources", None)
        if resources is None:
            _LOGGER.warning(
                "LovelaceData has no 'resources' attribute — pool card not auto-registered. "
                "Add manually: Settings → Dashboards → Resources → URL: %s  "
                "Type: JavaScript module",
                url,
            )
            return

        await resources.async_load()

        # async_items() is the public API; fall back to .data.values() if absent
        existing = (
            list(resources.async_items())
            if hasattr(resources, "async_items")
            else list(resources.data.values())
        )
        if any(item.get("url") == url for item in existing):
            _LOGGER.debug("Pool card resource already registered: %s", url)
            return

        await resources.async_create_item({"res_type": "module", "url": url})
        _LOGGER.info("Auto-registered Lovelace resource: %s", url)
    except Exception as err:  # pylint: disable=broad-except
        _LOGGER.warning(
            "Could not auto-register pool card Lovelace resource. "
            "Add manually: Settings → Dashboards → Resources → URL: %s  "
            "Type: JavaScript module. Error: %s",
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
