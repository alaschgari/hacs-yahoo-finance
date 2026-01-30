import yfinance as yf
import json

def inspect_ticker(symbol):
    ticker = yf.Ticker(symbol)
    info = ticker.fast_info
    
    data = {}
    for attr in dir(info):
        if not attr.startswith('_') and not callable(getattr(info, attr)):
            try:
                data[attr] = getattr(info, attr)
            except:
                pass
                
    return data

if __name__ == "__main__":
    symbol = "AAPL"
    print(f"Inspecting {symbol} fast_info fields:")
    fields = inspect_ticker(symbol)
    print(json.dumps(fields, indent=2, default=str))
