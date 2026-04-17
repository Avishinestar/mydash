# Advanced Investor Dashboard

A Streamlit dashboard for Indian stock market analysis — built for active investors tracking Nifty 50, Nifty 500, sector trends, technical setups, and global markets.

## Features

- **Sector Performance** — Outperformance/underperformance alpha vs Nifty 50 for all NSE sector indices; best/worst constituent stocks per sector
- **Technical Scanners** — Range breakout scanner (20D/50D/52W high proximity, volume surge, MACD, MA alignment, RSI); weekly RSI oversold scan (RSI < 40 + price above 200-DMA)
- **Volume Analysis** — Buying vs selling pressure across Nifty 500 (daily + weekly)
- **Fundamentals** — Undervalued Nifty 50 stocks screened by P/E < 20 and ROE > 15%
- **News & Macro** — Live Economic Times RSS feeds (Markets, Macro, Earnings, Companies)
- **Global Markets** — 20 major indices with ATH distance analysis
- **FII/DII Flows** — Institutional buying/selling data; FII shareholding tracker (auto-updated daily via GitHub Actions)

## Running Locally

```bash
pip install -r requirements.txt
streamlit run pro_dashboard.py
```

Requires Python 3.9+.

## Data Sources

- **Price data**: Yahoo Finance via `yfinance`
- **Technical indicators**: `ta` library
- **NSE constituent lists**: `nsepython` (with hardcoded fallback)
- **FII shareholding**: Screener.in (fetched by GitHub Actions workflow)
- **News**: Economic Times RSS feeds

## Project Structure

```
pro_dashboard.py          # Main application (~1100 lines)
app.py                    # Simpler prototype
requirements.txt          # Python dependencies
fii_stake_data.json       # FII shareholding data (auto-updated daily)
scripts/
  fetch_fii_shareholding.py  # Script run by GitHub Actions
.github/workflows/
  fetch_fii_data.yml      # Scheduled workflow — updates FII data Mon–Fri 8 AM IST
```

## Automated Data Updates

The GitHub Actions workflow (`.github/workflows/fetch_fii_data.yml`) runs every weekday at 8 AM IST and commits updated FII shareholding data to `fii_stake_data.json`. No setup required once the repo is on GitHub.
