"""Config flow for Yahoo Finance integration."""
import logging
from typing import Any

import voluptuous as vol
import yfinance as yf
import requests
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv

from .const import (
    DOMAIN, 
    CONF_SYMBOLS, 
    CONF_SHOW_CHANGE_PCT, 
    CONF_SHOW_HIGH, 
    CONF_SHOW_LOW, 
    CONF_SHOW_MARKET_CAP,
    CONF_SHOW_VOLUME,
    CONF_SHOW_OPEN,
    CONF_SHOW_52WK_HIGH,
    CONF_SHOW_52WK_LOW,
    CONF_SHOW_DIVIDEND,
    CONF_SHOW_EARNINGS,
    CONF_SHOW_PE,
    CONF_SHOW_TREND,
    get_headers
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SYMBOLS): str,
        vol.Optional(CONF_SHOW_CHANGE_PCT, default=True): bool,
        vol.Optional(CONF_SHOW_HIGH, default=True): bool,
        vol.Optional(CONF_SHOW_LOW, default=True): bool,
        vol.Optional(CONF_SHOW_MARKET_CAP, default=False): bool,
        vol.Optional(CONF_SHOW_VOLUME, default=False): bool,
        vol.Optional(CONF_SHOW_OPEN, default=False): bool,
        vol.Optional(CONF_SHOW_52WK_HIGH, default=False): bool,
        vol.Optional(CONF_SHOW_52WK_LOW, default=False): bool,
        vol.Optional(CONF_SHOW_DIVIDEND, default=False): bool,
        vol.Optional(CONF_SHOW_EARNINGS, default=False): bool,
        vol.Optional(CONF_SHOW_PE, default=False): bool,
        vol.Optional(CONF_SHOW_TREND, default=False): bool,
    }
)

async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    raw_symbols = [s.strip().upper() for s in data[CONF_SYMBOLS].split(",")]
    
    # We disable API validation here to avoid 429/Blocking calls during setup
    # Just check if the symbols look like valid ticker symbols
    # Support format SYMBOL:AMOUNT (e.g. AAPL:10)
    symbol_definitions = {}
    for entry in raw_symbols:
        if not entry:
            continue
            
        parts = entry.split(":")
        symbol = parts[0].strip()
        amount = 0.0
        
        if len(parts) > 1:
            try:
                amount = float(parts[1].strip())
            except ValueError:
                 _LOGGER.warning("Invalid amount for symbol %s: %s", symbol, parts[1])
        
        if symbol and all(c.isalnum() or c in "-.=_" for c in symbol):
            symbol_definitions[symbol] = amount
            
    if not symbol_definitions:
        raise vol.Invalid("invalid_symbols")

    return {
        "title": ", ".join(symbol_definitions.keys()), 
        CONF_SYMBOLS: symbol_definitions,
        CONF_SHOW_CHANGE_PCT: data.get(CONF_SHOW_CHANGE_PCT, True),
        CONF_SHOW_HIGH: data.get(CONF_SHOW_HIGH, True),
        CONF_SHOW_LOW: data.get(CONF_SHOW_LOW, True),
        CONF_SHOW_MARKET_CAP: data.get(CONF_SHOW_MARKET_CAP, False),
        CONF_SHOW_VOLUME: data.get(CONF_SHOW_VOLUME, False),
        CONF_SHOW_52WK_LOW: data.get(CONF_SHOW_52WK_LOW, False),
        CONF_SHOW_DIVIDEND: data.get(CONF_SHOW_DIVIDEND, False),
        CONF_SHOW_EARNINGS: data.get(CONF_SHOW_EARNINGS, False),
        CONF_SHOW_PE: data.get(CONF_SHOW_PE, False),
        CONF_SHOW_TREND: data.get(CONF_SHOW_TREND, False),
    }

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Yahoo Finance."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                return self.async_create_entry(title=info["title"], data=info)
            except vol.Invalid as err:
                _LOGGER.error("Validation error: %s", err)
                errors["base"] = str(err)
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )
