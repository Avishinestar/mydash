# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the App

```bash
pip install -r requirements.txt
streamlit run pro_dashboard.py
```

`app.py` is a simpler prototype; `pro_dashboard.py` is the main application.

## Architecture

Single-file Streamlit dashboard for Indian stock market analysis. All logic lives in `pro_dashboard.py` (~1055 lines).

### Structure within `pro_dashboard.py`

1. **Config (lines ~31–173)**: Hardcoded ticker lists — `NIFTY_50` (31 bluechip stocks), `SECTORS` (sector name → NSE index ticker), `SECTOR_CONSTITUENTS` (16 sectors × ~10 constituent tickers each), `GLOBAL_MARKETS` (20 global indices with market cap metadata), `ET_RSS_FEEDS` (4 Economic Times RSS feeds), `NIFTY_500` (large fallback list of ~250 NSE tickers grouped by sector).

2. **Optional dependency**: `nsepython` is imported with a try/except guard. When available, `get_nifty500_tickers()` fetches a live NSE constituent list; otherwise falls back to the hardcoded `NIFTY_500`. Similarly, `get_fiidii()` uses `nsepython.nse_fiidii` for FII/DII flow data.

3. **Data fetching (lines ~175–773)**: All functions use `@st.cache_data` (TTL 300–3600s). Key functions:
   - `get_volume_split_stocks()` — buys/sells volume split across daily + weekly for Nifty 500
   - `get_sector_data()` — returns/alpha for all NSE sector indices vs Nifty 50
   - `get_sector_performers(sector_name)` — best/worst stocks within a specific sector
   - `get_range_breakout_stocks()` — multi-signal breakout scanner (20D/50D/52W high proximity, volume surge, MACD, MA alignment, RSI)
   - `get_nifty500_weekly_rsi_scan()` — weekly RSI < 40 + price above 200-DMA for Nifty 500
   - `get_nifty_sensex_levels()` — Nifty/Sensex/VIX levels, Nifty RSI, % from ATH
   - `get_stock_info()` / `get_stock_data_daily()` / `get_stock_data_weekly()` — fundamentals and OHLCV for NIFTY_50
   - `get_global_markets_data()` — 20 global indices with ATH analysis
   - `get_top_10_overall_stocks()` — top performers across all SECTOR_CONSTITUENTS

4. **UI — 5 tabs (lines ~785–1054)**:
   - **"1 & 2: Sector Performance"**: Nifty/Sensex/VIX/FII/DII header bar; sector outperformance/underperformance alpha tables; best/worst sector constituent stocks; all-indices table; top 10 overall stocks
   - **"3 & 7: Technical Scanners"**: Range breakout candidates (multi-signal scored); weekly RSI oversold scan; volume analysis (buying vs selling pressure)
   - **"6: Fundamentals"**: Undervalued Nifty 50 stocks by P/E < 20 and ROE > 15%
   - **"4, 5, 8, 9: News & Macro"**: ET RSS feeds for Markets, Macro, Earnings, Companies
   - **"Global Markets"**: 20 major indices with ATH distance analysis

### Data flow
Yahoo Finance (`yfinance`) → pandas DataFrame → `ta` library indicators → `@st.cache_data` cache → Streamlit UI (plain dataframes, no Plotly)

### Caching
5-min TTL for price/volume data; 1-hour TTL for fundamentals and heavy scans (`get_nifty500_weekly_rsi_scan`, `get_stock_info`). A "Force Refresh All Data" button calls `st.cache_data.clear()`. Some fetch functions self-clear their cache on failure (e.g., `get_sector_data` clears if NIFTY 50 data is missing).
