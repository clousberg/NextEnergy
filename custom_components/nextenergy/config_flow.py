"""Config flow for NextEnergy integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .api import NextEnergyApi, NextEnergyAuthError, NextEnergyApiError
from .const import (
    DOMAIN,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_COST_LEVEL,
    COST_LEVEL_MARKET,
    COST_LEVEL_MARKET_PLUS,
    COST_LEVEL_OPTIONS,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Required(CONF_COST_LEVEL, default=COST_LEVEL_MARKET_PLUS): vol.In(COST_LEVEL_OPTIONS),
    }
)


class NextEnergyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for NextEnergy."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Check if already configured
            await self.async_set_unique_id(user_input[CONF_USERNAME].lower())
            self._abort_if_unique_id_configured()

            # Test authentication
            api = NextEnergyApi(
                username=user_input[CONF_USERNAME],
                password=user_input[CONF_PASSWORD],
            )

            try:
                await api.authenticate()
                await api.close()
            except NextEnergyAuthError:
                errors["base"] = "invalid_auth"
            except NextEnergyApiError:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=f"NextEnergy ({user_input[CONF_USERNAME]}) - {user_input[CONF_COST_LEVEL]}",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_reauth(
        self, entry_data: dict[str, Any]
    ) -> FlowResult:
        """Handle reauth flow."""
        return await self.async_step_user()

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> NextEnergyOptionsFlow:
        """Get the options flow for this handler."""
        return NextEnergyOptionsFlow(config_entry)


class NextEnergyOptionsFlow(config_entries.OptionsFlow):
    """Handle NextEnergy options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            # Update the config entry with new options
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data={**self.config_entry.data, **user_input},
            )
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_COST_LEVEL,
                        default=self.config_entry.data.get(CONF_COST_LEVEL, COST_LEVEL_MARKET_PLUS),
                    ): vol.In(COST_LEVEL_OPTIONS),
                }
            ),
        )