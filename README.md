# Yahoo Finance Integration for Home Assistant

<p align="center">
  <img src="https://raw.githubusercontent.com/alaschgari/hacs-yahoo-finance/main/logo.png" alt="Yahoo Finance Logo" width="150">
</p>

This integration provides a robust way to track stock prices, currencies, and technical indicators. Now with full **Portfolio Tracking** and **Smart Polling** support.

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Donate-orange.svg)](https://www.buymeacoffee.com/alaschgari)

This custom integration for Home Assistant allows you to track stock prices, currencies, and other financial data using the Yahoo Finance API via the `yfinance` library.
 
## Features
- **Pro Portfolio Tracking:** Track holding values across multiple currencies with automatic conversion to your base currency (EUR, USD, etc.).
- **Smart Polling (Eco-Mode):** Automatic interval adjustment for nights and weekends to avoid API bans.
- **Market Insights:** Real-time **Market Status** (Open/Closed/Extended) and **Extended Hours** (Pre/Post market) pricing support.
- **Technical Indicators:** 50-day and 200-day moving averages.
- **Professional Metrics:** **ESG Scores** (Environmental, Social, Governance), **Beta Factor**, and **YTD Performance**.
- **Dividend Intel:** Yields, Next Earnings dates, and Historical dividend rates.
- **Diversification:** Calculation of portfolio weights per position.
- **Reliability:** Powered by `yfinance` with automatic session & crumb management.
- **Localization:** Fully translated into English and German.
- **Easy Config:** Professional UI-based setup with toggleable Pro features and custom intervals.

## Installation via HACS
1. Open HACS in your Home Assistant instance.
2. Click on "Integrations".
3. Click the three dots in the upper right corner and select "Custom repositories".
4. Add the URL of this repository (`https://github.com/alaschgari/hacs-yahoo-finance`) and select "Integration" as the category.
5. Click "Add" and then install the "Yahoo Finance" integration.
6. Restart Home Assistant.

## Configuration
1. Go to **Settings** > **Devices & Services**.
2. Click **Add Integration**.
3. Search for **Yahoo Finance**.
4. Enter the **Symbols** (comma-separated, e.g., `AAPL,MSFT,BTC-USD,EURUSD=X`) you want to track.

## Support

If you find this integration useful and want to support its development, you can buy me a coffee! Your support is greatly appreciated and helps keep this project alive and updated.

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Donate-orange.svg?style=for-the-badge&logo=buy-me-a-coffee)](https://www.buymeacoffee.com/alaschgari)

## Disclaimer

This integration is an **unofficial** project and is **not** affiliated, associated, authorized, endorsed by, or in any way officially connected with Yahoo!, or any of its subsidiaries or its affiliates. The official Yahoo Finance website can be found at [https://finance.yahoo.com](https://finance.yahoo.com).

This project is provided "as is" by a private individual for educational and personal use only. **No warranty** of any kind, express or implied, is made regarding the accuracy, reliability, or availability of this integration. Use it at your own risk. The author assumes no responsibility or liability for any errors or omissions in the content of this project or for any damages arising from its use.
