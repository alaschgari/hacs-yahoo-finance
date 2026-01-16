"""Sensor platform for Yahoo Finance integration."""
import logging

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
    SensorDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Yahoo Finance sensor based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = []
    for symbol in coordinator.symbols:
        entities.append(YahooFinanceSensor(coordinator, symbol))
    
    async_add_entities(entities)

class YahooFinanceSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Yahoo Finance sensor."""

    _attr_has_entity_name = True
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_device_class = SensorDeviceClass.MONETARY

    def __init__(self, coordinator, symbol):
        """Initialize."""
        super().__init__(coordinator)
        self.symbol = symbol
        self._attr_unique_id = f"{DOMAIN}_{symbol}"
        self._attr_name = f"{symbol}"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.coordinator.data and self.symbol in self.coordinator.data:
            data = self.coordinator.data[self.symbol]
            return data.get("regularMarketPrice") or data.get("currentPrice")
        return None

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        if self.coordinator.data and self.symbol in self.coordinator.data:
            return self.coordinator.data[self.symbol].get("currency")
        return None

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        if self.coordinator.data and self.symbol in self.coordinator.data:
            info = self.coordinator.data[self.symbol]
            pct_change = info.get("regularMarketChangePercent")
            return {
                "regularMarketChangePercent": round(pct_change, 2) if pct_change is not None else None,
                "regularMarketDayHigh": info.get("dayHigh") or info.get("regularMarketDayHigh"),
                "regularMarketDayLow": info.get("dayLow") or info.get("regularMarketDayLow"),
                "longName": info.get("longName"),
                "shortName": info.get("shortName"),
            }
        return {}
