# Yahoo Finance Integration for Home Assistant

This integration allows you to track stock prices and other financial metrics using the `yfinance` library.

## Installation

1. Copy the `custom_components/yahoo_finance` directory to your Home Assistant `custom_components` directory.
2. Restart Home Assistant.
3. Add the integration via **Settings > Devices & Services > Add Integration**.

## Features

- **Multiple Tickers**: Monitor multiple stock symbols.
- **Real-time Data**: Periodic updates for price and other metrics.
- **Attributes**: Includes day high, day low, and percent change.

## Configuration

During setup, you will be asked to enter ticker symbols separated by commas (e.g., `AAPL, MSFT, BTC-USD`).

## Credits

This integration uses the [yfinance](https://github.com/ranaroussi/yfinance) library.
