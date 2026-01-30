"""Sensor platform for NextEnergy."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CURRENCY_EURO
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_COST_LEVEL, COST_LEVEL_MARKET_PLUS
from .coordinator import NextEnergyCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up NextEnergy sensor entities."""
    coordinator: NextEnergyCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    entities = [
        # Today's sensors
        NextEnergyCurrentPriceSensor(coordinator, entry),
        NextEnergyGasPriceSensor(coordinator, entry),
        NextEnergyAverageOffPeakSensor(coordinator, entry),
        NextEnergyMinPriceSensor(coordinator, entry),
        NextEnergyMaxPriceSensor(coordinator, entry),
        NextEnergyAveragePriceSensor(coordinator, entry),
        NextEnergyHourlyPricesSensor(coordinator, entry),
        # Tomorrow's sensors
        NextEnergyTomorrowAvailableSensor(coordinator, entry),
        NextEnergyTomorrowAveragePriceSensor(coordinator, entry),
        NextEnergyTomorrowMinPriceSensor(coordinator, entry),
        NextEnergyTomorrowMaxPriceSensor(coordinator, entry),
        NextEnergyTomorrowHourlyPricesSensor(coordinator, entry),
    ]

    async_add_entities(entities)


class NextEnergySensorBase(CoordinatorEntity[NextEnergyCoordinator], SensorEntity):
    """Base class for NextEnergy sensors."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: NextEnergyCoordinator,
        entry: ConfigEntry,
        sensor_type: str,
        name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{sensor_type}"
        self._attr_name = name
        self._entry = entry

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        cost_level = self._entry.data.get(CONF_COST_LEVEL, COST_LEVEL_MARKET_PLUS)
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=f"NextEnergy {cost_level}",
            manufacturer="NextEnergy",
            model=f"{cost_level} Tariff",
        )


# ========== TODAY'S SENSORS ==========

class NextEnergyCurrentPriceSensor(NextEnergySensorBase):
    """Sensor for current electricity price."""

    _attr_native_unit_of_measurement = f"{CURRENCY_EURO}/kWh"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:flash"

    def __init__(self, coordinator: NextEnergyCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, "current_price", "Current Electricity Price")

    @property
    def native_value(self) -> float | None:
        """Return the current price."""
        if self.coordinator.data and "today" in self.coordinator.data:
            return self.coordinator.data["today"].get("current_price")
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        attrs = {}
        if self.coordinator.data and "today" in self.coordinator.data:
            today = self.coordinator.data["today"]
            attrs["current_hour"] = today.get("current_hour")
            attrs["date"] = today.get("date")
            attrs["cost_level"] = self.coordinator.data.get("cost_level")
            attrs["last_update"] = self.coordinator.data.get("last_update")
        return attrs


class NextEnergyGasPriceSensor(NextEnergySensorBase):
    """Sensor for gas price."""

    _attr_native_unit_of_measurement = f"{CURRENCY_EURO}/m³"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:fire"

    def __init__(self, coordinator: NextEnergyCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, "gas_price", "Gas Price")

    @property
    def native_value(self) -> float | None:
        """Return the gas price."""
        if self.coordinator.data and "today" in self.coordinator.data:
            return self.coordinator.data["today"].get("gas_price")
        return None


class NextEnergyAverageOffPeakSensor(NextEnergySensorBase):
    """Sensor for average off-peak price."""

    _attr_native_unit_of_measurement = f"{CURRENCY_EURO}/kWh"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:weather-night"

    def __init__(self, coordinator: NextEnergyCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, "average_offpeak", "Average Off-Peak Price")

    @property
    def native_value(self) -> float | None:
        """Return the average off-peak price."""
        if self.coordinator.data and "today" in self.coordinator.data:
            return self.coordinator.data["today"].get("average_off_peak")
        return None


class NextEnergyMinPriceSensor(NextEnergySensorBase):
    """Sensor for minimum price today."""

    _attr_native_unit_of_measurement = f"{CURRENCY_EURO}/kWh"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:arrow-down-bold"

    def __init__(self, coordinator: NextEnergyCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, "min_price", "Minimum Price Today")

    @property
    def native_value(self) -> float | None:
        """Return the minimum price."""
        if self.coordinator.data and "today" in self.coordinator.data:
            return self.coordinator.data["today"].get("min_price")
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        if self.coordinator.data and "today" in self.coordinator.data:
            return {"hour": self.coordinator.data["today"].get("min_price_hour")}
        return {}


class NextEnergyMaxPriceSensor(NextEnergySensorBase):
    """Sensor for maximum price today."""

    _attr_native_unit_of_measurement = f"{CURRENCY_EURO}/kWh"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:arrow-up-bold"

    def __init__(self, coordinator: NextEnergyCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, "max_price", "Maximum Price Today")

    @property
    def native_value(self) -> float | None:
        """Return the maximum price."""
        if self.coordinator.data and "today" in self.coordinator.data:
            return self.coordinator.data["today"].get("max_price")
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        if self.coordinator.data and "today" in self.coordinator.data:
            return {"hour": self.coordinator.data["today"].get("max_price_hour")}
        return {}


class NextEnergyAveragePriceSensor(NextEnergySensorBase):
    """Sensor for average price today."""

    _attr_native_unit_of_measurement = f"{CURRENCY_EURO}/kWh"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:chart-line"

    def __init__(self, coordinator: NextEnergyCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, "average_price", "Average Price Today")

    @property
    def native_value(self) -> float | None:
        """Return the average price."""
        if self.coordinator.data and "today" in self.coordinator.data:
            return self.coordinator.data["today"].get("average_price")
        return None


class NextEnergyHourlyPricesSensor(NextEnergySensorBase):
    """Sensor containing all hourly prices for today as attributes."""

    _attr_native_unit_of_measurement = f"{CURRENCY_EURO}/kWh"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:clock-outline"

    def __init__(self, coordinator: NextEnergyCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, "hourly_prices_today", "Hourly Prices Today")

    @property
    def native_value(self) -> float | None:
        """Return the current hour price."""
        if self.coordinator.data and "today" in self.coordinator.data:
            return self.coordinator.data["today"].get("current_price")
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return all hourly prices as attributes."""
        attrs = {}
        if self.coordinator.data and "today" in self.coordinator.data:
            today = self.coordinator.data["today"]
            hourly = today.get("hourly_prices", {})
            for hour, price in hourly.items():
                hour_key = f"hour_{int(hour):02d}" if isinstance(hour, (int, float)) else f"hour_{hour}"
                attrs[hour_key] = price
            attrs["average"] = today.get("average_price")
            attrs["min"] = today.get("min_price")
            attrs["min_hour"] = today.get("min_price_hour")
            attrs["max"] = today.get("max_price")
            attrs["max_hour"] = today.get("max_price_hour")
            attrs["date"] = today.get("date")
        return attrs


# ========== TOMORROW'S SENSORS ==========

class NextEnergyTomorrowAvailableSensor(NextEnergySensorBase):
    """Sensor indicating if tomorrow's prices are available."""

    _attr_icon = "mdi:calendar-check"

    def __init__(self, coordinator: NextEnergyCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, "tomorrow_available", "Tomorrow Prices Available")

    @property
    def native_value(self) -> bool:
        """Return if tomorrow's prices are available."""
        if self.coordinator.data:
            return self.coordinator.data.get("tomorrow_available", False)
        return False


class NextEnergyTomorrowAveragePriceSensor(NextEnergySensorBase):
    """Sensor for average price tomorrow."""

    _attr_native_unit_of_measurement = f"{CURRENCY_EURO}/kWh"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:chart-line"

    def __init__(self, coordinator: NextEnergyCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, "average_price_tomorrow", "Average Price Tomorrow")

    @property
    def native_value(self) -> float | None:
        """Return the average price for tomorrow."""
        if self.coordinator.data and self.coordinator.data.get("tomorrow"):
            return self.coordinator.data["tomorrow"].get("average_price")
        return None

    @property
    def available(self) -> bool:
        """Return if sensor is available."""
        return self.coordinator.data is not None and self.coordinator.data.get("tomorrow_available", False)


class NextEnergyTomorrowMinPriceSensor(NextEnergySensorBase):
    """Sensor for minimum price tomorrow."""

    _attr_native_unit_of_measurement = f"{CURRENCY_EURO}/kWh"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:arrow-down-bold"

    def __init__(self, coordinator: NextEnergyCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, "min_price_tomorrow", "Minimum Price Tomorrow")

    @property
    def native_value(self) -> float | None:
        """Return the minimum price for tomorrow."""
        if self.coordinator.data and self.coordinator.data.get("tomorrow"):
            return self.coordinator.data["tomorrow"].get("min_price")
        return None

    @property
    def available(self) -> bool:
        """Return if sensor is available."""
        return self.coordinator.data is not None and self.coordinator.data.get("tomorrow_available", False)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        if self.coordinator.data and self.coordinator.data.get("tomorrow"):
            return {"hour": self.coordinator.data["tomorrow"].get("min_price_hour")}
        return {}


class NextEnergyTomorrowMaxPriceSensor(NextEnergySensorBase):
    """Sensor for maximum price tomorrow."""

    _attr_native_unit_of_measurement = f"{CURRENCY_EURO}/kWh"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:arrow-up-bold"

    def __init__(self, coordinator: NextEnergyCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, "max_price_tomorrow", "Maximum Price Tomorrow")

    @property
    def native_value(self) -> float | None:
        """Return the maximum price for tomorrow."""
        if self.coordinator.data and self.coordinator.data.get("tomorrow"):
            return self.coordinator.data["tomorrow"].get("max_price")
        return None

    @property
    def available(self) -> bool:
        """Return if sensor is available."""
        return self.coordinator.data is not None and self.coordinator.data.get("tomorrow_available", False)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        if self.coordinator.data and self.coordinator.data.get("tomorrow"):
            return {"hour": self.coordinator.data["tomorrow"].get("max_price_hour")}
        return {}


class NextEnergyTomorrowHourlyPricesSensor(NextEnergySensorBase):
    """Sensor containing all hourly prices for tomorrow as attributes."""

    _attr_native_unit_of_measurement = f"{CURRENCY_EURO}/kWh"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:calendar-clock"

    def __init__(self, coordinator: NextEnergyCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, entry, "hourly_prices_tomorrow", "Hourly Prices Tomorrow")

    @property
    def native_value(self) -> float | None:
        """Return the average price for tomorrow."""
        if self.coordinator.data and self.coordinator.data.get("tomorrow"):
            return self.coordinator.data["tomorrow"].get("average_price")
        return None

    @property
    def available(self) -> bool:
        """Return if sensor is available."""
        return self.coordinator.data is not None and self.coordinator.data.get("tomorrow_available", False)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return all hourly prices for tomorrow as attributes."""
        attrs = {}
        if self.coordinator.data and self.coordinator.data.get("tomorrow"):
            tomorrow = self.coordinator.data["tomorrow"]
            hourly = tomorrow.get("hourly_prices", {})
            for hour, price in hourly.items():
                hour_key = f"hour_{int(hour):02d}" if isinstance(hour, (int, float)) else f"hour_{hour}"
                attrs[hour_key] = price
            attrs["average"] = tomorrow.get("average_price")
            attrs["min"] = tomorrow.get("min_price")
            attrs["min_hour"] = tomorrow.get("min_price_hour")
            attrs["max"] = tomorrow.get("max_price")
            attrs["max_hour"] = tomorrow.get("max_price_hour")
            attrs["date"] = tomorrow.get("date")
        return attrs