"""DataUpdateCoordinator for Yahoo Finance integration."""
from datetime import timedelta
import logging

import yfinance as yf
import requests
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"

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
        try:
            data = {}
            session = requests.Session()
            session.headers.update({"User-Agent": USER_AGENT})

            for symbol in self.symbols:
                ticker = yf.Ticker(symbol, session=session)
                # Using fast_info to get the most important data quickly
                info = await self.hass.async_add_executor_job(lambda: ticker.info)
                # If ticker.info still fails with 429, we might need a fallback or a more resilient approach
                if info:
                    data[symbol] = info
            return data
        except Exception as err:
            raise UpdateFailed(f"Error communicating with Yahoo Finance API: {err}")
