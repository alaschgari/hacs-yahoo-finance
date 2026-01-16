"""DataUpdateCoordinator for Yahoo Finance integration."""
from datetime import timedelta
import logging

import yfinance as yf
import requests
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
                ticker = yf.Ticker(symbol, session=self.session)
                # Ensure the entire .info dict is fetched within the executor
                def fetch_info(t):
                    return t.info

                info = await self.hass.async_add_executor_job(fetch_info, ticker)
                if info:
                    data[symbol] = info
            return data
        except Exception as err:
            raise UpdateFailed(f"Error communicating with Yahoo Finance API: {err}")
