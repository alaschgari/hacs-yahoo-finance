"""Config flow for Yahoo Finance integration."""
import logging
from typing import Any

import voluptuous as vol
import yfinance as yf
import requests
from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
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
    CONF_SCAN_INTERVAL,
    CONF_ECO_THRESHOLD,
    CONF_BASE_CURRENCY,
    CONF_EXT_HOURS,
    CONF_SHOW_ESG,
    CONF_SHOW_PERFORMANCE,
    CONF_SHOW_MARKET_STATUS,
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
        vol.Optional(CONF_SHOW_ESG, default=False): bool,
        vol.Optional(CONF_SHOW_PERFORMANCE, default=False): bool,
        vol.Optional(CONF_SHOW_MARKET_STATUS, default=False): bool,
        vol.Optional(CONF_EXT_HOURS, default=False): bool,
        vol.Optional(CONF_BASE_CURRENCY, default="USD"): vol.In(["USD", "EUR", "CHF", "GBP", "JPY", "CAD", "AUD"]),
        vol.Optional(CONF_SCAN_INTERVAL, default=120): vol.All(vol.Coerce(int), vol.Range(min=30)),
        vol.Optional(CONF_ECO_THRESHOLD, default=600): vol.All(vol.Coerce(int), vol.Range(min=60)),
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
        CONF_SHOW_ESG: data.get(CONF_SHOW_ESG, False),
        CONF_SHOW_PERFORMANCE: data.get(CONF_SHOW_PERFORMANCE, False),
        CONF_SHOW_MARKET_STATUS: data.get(CONF_SHOW_MARKET_STATUS, False),
        CONF_EXT_HOURS: data.get(CONF_EXT_HOURS, False),
        CONF_BASE_CURRENCY: data.get(CONF_BASE_CURRENCY, "USD"),
        CONF_SCAN_INTERVAL: data.get(CONF_SCAN_INTERVAL, 120),
        CONF_ECO_THRESHOLD: data.get(CONF_ECO_THRESHOLD, 600),
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

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return OptionsFlowHandler()


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Yahoo Finance options."""



    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                return self.async_create_entry(title="", data=info)
            except vol.Invalid as err:
                errors["base"] = str(err)
            except Exception:
                errors["base"] = "unknown"

        # Convert symbols dict back to string for editing
        current_symbols_dict = self.config_entry.options.get(
            CONF_SYMBOLS, self.config_entry.data.get(CONF_SYMBOLS, {})
        )
        symbol_list = []
        for sym, amt in current_symbols_dict.items():
            if amt > 0:
                symbol_list.append(f"{sym}:{amt}")
            else:
                symbol_list.append(sym)
        
        symbols_string = ", ".join(symbol_list)

        options_schema = vol.Schema(
            {
                vol.Required(CONF_SYMBOLS, default=symbols_string): str,
                vol.Optional(
                    CONF_SHOW_CHANGE_PCT, 
                    default=self.config_entry.options.get(
                        CONF_SHOW_CHANGE_PCT, 
                        self.config_entry.data.get(CONF_SHOW_CHANGE_PCT, True)
                    )
                ): bool,
                vol.Optional(
                    CONF_SHOW_HIGH, 
                    default=self.config_entry.options.get(
                        CONF_SHOW_HIGH, 
                        self.config_entry.data.get(CONF_SHOW_HIGH, True)
                    )
                ): bool,
                vol.Optional(
                    CONF_SHOW_LOW, 
                    default=self.config_entry.options.get(
                        CONF_SHOW_LOW, 
                        self.config_entry.data.get(CONF_SHOW_LOW, True)
                    )
                ): bool,
                vol.Optional(
                    CONF_SHOW_MARKET_CAP, 
                    default=self.config_entry.options.get(
                        CONF_SHOW_MARKET_CAP, 
                        self.config_entry.data.get(CONF_SHOW_MARKET_CAP, False)
                    )
                ): bool,
                vol.Optional(
                    CONF_SHOW_VOLUME, 
                    default=self.config_entry.options.get(
                        CONF_SHOW_VOLUME, 
                        self.config_entry.data.get(CONF_SHOW_VOLUME, False)
                    )
                ): bool,
                vol.Optional(
                    CONF_SHOW_OPEN, 
                    default=self.config_entry.options.get(
                        CONF_SHOW_OPEN, 
                        self.config_entry.data.get(CONF_SHOW_OPEN, False)
                    )
                ): bool,
                vol.Optional(
                    CONF_SHOW_52WK_HIGH, 
                    default=self.config_entry.options.get(
                        CONF_SHOW_52WK_HIGH, 
                        self.config_entry.data.get(CONF_SHOW_52WK_HIGH, False)
                    )
                ): bool,
                vol.Optional(
                    CONF_SHOW_52WK_LOW, 
                    default=self.config_entry.options.get(
                        CONF_SHOW_52WK_LOW, 
                        self.config_entry.data.get(CONF_SHOW_52WK_LOW, False)
                    )
                ): bool,
                vol.Optional(
                    CONF_SHOW_DIVIDEND, 
                    default=self.config_entry.options.get(
                        CONF_SHOW_DIVIDEND, 
                        self.config_entry.data.get(CONF_SHOW_DIVIDEND, False)
                    )
                ): bool,
                vol.Optional(
                    CONF_SHOW_EARNINGS, 
                    default=self.config_entry.options.get(
                        CONF_SHOW_EARNINGS, 
                        self.config_entry.data.get(CONF_SHOW_EARNINGS, False)
                    )
                ): bool,
                vol.Optional(
                    CONF_SHOW_PE, 
                    default=self.config_entry.options.get(
                        CONF_SHOW_PE, 
                        self.config_entry.data.get(CONF_SHOW_PE, False)
                    )
                ): bool,
                vol.Optional(
                    CONF_SHOW_TREND, 
                    default=self.config_entry.options.get(
                        CONF_SHOW_TREND, 
                        self.config_entry.data.get(CONF_SHOW_TREND, False)
                    )
                ): bool,
                vol.Optional(
                    CONF_SHOW_ESG, 
                    default=self.config_entry.options.get(
                        CONF_SHOW_ESG, 
                        self.config_entry.data.get(CONF_SHOW_ESG, False)
                    )
                ): bool,
                vol.Optional(
                    CONF_SHOW_PERFORMANCE, 
                    default=self.config_entry.options.get(
                        CONF_SHOW_PERFORMANCE, 
                        self.config_entry.data.get(CONF_SHOW_PERFORMANCE, False)
                    )
                ): bool,
                vol.Optional(
                    CONF_SHOW_MARKET_STATUS, 
                    default=self.config_entry.options.get(
                        CONF_SHOW_MARKET_STATUS, 
                        self.config_entry.data.get(CONF_SHOW_MARKET_STATUS, False)
                    )
                ): bool,
                vol.Optional(
                    CONF_EXT_HOURS, 
                    default=self.config_entry.options.get(
                        CONF_EXT_HOURS, 
                        self.config_entry.data.get(CONF_EXT_HOURS, False)
                    )
                ): bool,
                vol.Optional(
                    CONF_BASE_CURRENCY, 
                    default=self.config_entry.options.get(
                        CONF_BASE_CURRENCY, 
                        self.config_entry.data.get(CONF_BASE_CURRENCY, "USD")
                    )
                ): vol.In(["USD", "EUR", "CHF", "GBP", "JPY", "CAD", "AUD"]),
                vol.Optional(
                    CONF_SCAN_INTERVAL, 
                    default=self.config_entry.options.get(
                        CONF_SCAN_INTERVAL, 
                        self.config_entry.data.get(CONF_SCAN_INTERVAL, 120)
                    )
                ): vol.All(vol.Coerce(int), vol.Range(min=30)),
                vol.Optional(
                    CONF_ECO_THRESHOLD, 
                    default=self.config_entry.options.get(
                        CONF_ECO_THRESHOLD, 
                        self.config_entry.data.get(CONF_ECO_THRESHOLD, 600)
                    )
                ): vol.All(vol.Coerce(int), vol.Range(min=60)),
            }
        )

        return self.async_show_form(
            step_id="init", data_schema=options_schema, errors=errors
        )
