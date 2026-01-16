"""Config flow for Yahoo Finance integration."""
import logging
from typing import Any

import voluptuous as vol
import yfinance as yf
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, CONF_SYMBOLS

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SYMBOLS): str,
    }
)

async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    symbols = [s.strip().upper() for s in data[CONF_SYMBOLS].split(",")]
    
    # Check if symbols are valid (at least one)
    valid_symbols = []
    for symbol in symbols:
        ticker = yf.Ticker(symbol)
        # Check if we can get some fast info to verify symbol
        try:
            info = await hass.async_add_executor_job(lambda: ticker.info)
            if info and "symbol" in info:
                valid_symbols.append(symbol)
        except Exception:
            _LOGGER.warning("Could not validate symbol: %s", symbol)
            continue
            
    if not valid_symbols:
        raise vol.Invalid("No valid symbols found")

    return {"title": ", ".join(valid_symbols), CONF_SYMBOLS: valid_symbols}

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
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )
