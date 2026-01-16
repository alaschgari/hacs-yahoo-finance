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
            
            def fetch_ultra_lite_info(t):
                try:
                    # Using history(period="2d") is much more stable as it uses v8/finance/chart
                    # which is less guarded than the quoteSummary endpoint.
                    hist = t.history(period="2d")
                    if hist.empty:
                        return None
                    
                    # Extract metadata from the chart response
                    meta = t.history_metadata
                    
                    last_close = hist["Close"].iloc[-1]
                    prev_close = hist["Close"].iloc[-2] if len(hist) > 1 else last_close
                    high = hist["High"].iloc[-1]
                    low = hist["Low"].iloc[-1]
                    
                    return {
                        "regularMarketPrice": last_close,
                        "currency": meta.get("currency"),
                        "regularMarketChangePercent": (last_close - prev_close) / prev_close * 100 if prev_close else 0,
                        "dayHigh": high,
                        "dayLow": low,
                        "symbol": symbol,
                        "longName": symbol,
                        "shortName": symbol,
                    }
                except Exception as ex:
                    _LOGGER.warning("Error fetching %s via ultra-lite method: %s", symbol, ex)
                    return None

            info = await self.hass.async_add_executor_job(fetch_ultra_lite_info, ticker)
            if info:
                data[symbol] = info
            else:
                _LOGGER.info("No data for %s, skipping this update", symbol)
                
        if not data:
            raise UpdateFailed("Failed to fetch data for any symbol")
        return data
