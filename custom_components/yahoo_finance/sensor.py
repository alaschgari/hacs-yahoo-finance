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

from .const import (
    DOMAIN, 
    CONF_SYMBOLS, 
    CONF_SHOW_CHANGE_PCT, 
    CONF_SHOW_HIGH, 
    CONF_SHOW_LOW
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Yahoo Finance sensor based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    
    show_change_pct = entry.data.get(CONF_SHOW_CHANGE_PCT, True)
    show_high = entry.data.get(CONF_SHOW_HIGH, True)
    show_low = entry.data.get(CONF_SHOW_LOW, True)

    entities = []
    for symbol in coordinator.symbols:
        entities.append(YahooFinanceSensor(coordinator, symbol, "price"))
        if show_change_pct:
            entities.append(YahooFinanceSensor(coordinator, symbol, "change_pct"))
        if show_high:
            entities.append(YahooFinanceSensor(coordinator, symbol, "high"))
        if show_low:
            entities.append(YahooFinanceSensor(coordinator, symbol, "low"))
    
    async_add_entities(entities)

class YahooFinanceSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Yahoo Finance sensor."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, symbol, sensor_type):
        """Initialize."""
        super().__init__(coordinator)
        self.symbol = symbol
        self.sensor_type = sensor_type
        self._attr_unique_id = f"{DOMAIN}_{symbol.lower()}_{sensor_type}"
        
        if sensor_type == "price":
            self._attr_name = f"{symbol}"
            self._attr_device_class = SensorDeviceClass.MONETARY
        elif sensor_type == "change_pct":
            self._attr_name = f"{symbol} Change %"
            self._attr_native_unit_of_measurement = "%"
            self._attr_icon = "mdi:percent"
        elif sensor_type == "high":
            self._attr_name = f"{symbol} Day High"
            self._attr_device_class = SensorDeviceClass.MONETARY
            self._attr_icon = "mdi:arrow-up-circle"
        elif sensor_type == "low":
            self._attr_name = f"{symbol} Day Low"
            self._attr_device_class = SensorDeviceClass.MONETARY
            self._attr_icon = "mdi:arrow-down-circle"

        self.entity_id = f"sensor.{DOMAIN}_{symbol.lower()}_{sensor_type}"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if not self.coordinator.data or self.symbol not in self.coordinator.data:
            return None
        
        data = self.coordinator.data[self.symbol]
        if self.sensor_type == "price":
            return data.get("regularMarketPrice")
        elif self.sensor_type == "change_pct":
            pct = data.get("regularMarketChangePercent")
            return round(pct, 2) if pct is not None else None
        elif self.sensor_type == "high":
            return data.get("dayHigh")
        elif self.sensor_type == "low":
            return data.get("dayLow")
        return None

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        if self.sensor_type == "change_pct":
            return "%"
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
