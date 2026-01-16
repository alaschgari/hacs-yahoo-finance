"""DataUpdateCoordinator for Yahoo Finance integration."""
from datetime import timedelta
import logging

import yfinance as yf
import requests
import asyncio
import random
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL, get_headers

_LOGGER = logging.getLogger(__name__)

class YahooFinanceDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Yahoo Finance data."""

    def __init__(self, hass, symbols):
        """Initialize."""
        self.symbols = symbols
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self):
        """Fetch data from Yahoo Finance."""
        data = {}
        for symbol in self.symbols:
            # Random delay before EACH symbol to avoid detection
            await asyncio.sleep(random.uniform(2.0, 5.0))
            
            # Create a fresh session with random headers for each symbol
            session = requests.Session()
            session.headers.update(get_headers())
            
            ticker = yf.Ticker(symbol, session=session)
            
            def fetch_fast_info(t):
                try:
                    fi = t.fast_info
                    return {
                        "regularMarketPrice": fi.last_price,
                        "currency": fi.currency,
                        "regularMarketChangePercent": (fi.last_price - fi.previous_close) / fi.previous_close * 100 if fi.last_price and fi.previous_close else None,
                        "dayHigh": fi.day_high,
                        "dayLow": fi.day_low,
                        "symbol": fi.symbol,
                        "longName": fi.symbol,
                        "shortName": fi.symbol,
                    }
                except Exception as ex:
                    _LOGGER.warning("Error fetching %s: %s", symbol, ex)
                    return None

            info = await self.hass.async_add_executor_job(fetch_fast_info, ticker)
            if info:
                data[symbol] = info
            else:
                _LOGGER.info("No data for %s, skipping this update", symbol)
                
        if not data:
            raise UpdateFailed("Failed to fetch data for any symbol")
        return data
