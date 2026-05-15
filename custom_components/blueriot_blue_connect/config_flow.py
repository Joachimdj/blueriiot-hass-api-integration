"""Config flow for Blueriot Blue Connect integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .api import BlueriotBlueConnectCloudAPI
from .const import (
    CONF_LANGUAGE,
    CONF_PASSWORD,
    CONF_POLLING_INTERVAL,
    CONF_USERNAME,
    DEFAULT_LANGUAGE,
    DEFAULT_POLLING_INTERVAL,
    DOMAIN,
    SUPPORTED_LANGUAGES,
)

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Optional(CONF_LANGUAGE, default=DEFAULT_LANGUAGE): vol.In(SUPPORTED_LANGUAGES),
        vol.Optional(CONF_POLLING_INTERVAL, default=DEFAULT_POLLING_INTERVAL): int,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""

    username = data[CONF_USERNAME]
    password = data[CONF_PASSWORD]
    valid = await BlueriotBlueConnectCloudAPI.async_validate_credentials(
        username, password
    )

    if not valid:
        raise CannotConnect("Could not authenticate against cloud API")

    masked_username = username.split("@")[0]
    return {"title": f"Blueriot Blue Connect ({masked_username})"}


class BlueriotBlueConnectConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Blueriot Blue Connect."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)

                return self.async_create_entry(title=info["title"], data=user_input)

            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception: %s", err)
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )

    async def async_step_import(self, import_data: dict[str, Any]) -> config_entries.FlowResult:
        """Handle import from configuration.yaml."""
        return await self.async_step_user(import_data)


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""

    pass
