# 🚀 Yahoo Finance Integration for Home Assistant

<p align="center">
  <img src="https://raw.githubusercontent.com/alaschgari/hacs-yahoo-finance/main/logo.png" alt="Yahoo Finance Logo" width="180">
</p>

<p align="center">
  <b>The ultimate tool for tracking stocks, currencies, and technical indicators directly in your Dashboard.</b>
</p>

<p align="center">
  <a href="https://github.com/hacs/integration"><img src="https://img.shields.io/badge/HACS-Custom-41BDF5.svg" alt="HACS Badge"></a>
  <a href="https://github.com/alaschgari/hacs-yahoo-finance/releases"><img src="https://img.shields.io/github/v/release/alaschgari/hacs-yahoo-finance" alt="Latest Release"></a>
  <a href="https://github.com/alaschgari/hacs-yahoo-finance/blob/main/LICENSE"><img src="https://img.shields.io/github/license/alaschgari/hacs-yahoo-finance" alt="License"></a>
  <a href="https://www.buymeacoffee.com/alaschgari"><img src="https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Donate-orange.svg" alt="Buy Me A Coffee"></a>
</p>

---

This integration brings real-time financial data to Home Assistant. Whether you're tracking your investment portfolio, monitoring crypto prices, or watching currency fluctuations, this component provides all the tools you need with professional-grade accuracy.

## 📸 Dashboard Preview

> [!TIP]
> **Showcase your dashboard!** Replace the image below with a screenshot of your own Home Assistant setup to show new users what's possible.

![Dashboard Preview Placeholder](https://via.placeholder.com/800x400?text=Your+Home+Assistant+Dashboard+Screenshot+Here)

---

## ✨ Key Features

### 🏦 Portfolio Tracking (Pro)
- **Multi-Currency Value:** Automatically convert your various holdings (USD, EUR, BTC, etc.) into a single base currency of your choice.
- **Auto-Calculated Weights:** See exactly what percentage each stock occupies in your total portfolio.
- **Performance:** Real-time YTD (Year-to-Date) return tracking.

### 📈 Market Intel & Technicals
- **Market Status:** Instant feedback on whether the market is Open, Closed, or in Extended Hours (Pre/Post market).
- **Technical Indicators:** Native support for 50-day and 200-day moving averages.
- **ESG Scores:** Professional sustainability ratings (Environmental, Social, Governance).
- **Risk Metrics:** Live **Beta Factor** calculation.

### 🧠 Smart Polling (Eco-Mode)
- Automatically saves resources and preserves API health by slowing down polling during nights and weekends when markets are closed.

---

## 🚀 Installation

### Via HACS (Recommended)
1. Open **HACS** > **Integrations**.
2. Click the three dots (top right) > **Custom repositories**.
3. Add `https://github.com/alaschgari/hacs-yahoo-finance` and select **Integration**.
4. Restart Home Assistant.

### Configuration
1. Navigate to **Settings** > **Devices & Services**.
2. Add the **Yahoo Finance** integration.
3. Enter your symbols (e.g., `AAPL, TSLA, BTC-USD, EURUSD=X`).
4. Toggle your preferred **Pro Features** in the Options menu at any time!

---

## 🛠 Advanced Features Table

| Feature | Description | Attribute |
|---------|-------------|-----------|
| **ESG Score** | Comprehensive sustainability rating | `totalEsg` |
| **Beta Factor** | Measure of volatility vs. the market | `beta` |
| **Market Status**| Real-time market phase (e.g., REGULAR, POST) | `marketState` |
| **Pre/Post Market**| Pricing data outside regular trading hours | `preMarketPrice` |

---

## 🗺 Localization
Fully translated and supported in:
- 🇺🇸 **English**
- 🇩🇪 **German**

---

## 🤝 Support & Contribution

If you find this project valuable, consider supporting its maintenance:

<a href="https://www.buymeacoffee.com/alaschgari"><img src="https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Donate-orange.svg?style=for-the-badge&logo=buy-me-a-coffee" alt="Coffee Support"></a>

**Contributions are welcome!** Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## ⚖️ Disclaimer
*This is an unofficial project not affiliated with Yahoo Finance. Provided "as is" with no warranty. Use at your own risk.*
