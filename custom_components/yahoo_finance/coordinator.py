"""DataUpdateCoordinator for Yahoo Finance integration."""
from datetime import timedelta
import logging

import yfinance as yf
import requests
import asyncio
import random
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL, MIN_UPDATE_INTERVAL, get_headers

_LOGGER = logging.getLogger(__name__)

# Global cooldown for 429 errors
_LAST_429_TIME = 0
_COOLDOWN_DURATION = 300  # 5 minutes

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
        self._last_update_success_time = 0

    async def _async_update_data(self):
        """Fetch data from Yahoo Finance."""
        global _LAST_429_TIME
        
        # Check if we are in cooldown
        if asyncio.get_event_loop().time() < _LAST_429_TIME + _COOLDOWN_DURATION:
            _LOGGER.info("Skipping update due to recent 429 rate limit (cooling down)")
            return self.data if self.data else {}

        # Check for minimum update interval to prevent spamming
        now = asyncio.get_event_loop().time()
        if now < self._last_update_success_time + MIN_UPDATE_INTERVAL:
            _LOGGER.debug("Skipping update due to minimum interval limit (throttling)")
            return self.data if self.data else {}

        def fetch_batch(symbols):
            try:
                # yfinance allows fetching multiple tickers at once
                # The Tickers object handles thread-safe data fetching
                tickers = yf.Tickers(" ".join(symbols))
                
                batch_data = {}
                for symbol in symbols:
                    # Accessing the ticker object from the Tickers container
                    ticker = tickers.tickers.get(symbol)
                    if not ticker:
                        continue
                        
                    # fast_info provides the data we need without downloading history
                    info = ticker.fast_info
                    if not info:
                        continue
                    
                    try:
                        price = info.last_price
                        prev_close = info.previous_close
                        
                        batch_data[symbol] = {
                            "regularMarketPrice": price,
                            "currency": info.currency,
                            "regularMarketChangePercent": (price - prev_close) / prev_close * 100 if price and prev_close else 0,
                            "dayHigh": info.day_high,
                            "dayLow": info.day_low,
                            "symbol": symbol,
                            # fast_info doesn't always have long/short name, fallback to symbol
                            "longName": symbol, 
                            "shortName": symbol,
                        }
                    except Exception as e:
                        _LOGGER.debug("Error extracting data for %s: %s", symbol, e)
                        continue
                        
                return batch_data
            except Exception as ex:
                _LOGGER.warning("Batch fetch failed: %s", ex)
                return None

        # Add a random delay before the batch request to be stealthy
        await asyncio.sleep(random.uniform(2.0, 5.0))
        
        result = await self.hass.async_add_executor_job(fetch_batch, self.symbols)
        
        if result == "429":
            _LOGGER.warning("Hit 429 Rate Limit during batch fetch. Entering 5-minute cooldown.")
            _LAST_429_TIME = asyncio.get_event_loop().time()
            return self.data if self.data else {}
        
        if result:
            _LOGGER.debug("Successfully fetched batch data for %d symbols", len(result))
            # Merge with existing data to keep historical values if some symbols are missing in this batch
            new_data = self.data.copy() if self.data else {}
            new_data.update(result)
            self._last_update_success_time = asyncio.get_event_loop().time()
            return new_data
        
        if not self.data:
            raise UpdateFailed("Failed to fetch data for any symbol in batch.")
            
        return self.data
