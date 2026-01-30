"""DataUpdateCoordinator for NextEnergy."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import NextEnergyApi, NextEnergyApiError
from .const import DOMAIN, SCAN_INTERVAL, CONF_COST_LEVEL, COST_LEVEL_MARKET_PLUS

_LOGGER = logging.getLogger(__name__)


class NextEnergyCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """NextEnergy data update coordinator."""

    def __init__(
        self, 
        hass: HomeAssistant, 
        api: NextEnergyApi,
        cost_level: str,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.api = api
        self.cost_level = cost_level

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from NextEnergy API."""
        try:
            # Get today's prices
            today_prices = await self.api.get_hourly_prices(
                date=datetime.now(),
                cost_level=self.cost_level
            )

            # Try to get tomorrow's prices (typically available after 14:00)
            tomorrow = datetime.now() + timedelta(days=1)
            tomorrow_prices = None
            tomorrow_available = False
            
            try:
                tomorrow_prices = await self.api.get_hourly_prices(
                    date=tomorrow,
                    cost_level=self.cost_level
                )
                # Check if we actually got prices
                if tomorrow_prices and tomorrow_prices.get("hourly_prices"):
                    tomorrow_available = True
                else:
                    tomorrow_prices = None
            except NextEnergyApiError as err:
                _LOGGER.debug("Tomorrow's prices not yet available: %s", err)
                tomorrow_prices = None

            return {
                "today": today_prices,
                "tomorrow": tomorrow_prices,
                "tomorrow_available": tomorrow_available,
                "cost_level": self.cost_level,
                "last_update": datetime.now().isoformat(),
            }

        except NextEnergyApiError as err:
            raise UpdateFailed(f"Error fetching NextEnergy data: {err}") from err