import sys
import os
import requests
import json
import logging

# Add custom_components to path so we can import const
sys.path.append(os.path.join(os.getcwd(), 'custom_components'))

try:
    from yahoo_finance.const import get_headers
except ImportError:
    # Fallback if running from a different directory structure or plain script
    import random
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    ]
    def get_headers():
        return {
            "User-Agent": random.choice(USER_AGENTS)
        }

# Configure logging
logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)

def fetch_batch(symbols):
    """
    Fetches data for a batch of symbols. 
    Logic replicated from coordinator.py
    """
    if not symbols:
        return {}
        
    symbols_str = ",".join(symbols)
    # Spark endpoint allows batch fetching multiple symbols at once
    url = f"https://query1.finance.yahoo.com/v7/finance/spark?symbols={symbols_str}&range=1d&interval=1d"
    
    headers = get_headers()
    print(f"Fetching: {url}")
    print(f"Headers: {headers}")

    try:
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 429:
            print("Received 429 Rate Limit!")
            return "429"
            
        response.raise_for_status()
        content = response.json()
        
        # Debug: print raw content (truncated)
        # print("Raw response:", json.dumps(content)[:200] + "...")
        
        batch_data = {}
        if "spark" in content and "result" in content["spark"]:
            for entry in content["spark"]["result"]:
                symbol = entry.get("symbol")
                if not symbol or not entry.get("response"):
                    continue
                    
                # Response is usually a list with one item metadata
                resp_item = entry["response"][0]
                meta = resp_item.get("meta")
                if not meta:
                    continue
                    
                price = meta.get("regularMarketPrice")
                prev_close = meta.get("chartPreviousClose")
                high = meta.get("regularMarketDayHigh") or price
                low = meta.get("regularMarketDayLow") or price
                
                # Safe calculation for change percent
                change_pct = 0
                if price and prev_close:
                    change_pct = (price - prev_close) / prev_close * 100
                
                batch_data[symbol] = {
                    "regularMarketPrice": price,
                    "currency": meta.get("currency"),
                    "regularMarketChangePercent": change_pct,
                    "dayHigh": high,
                    "dayLow": low,
                    "symbol": symbol,
                    "longName": meta.get("longName") or symbol,
                    "shortName": meta.get("shortName") or symbol,
                }
        return batch_data
    except Exception as ex:
        _LOGGER.warning("Batch fetch failed: %s", ex)
        return None

if __name__ == "__main__":
    # Sample symbols to test
    # basic stock, currency, crypto (if supported by yahoo finance logic)
    TEST_SYMBOLS = ["AAPL"]
    
    print(f"Testing fetch_batch with symbols: {TEST_SYMBOLS}")
    result = fetch_batch(TEST_SYMBOLS)
    
    if result == "429":
        print("Rate limited.")
    elif result:
        print("\n--- Results ---")
        print(json.dumps(result, indent=2))
        print(f"\nSuccessfully fetched {len(result)} symbols.")
    else:
        print("Failed to fetch data or no data returned.")
