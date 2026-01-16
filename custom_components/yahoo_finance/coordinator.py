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

# Global cooldown for 429 errors
_LAST_429_TIME = 0
_COOLDOWN_DURATION = 1800  # 30 minutes

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
        global _LAST_429_TIME
        
        # Check if we are in cooldown
        if asyncio.get_event_loop().time() < _LAST_429_TIME + _COOLDOWN_DURATION:
            _LOGGER.info("Skipping update due to recent 429 rate limit (cooling down)")
            return self.data if self.data else {}

        data = {}
        for symbol in self.symbols:
            # Random delay before EACH symbol to avoid detection
            await asyncio.sleep(random.uniform(5.0, 10.0))
            
            def fetch_direct(s):
                # Use query2 as alternative, often less guarded
                url = f"https://query2.finance.yahoo.com/v8/finance/chart/{s}?range=1d&interval=1d"
                headers = get_headers()
                try:
                    response = requests.get(url, headers=headers, timeout=15)
                    
                    if response.status_code == 429:
                        return "429"
                        
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
                                high = next((h for h in quotes["high"] if h is not None), price)
                            if quotes.get("low"):
                                low = next((l for l in quotes["low"] if l is not None), price)
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

            result = await self.hass.async_add_executor_job(fetch_direct, symbol)
            
            if result == "429":
                _LOGGER.warning("Hit 429 Rate Limit for %s. Entering 30-minute cooldown.", symbol)
                _LAST_429_TIME = asyncio.get_event_loop().time()
                # Return whatever we already have to stop the retry loop
                return data if data else (self.data if self.data else {})
            
            if result:
                data[symbol] = result
            else:
                _LOGGER.info("No data for %s via direct API, skipping", symbol)
                
        if not data and not self.data:
             # Only raise if we have NO data yet, otherwise return old data to avoid retries
            raise UpdateFailed("Failed to fetch data for any symbol. Yahoo might be blocking.")
            
        # Merge new data with old data for missing symbols
        final_data = self.data.copy() if self.data else {}
        final_data.update(data)
        return final_data
