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
            
            def fetch_direct(s):
                url = f"https://query1.finance.yahoo.com/v8/finance/chart/{s}?range=1d&interval=1d"
                headers = get_headers()
                try:
                    response = requests.get(url, headers=headers, timeout=15)
                    response.raise_for_status()
                    content = response.json()
                    
                    if "chart" in content and content["chart"]["result"]:
                        result = content["chart"]["result"][0]
                        meta = result["meta"]
                        
                        price = meta.get("regularMarketPrice")
                        prev_close = meta.get("chartPreviousClose")
                        
                        # Get high/low from indicators if available
                        high = price
                        low = price
                        try:
                            quotes = result["indicators"]["quote"][0]
                            if quotes.get("high"):
                                high = quotes["high"][0]
                            if quotes.get("low"):
                                low = quotes["low"][0]
                        except (KeyError, IndexError):
                            pass

                        return {
                            "regularMarketPrice": price,
                            "currency": meta.get("currency"),
                            "regularMarketChangePercent": (price - prev_close) / prev_close * 100 if price and prev_close else 0,
                            "dayHigh": high,
                            "dayLow": low,
                            "symbol": s,
                            "longName": s,
                            "shortName": s,
                        }
                except Exception as ex:
                    _LOGGER.warning("Direct fetch failed for %s: %s", s, ex)
                return None

            info = await self.hass.async_add_executor_job(fetch_direct, symbol)
            if info:
                data[symbol] = info
            else:
                _LOGGER.info("No data for %s via direct API, skipping", symbol)
                
        if not data:
            raise UpdateFailed("Failed to fetch data for any symbol via direct API. Yahoo might be blocking or the symbols are invalid.")
        return data
