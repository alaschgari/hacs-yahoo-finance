"""DataUpdateCoordinator for Yahoo Finance integration."""
from datetime import timedelta
import logging

import yfinance as yf
import requests
import asyncio
import random
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL, HEADERS

_LOGGER = logging.getLogger(__name__)

class YahooFinanceDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Yahoo Finance data."""

    def __init__(self, hass, symbols):
        """Initialize."""
        self.symbols = symbols
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self):
        """Fetch data from Yahoo Finance."""
        try:
            data = {}
            for symbol in self.symbols:
                # Small delay to avoid 429
                await asyncio.sleep(random.uniform(1.0, 2.0))
                
                ticker = yf.Ticker(symbol, session=self.session)
                
                def fetch_fast_info(t):
                    fi = t.fast_info
                    # Access attributes inside executor to avoid blocking
                    return {
                        "regularMarketPrice": fi.last_price,
                        "currency": fi.currency,
                        "regularMarketChangePercent": (fi.last_price - fi.previous_close) / fi.previous_close * 100 if fi.last_price and fi.previous_close else None,
                        "dayHigh": fi.day_high,
                        "dayLow": fi.day_low,
                        "symbol": fi.symbol,
                        # fast_info doesn't have longName/shortName easily, we'll use symbol
                        "longName": fi.symbol,
                        "shortName": fi.symbol,
                    }

                info = await self.hass.async_add_executor_job(fetch_fast_info, ticker)
                if info:
                    data[symbol] = info
            return data
        except Exception as err:
            raise UpdateFailed(f"Error communicating with Yahoo Finance API: {err}")
