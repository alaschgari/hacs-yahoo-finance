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
    }
)

async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    symbols = [s.strip().upper() for s in data[CONF_SYMBOLS].split(",")]
    
    # We disable API validation here to avoid 429/Blocking calls during setup
    # Just check if the symbols look like valid ticker symbols
    valid_symbols = []
    for symbol in symbols:
        if symbol and all(c.isalnum() or c in "-.=_" for c in symbol):
            valid_symbols.append(symbol)
            
    if not valid_symbols:
        raise vol.Invalid("invalid_symbols")

    return {
        "title": ", ".join(valid_symbols), 
        CONF_SYMBOLS: valid_symbols,
        CONF_SHOW_CHANGE_PCT: data.get(CONF_SHOW_CHANGE_PCT, True),
        CONF_SHOW_HIGH: data.get(CONF_SHOW_HIGH, True),
        CONF_SHOW_LOW: data.get(CONF_SHOW_LOW, True),
        CONF_SHOW_MARKET_CAP: data.get(CONF_SHOW_MARKET_CAP, False),
        CONF_SHOW_VOLUME: data.get(CONF_SHOW_VOLUME, False),
        CONF_SHOW_OPEN: data.get(CONF_SHOW_OPEN, False),
        CONF_SHOW_52WK_HIGH: data.get(CONF_SHOW_52WK_HIGH, False),
        CONF_SHOW_52WK_LOW: data.get(CONF_SHOW_52WK_LOW, False),
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
