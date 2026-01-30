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

    last_exception = coordinator.last_exception
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
            "last_exception": str(last_exception) if last_exception else None,
            "update_interval": str(coordinator.update_interval),
            "cost_level": coordinator.cost_level,
        },
        "api": {
            "authenticated": getattr(api, "authenticated", None),
            "module_version": getattr(api, "module_version", None),
            "api_version_prices": getattr(api, "api_version_prices", None),
            "api_version_costs": getattr(api, "api_version_costs", None),
        },
        "data": (
            async_redact_data(coordinator.data, TO_REDACT) if coordinator.data else None
        ),
    }

    return diagnostics_data
