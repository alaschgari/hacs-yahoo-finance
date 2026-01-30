"""The Yahoo Finance integration."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_SYMBOLS, CONF_SCAN_INTERVAL, CONF_ECO_THRESHOLD
from .coordinator import YahooFinanceDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Yahoo Finance from a config entry."""
    # Prioritize options over data
    conf = {**entry.data, **entry.options}
    symbols = conf.get(CONF_SYMBOLS, {})
    scan_interval = conf.get(CONF_SCAN_INTERVAL, 120)
    eco_threshold = conf.get(CONF_ECO_THRESHOLD, 600)
    
    coordinator = YahooFinanceDataUpdateCoordinator(hass, symbols, scan_interval, eco_threshold)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    # Register update listener
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update options."""
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
