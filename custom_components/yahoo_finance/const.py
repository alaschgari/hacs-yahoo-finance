import random

DOMAIN = "yahoo_finance"
DEFAULT_SCAN_INTERVAL = 120
MIN_UPDATE_INTERVAL = 30

CONF_SYMBOLS = "symbols"
CONF_SHOW_CHANGE_PCT = "show_change_pct"
CONF_SHOW_HIGH = "show_high"
CONF_SHOW_LOW = "show_low"
CONF_SHOW_MARKET_CAP = "show_market_cap"
CONF_SHOW_VOLUME = "show_volume"
CONF_SHOW_OPEN = "show_open"
CONF_SHOW_52WK_HIGH = "show_52wk_high"
CONF_SHOW_52WK_LOW = "show_52wk_low"
CONF_SHOW_DIVIDEND = "show_dividend"
CONF_SHOW_EARNINGS = "show_earnings"
CONF_SHOW_PE = "show_pe"
CONF_SHOW_TREND = "show_trend"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_ECO_THRESHOLD = "eco_threshold"
CONF_BASE_CURRENCY = "base_currency"
CONF_EXT_HOURS = "ext_hours"
CONF_SHOW_ESG = "show_esg"
CONF_SHOW_PERFORMANCE = "show_performance"
CONF_SHOW_MARKET_STATUS = "show_market_status"

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
]

def get_headers():
    """Return a random set of headers."""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
        "Referer": "https://finance.yahoo.com/",
        "DNT": "1",
    }


