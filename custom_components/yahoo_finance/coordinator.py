"""DataUpdateCoordinator for Yahoo Finance integration."""
import datetime
from datetime import timedelta
import logging

import yfinance as yf
import requests
import asyncio
import random
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN, 
    DEFAULT_SCAN_INTERVAL, 
    MIN_UPDATE_INTERVAL, 
    CONF_SCAN_INTERVAL, 
    CONF_ECO_THRESHOLD, 
    CONF_BASE_CURRENCY,
    CONF_EXT_HOURS,
    get_headers
)

_LOGGER = logging.getLogger(__name__)

# Global cooldown for 429 errors
_LAST_429_TIME = 0
_COOLDOWN_DURATION = 300  # 5 minutes

class YahooFinanceDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Yahoo Finance data."""

    def __init__(self, hass, symbol_definitions, scan_interval=DEFAULT_SCAN_INTERVAL, eco_threshold=600, base_currency="USD", ext_hours=False):
        """Initialize."""
        self.symbol_definitions = symbol_definitions
        self.symbols = list(symbol_definitions.keys())
        self.scan_interval = scan_interval
        self.eco_threshold = eco_threshold
        self.base_currency = base_currency
        self.ext_hours = ext_hours
        self._slow_update_interval = 21600  # 6 hours
        self._last_slow_update = 0
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self._last_update_success_time = 0
        self._fx_rates = {}

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
        def fetch_batch(symbols, fetch_slow, ext_hours=False, base_currency="USD"):
            try:
                # Add currency pairs to symbols if they are missing
                all_request_symbols = list(symbols)
                currencies_to_fetch = set()
                
                tickers = yf.Tickers(" ".join(all_request_symbols))
                batch_data = {}
                fx_rates = {}

                for symbol in all_request_symbols:
                    ticker = tickers.tickers.get(symbol)
                    if not ticker: continue
                    
                    try:
                        # Use fast_info for basic data
                        fast = ticker.fast_info
                        
                        # Basic Data
                        data = {
                            "regularMarketPrice": fast.last_price,
                            "currency": fast.currency,
                            "regularMarketChangePercent": ((fast.last_price - fast.previous_close) / fast.previous_close * 100) if fast.last_price and fast.previous_close else 0,
                            "marketCap": fast.market_cap,
                            "symbol": symbol,
                            "longName": symbol,
                        }

                        if fetch_slow:
                            info = ticker.info
                            data.update({
                                "longName": info.get("longName") or symbol,
                                "shortName": info.get("shortName") or symbol,
                                "dividendYield": info.get("dividendYield"),
                                "exDividendDate": info.get("exDividendDate"),
                                "nextEarningsDate": info.get("nextEarningsDate"),
                                "forwardPE": info.get("forwardPE"),
                                "trailingPE": info.get("trailingPE"),
                                "beta": info.get("beta"),
                                "totalEsg": info.get("totalEsg"),
                                "environmentScore": info.get("environmentScore"),
                                "socialScore": info.get("socialScore"),
                                "governanceScore": info.get("governanceScore"),
                                "marketState": info.get("marketState"),
                                "preMarketPrice": info.get("preMarketPrice"),
                                "postMarketPrice": info.get("postMarketPrice"),
                                "fiftyDayAverage": info.get("fiftyDayAverage"),
                                "twoHundredDayAverage": info.get("twoHundredDayAverage"),
                                "ytdReturn": info.get("ytdReturn"),
                                "trailingAnnualDividendRate": info.get("trailingAnnualDividendRate"),
                                "news": [
                                    {
                                        "title": n.get("content", {}).get("title"),
                                        "link": n.get("content", {}).get("canonicalUrl", {}).get("url")
                                    }
                                    for n in (ticker.news[:5] if hasattr(ticker, "news") else [])
                                    if n.get("content", {}).get("title")
                                ],
                            })
                            
                            # Collect currencies for FX fetching
                            if fast.currency and fast.currency != base_currency:
                                currencies_to_fetch.add(f"{fast.currency}{base_currency}=X")

                        batch_data[symbol] = data
                    except Exception as e:
                        _LOGGER.debug("Error extracting data for %s: %s", symbol, e)

                # Fetch FX rates if any
                if currencies_to_fetch:
                    fx_tickers = yf.Tickers(" ".join(currencies_to_fetch))
                    for fx_sym in currencies_to_fetch:
                        try:
                            fx_rates[fx_sym[:3]] = fx_tickers.tickers[fx_sym].fast_info.last_price
                        except: pass

                return batch_data, fetch_slow, fx_rates
            except Exception as ex:
                _LOGGER.warning("Batch fetch failed: %s", ex)
                return None, False, {}

        # Add a random delay before the batch request to be stealthy
        await asyncio.sleep(random.uniform(2.0, 5.0))
        
        result, was_slow, fx_rates = await self.hass.async_add_executor_job(
            fetch_batch, self.symbols, fetch_slow_data, self.ext_hours, self.base_currency
        )
        
        # Store FX rates for conversion
        if fx_rates:
            self._fx_rates.update(fx_rates)
        
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
                    price = val["regularMarketPrice"]
                    currency = val.get("currency", "USD")
                    
                    # Store original total value
                    val["total_value"] = amount * price
                    
                    # Convert to base currency for portfolio total
                    if currency != self.base_currency:
                         rate = self._fx_rates.get(currency)
                         if rate:
                             val["total_value_base"] = amount * price * rate
                         else:
                             # Try reciprocal if needed or just use 1.0 (though yf should provide the rate)
                             val["total_value_base"] = amount * price
                    else:
                         val["total_value_base"] = amount * price
                    
                    total_portfolio_value += val["total_value_base"]
                else:
                    val["total_value"] = 0
                    val["total_value_base"] = 0
                
                new_data[symbol] = val

            # Calculate weight for each symbol
            for symbol, val in new_data.items():
                if symbol == "__portfolio__":
                    continue
                if total_portfolio_value > 0:
                    val["portfolio_weight"] = (val.get("total_value_base", 0) / total_portfolio_value) * 100
                else:
                    val["portfolio_weight"] = 0
            
            new_data["__portfolio__"] = {
                "total_value": total_portfolio_value,
                "currency": self.base_currency
            }
            
            self._last_update_success_time = asyncio.get_event_loop().time()
            return new_data
        
        if not self.data:
            raise UpdateFailed("Failed to fetch data for any symbol in batch.")
            
        return self.data
