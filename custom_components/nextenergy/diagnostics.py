"""Diagnostics support for NextEnergy."""
from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_PASSWORD, CONF_USERNAME, DOMAIN

TO_REDACT = {
    CONF_USERNAME,
    CONF_PASSWORD,
    "username",
    "password",
    "email",
    "token",
    "access_token",
    "refresh_token",
    "csrf_token",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    api = hass.data[DOMAIN][entry.entry_id]["api"]

    diagnostics_data = {
        "config_entry": {
            "entry_id": entry.entry_id,
            "version": entry.version,
            "domain": entry.domain,
            "title": entry.title,
            "data": async_redact_data(entry.data, TO_REDACT),
            "options": async_redact_data(dict(entry.options), TO_REDACT),
        },
        "coordinator": {
            "last_update_success": coordinator.last_update_success,
            "last_exception": str(coordinator.last_exception) if coordinator.last_exception else None,
            "update_interval": str(coordinator.update_interval),
            "cost_level": coordinator.cost_level,
        },
        "api": {
            "authenticated": api.authenticated if hasattr(api, "authenticated") else None,
            "module_version": api.module_version if hasattr(api, "module_version") else None,
            "api_version_prices": api.api_version_prices if hasattr(api, "api_version_prices") else None,
            "api_version_costs": api.api_version_costs if hasattr(api, "api_version_costs") else None,
        },
        "data": async_redact_data(coordinator.data, TO_REDACT) if coordinator.data else None,
    }

    return diagnostics_data
