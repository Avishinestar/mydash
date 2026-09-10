---
title: Advanced Investor Dashboard
emoji: 📈
colorFrom: blue
colorTo: indigo
sdk: streamlit
app_file: pro_dashboard.py
pinned: false
---

# 📈 Advanced Investor Dashboard

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-Automated_Data-2088FF.svg?logo=github-actions&logoColor=white)](.github/workflows/fetch_fii_data.yml)

A high-performance market dashboard and scanner for active investors and traders. Built with Streamlit, Yahoo Finance, and technical analysis indicators, covering Indian markets (Nifty 50, Nifty 500, Sector Indices) and US markets (Nasdaq 100, Russell 1000).

---

## 🌟 Key Features

- **📊 Sector Performance & Alpha Analysis**
  - Live outperformance / underperformance alpha vs Nifty 50 for all NSE sectoral indices.
  - Granular constituent drill-down identifying top gainers and laggards within each sector.
- **⚡ Technical Breakout & Momentum Scanners**
  - Multi-factor range breakout scanner (20D/50D/52-week high proximity, volume surges, MACD, moving average alignment, RSI).
  - Weekly RSI oversold rebound scan (Weekly RSI < 40 + price trading above 200-DMA).
  - Broad-universe scanning across Nifty 500 and Top 2000 NSE tickers.
- **🇺🇸 US Market Momentum Scanner**
  - Dedicated scanner for US Equities covering **Nasdaq 100** and **Russell 1000**.
  - Highlights breakout movers (up 3%+), technical levels (Daily/Weekly RSI, 50/200 DMA), and integrates live TradingView news feeds.
- **🇮🇳 GIFT Nifty Live Tracker**
  - Live pre-market tracking comparing GIFT Nifty against Nifty 50 closing levels.
- **📦 Volume Analysis & Market Breadth**
  - Aggregated buying vs selling pressure across Nifty 500 on daily and weekly timeframes.
- **💎 Fundamental Screeners**
  - Screens fundamentally solid companies (P/E < 20, ROE > 15%).
- **📰 Live Market News & Macro Feeds**
  - Real-time RSS feeds from Economic Times (Markets, Macro, Earnings, Companies).
- **🌍 Global Indices & ATH Distance**
  - 20 major world indices with real-time distance from All-Time Highs (ATH).
- **🤖 Automated FII/DII Institutional Flows**
  - Daily automated tracking of Foreign Institutional Investor (FII) shareholding trends via scheduled GitHub Actions.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9, 3.10, or 3.11 installed
- Git

### Option 1: 1-Click Launch (Windows)
Double-click `index.bat` or run:
```cmd
index.bat
```
This automatically installs dependencies and opens the dashboard in your browser.

### Option 2: Manual Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Avishinestar/mydash.git
   cd mydash
   ```

2. **Create and activate a virtual environment (recommended):**
   ```bash
   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate

   # Windows
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the dashboard:**
   ```bash
   streamlit run pro_dashboard.py
   ```
   The dashboard will open at `http://localhost:8501`.

### Option 3: Docker Deployment

1. **Build the container:**
   ```bash
   docker build -t investor-dashboard .
   ```

2. **Run the container:**
   ```bash
   docker run -p 7860:7860 investor-dashboard
   ```
   Access the dashboard at `http://localhost:7860`.

---

## 📁 Project Structure

```
├── .github/workflows/
│   └── fetch_fii_data.yml       # Scheduled GitHub Action (Runs Mon–Fri 8 AM IST)
├── .streamlit/
│   └── config.toml              # Streamlit server & dark theme configuration
├── scripts/
│   ├── fetch_fii_shareholding.py # Scrapes FII shareholding data
│   └── fetch_top2000.py         # Utility to refresh Indian market ticker universe
├── Dockerfile                   # Docker configuration (Hugging Face Spaces compatible)
├── index.bat                    # One-click Windows runner script
├── requirements.txt             # Python package dependencies
├── pro_dashboard.py             # Main application dashboard
├── app.py                       # Lightweight prototype
├── fii_stake_data.json          # Cached FII shareholding dataset
├── top_2000_tickers.json        # 2000+ NSE stock ticker universe
├── usa_tickers.json             # Russell 1000 & Nasdaq 100 ticker mapping
├── LICENSE                      # MIT License
└── README.md                    # Project documentation
```

---

## ⏰ Automated Workflows

The repository includes a GitHub Actions workflow located at `.github/workflows/fetch_fii_data.yml`:
- **Schedule:** Runs automatically every weekday at 8:00 AM IST (2:30 AM UTC).
- **Function:** Executes `scripts/fetch_fii_shareholding.py` to retrieve institutional shareholding data from Screener.in and commits updates back to `fii_stake_data.json` without requiring any manual intervention.

---

## 📊 Data Sources

| Source | Usage |
|---|---|
| **Yahoo Finance (`yfinance`)** | Historical OHLCV price and volume data, global indices, US tickers |
| **`ta` Library** | Technical indicators (RSI, MACD, Moving Averages, Bollinger Bands) |
| **NSE India (`nsepython`)** | Indian market sectoral indices and constituents |
| **Screener.in** | FII shareholding and fundamental metrics |
| **Economic Times** | Financial RSS news feeds |
| **TradingView** | US stock ticker news and real-time interactive charting |

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
