"""DataUpdateCoordinator for Yahoo Finance integration."""
import datetime
from datetime import timedelta
import logging

import yfinance as yf
import requests
import asyncio
import random
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL, MIN_UPDATE_INTERVAL, CONF_SCAN_INTERVAL, CONF_ECO_THRESHOLD, get_headers

_LOGGER = logging.getLogger(__name__)

# Global cooldown for 429 errors
_LAST_429_TIME = 0
_COOLDOWN_DURATION = 300  # 5 minutes

class YahooFinanceDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Yahoo Finance data."""

    def __init__(self, hass, symbol_definitions, scan_interval=DEFAULT_SCAN_INTERVAL, eco_threshold=600):
        """Initialize."""
        self.symbol_definitions = symbol_definitions
        self.symbols = list(symbol_definitions.keys())
        self.scan_interval = scan_interval
        self.eco_threshold = eco_threshold
        self._slow_update_interval = 21600  # 6 hours
        self._last_slow_update = 0
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
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
        
        # Eco-Mode Logic: Check if we are in off-market hours (Night or Weekend)
        # Local time of the Home Assistant instance
        local_now = datetime.datetime.now()
        is_weekend = local_now.weekday() >= 5  # 5=Saturday, 6=Sunday
        is_night = local_now.hour < 8 or local_now.hour >= 22
        
        current_threshold = MIN_UPDATE_INTERVAL
        if is_weekend or is_night:
            # Use configured eco-threshold
            current_threshold = self.eco_threshold
            
        if now < self._last_update_success_time + current_threshold:
             _LOGGER.debug("Skipping update due to %s interval limit (%ss)", "Eco-Mode" if current_threshold >= self.eco_threshold else "minimum", current_threshold)
             return self.data if self.data else {}

        # Determine if we should fetch slow data (earnings, etc.)
        fetch_slow_data = False
        if now > self._last_slow_update + self._slow_update_interval:
            fetch_slow_data = True

        def fetch_batch(symbols, fetch_slow):
            try:
                tickers = yf.Tickers(" ".join(symbols))
                
                batch_data = {}
                for symbol in symbols:
                    ticker = tickers.tickers.get(symbol)
                    if not ticker:
                        continue
                        
                    info = ticker.fast_info
                    if not info:
                        continue
                    
                    try:
                        price = info.last_price
                        prev_close = info.previous_close
                        
                        # Base data
                        data = {
                            "regularMarketPrice": price,
                            "currency": info.currency,
                            "regularMarketChangePercent": (price - prev_close) / prev_close * 100 if price and prev_close else 0,
                            "dayHigh": info.day_high,
                            "dayLow": info.day_low,
                            "marketCap": info.market_cap,
                            "volume": info.last_volume,
                            "open": info.open,
                            "yearHigh": info.year_high,
                            "yearLow": info.year_low,
                            "symbol": symbol,
                            "longName": symbol, 
                            "shortName": symbol,
                        }

                        # Slow data (only if requested)
                        if fetch_slow:
                            # Ticker.info is slower but contains earnings/dividends
                            # We only fetch this every 6 hours
                            ext_info = ticker.info
                            data.update({
                                "dividendYield": ext_info.get("dividendYield"),
                                "exDividendDate": ext_info.get("exDividendDate"),
                                "nextEarningsDate": ext_info.get("nextEarningsDate"),
                                "forwardPE": ext_info.get("forwardPE"),
                                "trailingPE": ext_info.get("trailingPE"),
                                "longName": ext_info.get("longName") or symbol,
                                "shortName": ext_info.get("shortName") or symbol,
                                "news": [
                                    {
                                        "title": n.get("content", {}).get("title"),
                                        "link": n.get("content", {}).get("canonicalUrl", {}).get("url")
                                    }
                                    for n in (ticker.news[:5] if hasattr(ticker, "news") else [])
                                    if n.get("content", {}).get("title")
                                ],
                            })
                            
                        batch_data[symbol] = data
                    except Exception as e:
                        _LOGGER.debug("Error extracting data for %s: %s", symbol, e)
                        continue
                        
                return batch_data, fetch_slow
            except Exception as ex:
                _LOGGER.warning("Batch fetch failed: %s", ex)
                return None, False

        # Add a random delay before the batch request to be stealthy
        await asyncio.sleep(random.uniform(2.0, 5.0))
        
        result, was_slow = await self.hass.async_add_executor_job(fetch_batch, self.symbols, fetch_slow_data)
        
        if result == "429":
            _LOGGER.warning("Hit 429 Rate Limit during batch fetch. Entering 5-minute cooldown.")
            _LAST_429_TIME = asyncio.get_event_loop().time()
            return self.data if self.data else {}
        
        if result:
            _LOGGER.debug("Successfully fetched batch data for %d symbols", len(result))
            if was_slow:
                self._last_slow_update = asyncio.get_event_loop().time()

            # Merge with existing data
            new_data = self.data.copy() if self.data else {}
            
            total_portfolio_value = 0
            for symbol, val in result.items():
                # Add owned amount to data
                amount = self.symbol_definitions.get(symbol, 0)
                val["owned_amount"] = amount
                
                if amount > 0 and val.get("regularMarketPrice"):
                    val["total_value"] = amount * val["regularMarketPrice"]
                    total_portfolio_value += val["total_value"]
                else:
                    val["total_value"] = 0
                
                new_data[symbol] = val

            # Calculate weight for each symbol
            for symbol, val in new_data.items():
                if symbol == "__portfolio__":
                    continue
                if total_portfolio_value > 0:
                    val["portfolio_weight"] = (val.get("total_value", 0) / total_portfolio_value) * 100
                else:
                    val["portfolio_weight"] = 0
            
            new_data["__portfolio__"] = {"total_value": total_portfolio_value}
            
            self._last_update_success_time = asyncio.get_event_loop().time()
            return new_data
        
        if not self.data:
            raise UpdateFailed("Failed to fetch data for any symbol in batch.")
            
        return self.data
