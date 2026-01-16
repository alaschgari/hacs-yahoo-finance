"""DataUpdateCoordinator for Yahoo Finance integration."""
from datetime import timedelta
import logging

import yfinance as yf
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL

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
        try:
            data = {}
            for symbol in self.symbols:
                ticker = yf.Ticker(symbol)
                # We use fast_info for basic data or info for everything
                # Note: yfinance can be blocking, so we run it in executor if needed
                # However, yfinance 0.2.x has some async capabilities or we can just use hass.async_add_executor_job
                info = await self.hass.async_add_executor_job(lambda: ticker.info)
                if info:
                    data[symbol] = info
            return data
        except Exception as err:
            raise UpdateFailed(f"Error communicating with Yahoo Finance API: {err}")
