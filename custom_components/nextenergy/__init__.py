"""NextEnergy integration for Home Assistant."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady

from .api import NextEnergyApi, NextEnergyApiError, NextEnergyAuthError
from .const import (
    CONF_COST_LEVEL,
    CONF_PASSWORD,
    CONF_USERNAME,
    COST_LEVEL_MARKET_PLUS,
    DOMAIN,
)
from .coordinator import NextEnergyCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up NextEnergy from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    api = NextEnergyApi(
        username=entry.data[CONF_USERNAME],
        password=entry.data[CONF_PASSWORD],
    )

    try:
        await api.authenticate()
    except NextEnergyAuthError as err:
        raise ConfigEntryAuthFailed(f"Authentication failed: {err}") from err
    except NextEnergyApiError as err:
        raise ConfigEntryNotReady(f"Unable to connect to NextEnergy: {err}") from err

    cost_level = entry.data.get(CONF_COST_LEVEL, COST_LEVEL_MARKET_PLUS)
    coordinator = NextEnergyCoordinator(hass, api, cost_level)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        "api": api,
        "coordinator": coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register update listener for options changes
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    return True


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        data = hass.data[DOMAIN].pop(entry.entry_id)
        await data["api"].close()

    return unload_ok
