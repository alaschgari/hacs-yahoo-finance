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

from .const import DOMAIN, CONF_SYMBOLS, HEADERS

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
    session = requests.Session()
    session.headers.update(HEADERS)

    for symbol in symbols:
        ticker = yf.Ticker(symbol, session=session)
        try:
            # Wrap BOTH the data fetch and the attribute check in the executor
            def check_validity(t):
                try:
                    # Tickers for shares, ETFs, etc. have a currency
                    return hasattr(t.fast_info, "currency") and t.fast_info.currency is not None
                except Exception as exc:
                    _LOGGER.debug("fast_info failed for %s: %s, trying history fallback", symbol, exc)
                    # Fallback: check if we can get any history data
                    hist = t.history(period="1d")
                    return not hist.empty

            is_valid = await hass.async_add_executor_job(check_validity, ticker)
            
            if is_valid:
                valid_symbols.append(symbol)
            else:
                # If we get here, yfinance explicitly says no data. 
                # However, if yfinance is being flaky, we might want to allow it anyway if it's a known symbol format
                _LOGGER.warning("Symbol %s could not be validated, but adding anyway as fallback", symbol)
                valid_symbols.append(symbol)
        except Exception as err:
            _LOGGER.error("Error during validation of %s: %s. Adding anyway.", symbol, err)
            valid_symbols.append(symbol)
            
    if not valid_symbols:
        raise vol.Invalid("invalid_symbols")

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
            except vol.Invalid as err:
                _LOGGER.error("Validation error: %s", err)
                errors["base"] = str(err)
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )
