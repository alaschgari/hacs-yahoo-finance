import sys
import os
import yfinance as yf
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)

def fetch_batch(symbols):
    """
    Fetches data for a batch of symbols using yfinance. 
    Logic replicated from expected coordinator.py
    """
    if not symbols:
        return {}
        
    print(f"Fetching with yfinance: {symbols}")

    try:
        # yfinance allows fetching multiple tickers at once
        tickers = yf.Tickers(" ".join(symbols))
        
        batch_data = {}
        for symbol in symbols:
            ticker = tickers.tickers.get(symbol)
            if not ticker:
                print(f"Ticker {symbol} not found in response.")
                continue
                
            # fast_info provides the data we need without downloading history
            info = ticker.fast_info
            if not info:
                print(f"No fast_info for {symbol}")
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
                    "longName": symbol, 
                    "shortName": symbol,
                }
            except Exception as e:
                print(f"Error extracting data for {symbol}: {e}")
                continue
                
        return batch_data
    except Exception as ex:
        print(f"Batch fetch failed: {ex}")
        return None

if __name__ == "__main__":
    TEST_SYMBOLS = ["AAPL", "MSFT", "EURUSD=X", "BTC-USD"]
    
    print(f"Testing yfinance fetch with symbols: {TEST_SYMBOLS}")
    result = fetch_batch(TEST_SYMBOLS)
    
    if result:
        print("\n--- Results ---")
        # Use default=str to handle non-serializable objects just in case
        print(json.dumps(result, indent=2, default=str))
        print(f"\nSuccessfully fetched {len(result)} symbols.")
    else:
        print("Failed to fetch data or no data returned.")
