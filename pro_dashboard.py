import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import feedparser
import io
import warnings
from contextlib import nullcontext as _spinner
try:
    from nsepython import nse_eq_symbols
    _NSE_AVAILABLE = True
except Exception:
    _NSE_AVAILABLE = False

warnings.filterwarnings('ignore')

@st.cache_data(ttl=86400)  # refresh once a day
def get_nifty500_tickers():
    """Fetch live Nifty 500 constituent list from NSE and convert to yfinance format."""
    try:
        if _NSE_AVAILABLE:
            symbols = nse_eq_symbols()
            if symbols and len(symbols) > 100:
                return [s.strip() + ".NS" for s in symbols]
    except Exception:
        pass
    # Fallback to hardcoded list if NSE fetch fails
    return NIFTY_500

st.set_page_config(page_title="Advanced Investor Dashboard", layout="wide")

NIFTY_50 = [
    # Top 10 by weight
    "RELIANCE.NS", "HDFCBANK.NS", "BHARTIARTL.NS", "SBIN.NS", "ICICIBANK.NS",
    "TCS.NS", "BAJFINANCE.NS", "INFY.NS", "LT.NS", "HINDUNILVR.NS",
    # 11–20
    "SUNPHARMA.NS", "MARUTI.NS", "M&M.NS", "AXISBANK.NS", "HCLTECH.NS",
    "ITC.NS", "NTPC.NS", "KOTAKBANK.NS", "ONGC.NS", "TITAN.NS",
    # 21–30
    "ULTRACEMCO.NS", "ADANIPORTS.NS", "BEL.NS", "JSWSTEEL.NS", "POWERGRID.NS",
    "COALINDIA.NS", "BAJAJFINSV.NS", "BAJAJ-AUTO.NS", "TATASTEEL.NS", "ADANIENT.NS",
    # 31–40
    "NESTLEIND.NS", "ETERNAL.NS", "ASIANPAINT.NS", "WIPRO.NS", "HINDALCO.NS",
    "EICHERMOT.NS", "SBILIFE.NS", "GRASIM.NS", "SHRIRAMFIN.NS", "INDIGO.NS",
    # 41–50
    "JIOFIN.NS", "TECHM.NS", "HDFCLIFE.NS", "TRENT.NS", "TATAMOTORS.NS",
    "APOLLOHOSP.NS", "DRREDDY.NS", "TATACONSUM.NS", "CIPLA.NS", "MAXHEALTH.NS",
]

SECTORS = {
    "NIFTY 50": "^NSEI",
    "BANK": "^NSEBANK",
    "IT": "^CNXIT",
    "AUTO": "^CNXAUTO",
    "FMCG": "^CNXFMCG",
    "PHARMA": "^CNXPHARMA",
    "METAL": "^CNXMETAL",
    "ENERGY": "^CNXENERGY",
    "FINANCIAL SERVICES": "^CNXFIN",
    "REALTY": "^CNXREALTY",
    "MEDIA": "^CNXMEDIA",
    "PSU BANK": "^CNXPSUBANK",
    "INFRASTRUCTURE": "^CNXINFRA",
    "COMMODITIES": "^CNXCMDT",
    "CONSUMPTION": "^CNXCONSUM",
    "MNC": "^CNXMNC",
    "PSE": "^CNXPSE"
}

ET_RSS_FEEDS = {
    "Markets": "https://economictimes.indiatimes.com/markets/rssfeeds/2146842.cms",
    "Macro Economy": "https://economictimes.indiatimes.com/news/economy/macro-economy/rssfeeds/1373380680.cms",
    "Earnings": "https://economictimes.indiatimes.com/markets/stocks/earnings/rssfeeds/514120.cms",
    "Companies": "https://economictimes.indiatimes.com/industry/rssfeeds/13352306.cms"
}

GLOBAL_MARKETS = {
    "^GSPC": {"Country": "USA", "Name": "S&P 500", "MarketCap": 45.0},
    "^DJI": {"Country": "USA", "Name": "Dow Jones", "MarketCap": 11.0},
    "^IXIC": {"Country": "USA", "Name": "Nasdaq", "MarketCap": 25.0},
    "^FTSE": {"Country": "UK", "Name": "FTSE 100", "MarketCap": 3.2},
    "^GDAXI": {"Country": "Germany", "Name": "DAX", "MarketCap": 2.2},
    "^FCHI": {"Country": "France", "Name": "CAC 40", "MarketCap": 3.0},
    "^N225": {"Country": "Japan", "Name": "Nikkei 225", "MarketCap": 6.0},
    "000001.SS": {"Country": "China", "Name": "Shanghai Composite", "MarketCap": 6.5},
    "^HSI": {"Country": "Hong Kong", "Name": "Hang Seng", "MarketCap": 4.0},
    "^KS11": {"Country": "South Korea", "Name": "KOSPI", "MarketCap": 1.8},
    "^TWII": {"Country": "Taiwan", "Name": "Taiwan Weighted", "MarketCap": 2.1},
    "^AXJO": {"Country": "Australia", "Name": "ASX 200", "MarketCap": 1.7},
    "^GSPTSE": {"Country": "Canada", "Name": "TSX Composite", "MarketCap": 3.0},
    "^BVSP": {"Country": "Brazil", "Name": "Bovespa", "MarketCap": 1.0},
    "^MXX": {"Country": "Mexico", "Name": "IPC", "MarketCap": 0.5},
    "^SSMI": {"Country": "Switzerland", "Name": "SMI", "MarketCap": 1.5},
    "^STOXX50E": {"Country": "Eurozone", "Name": "Euro Stoxx 50", "MarketCap": 4.0},
    "^STI": {"Country": "Singapore", "Name": "STI Index", "MarketCap": 0.4},
    "^NSEI": {"Country": "India", "Name": "Nifty 50", "MarketCap": 4.5},
    "^BSESN": {"Country": "India", "Name": "BSE Sensex", "MarketCap": 4.5}
}

NIFTY_500 = [
    # Large Cap (current Nifty 50)
    "RELIANCE.NS","HDFCBANK.NS","BHARTIARTL.NS","SBIN.NS","ICICIBANK.NS",
    "TCS.NS","BAJFINANCE.NS","INFY.NS","LT.NS","HINDUNILVR.NS",
    "SUNPHARMA.NS","MARUTI.NS","M&M.NS","AXISBANK.NS","HCLTECH.NS",
    "ITC.NS","NTPC.NS","KOTAKBANK.NS","ONGC.NS","TITAN.NS",
    "ULTRACEMCO.NS","ADANIPORTS.NS","BEL.NS","JSWSTEEL.NS","POWERGRID.NS",
    "COALINDIA.NS","BAJAJFINSV.NS","BAJAJ-AUTO.NS","TATASTEEL.NS","ADANIENT.NS",
    "NESTLEIND.NS","ETERNAL.NS","ASIANPAINT.NS","WIPRO.NS","HINDALCO.NS",
    "EICHERMOT.NS","SBILIFE.NS","GRASIM.NS","SHRIRAMFIN.NS","INDIGO.NS",
    "JIOFIN.NS","TECHM.NS","HDFCLIFE.NS","TRENT.NS","TATAMOTORS.NS",
    "APOLLOHOSP.NS","DRREDDY.NS","TATACONSUM.NS","CIPLA.NS","MAXHEALTH.NS",
    # Other Large Cap outside Nifty 50
    "LICI.NS",
    # Banking & Finance
    "INDUSINDBK.NS","BANKBARODA.NS","PNB.NS","FEDERALBNK.NS","IDFCFIRSTB.NS","CANBK.NS",
    "UNIONBANK.NS","INDIANB.NS","BANKINDIA.NS","CENTRALBK.NS","MAHABANK.NS","UCOBANK.NS",
    "CHOLAFIN.NS","MUTHOOTFIN.NS","RECLTD.NS","PFC.NS","HDFCAMC.NS","SBICARD.NS",
    "ABCAPITAL.NS","SHRIRAMFIN.NS","MANAPPURAM.NS","LICHSGFIN.NS","IIFL.NS","SUNDARMFIN.NS",
    "CANFINHOME.NS","REPCO.NS","PNBHOUSING.NS","UGROCAP.NS","CREDITACC.NS",
    # IT & Tech
    "LTIM.NS","COFORGE.NS","PERSISTENT.NS","MPHASIS.NS","KPITTECH.NS","LTTS.NS",
    "OFSS.NS","HEXT.NS","ZENSAR.NS","TATAELXSI.NS","CYIENT.NS",
    "MASTEK.NS","BIRLASOFT.NS","SONATSOFTW.NS","TANLA.NS","ROUTE.NS",
    # Auto & Auto Ancillaries
    "HEROMOTOCO.NS","EICHERMOT.NS","TVSMOTOR.NS","ASHOKLEY.NS","MOTHERSON.NS","BOSCHLTD.NS",
    "ESCORTS.NS","APOLLOTYRE.NS","MRF.NS","CEAT.NS","BALKRISIND.NS","EXIDEIND.NS",
    "AMARARAJA.NS","SUNDRMFAST.NS","BHARATFORG.NS","ENDURANCE.NS","SUPRAJIT.NS","GABRIEL.NS",
    # Pharma & Healthcare
    "CIPLA.NS","DRREDDY.NS","DIVISLAB.NS","LUPIN.NS","AUROPHARMA.NS","TORNTPHARM.NS",
    "ZYDUSLIFE.NS","ALKEM.NS","BIOCON.NS","IPCA.NS","GLENMARK.NS","PFIZER.NS",
    "ABBOTINDIA.NS","SANOFI.NS","LAURUSLABS.NS","GRANULES.NS","SUVEN.NS","NATCOPHARM.NS",
    "AJANTPHARM.NS","JBCHEPHARM.NS","ERIS.NS","VINATIORGA.NS",
    # FMCG & Consumer
    "BRITANNIA.NS","TATACONSUM.NS","GODREJCP.NS","DABUR.NS","MARICO.NS","VBL.NS",
    "COLPAL.NS","EMAMILTD.NS","RADICO.NS","VSTIND.NS","UNITDSPR.NS","PGHH.NS",
    # Metals & Mining
    "TATASTEEL.NS","JSWSTEEL.NS","HINDALCO.NS","VEDL.NS","COALINDIA.NS","NMDC.NS",
    "SAIL.NS","JINDALSTEL.NS","NATIONALUM.NS","RATNAMANI.NS","WELCORP.NS","APL.NS",
    "JSPL.NS","HINDZINC.NS","MOIL.NS","GMDC.NS",
    # Energy & Power
    "IOC.NS","BPCL.NS","GAIL.NS","HINDPETRO.NS","TATAPOWER.NS","PETRONET.NS",
    "ADANIGREEN.NS","ADANIPOWER.NS","TORNTPOWER.NS","CESC.NS","NHPC.NS","SJVN.NS",
    "IREDA.NS","RPOWER.NS","JPPOWER.NS",
    # Infrastructure & Cement
    "AMBUJACEM.NS","SHREECEM.NS","ACC.NS","GMRAIRPORT.NS",
    "IRB.NS","HCC.NS","NBCC.NS","KEC.NS","KALPATPOWER.NS","THERMAX.NS","CUMMINSIND.NS",
    "ABB.NS","SIEMENS.NS","VOLTAS.NS","HAVELLS.NS","POLYCAB.NS","KEI.NS","FINOLEX.NS",
    # Realty
    "DLF.NS","LODHA.NS","GODREJPROP.NS","OBEROIRLTY.NS","PRESTIGE.NS",
    "PHOENIXLTD.NS","BRIGADE.NS","SOBHA.NS","MAHLIFE.NS","SUNTECK.NS","KOLTEPATIL.NS",
    # Chemicals & Specialty
    "PIDILITIND.NS","SRF.NS","AARTIIND.NS","DEEPAKNTR.NS","NAVINFLUOR.NS","FINEORG.NS",
    "TATACHEM.NS","UPL.NS","PIIND.NS","COROMANDEL.NS","RALLIS.NS","BASF.NS",
    "GALAXYSURF.NS","CLEAN.NS","ROSSARI.NS","SUDARSCHEM.NS",
    # Consumption & Retail
    "TRENT.NS","PAGEIND.NS","BATAINDIA.NS","CROMPTON.NS","DIXON.NS","RELAXO.NS",
    "RAYMOND.NS","VEDANT.NS","DMART.NS","NYKAA.NS","ETERNAL.NS","JUBLFOOD.NS",
    "DEVYANI.NS","WESTLIFE.NS","SAPPHIRE.NS",
    # Hotels & Tourism
    "INDHOTEL.NS","LEMONTREE.NS","CHALET.NS","EIHOTEL.NS","MHRIL.NS",
    # Logistics & Transport
    "BLUEDART.NS","DELHIVERY.NS","CONCOR.NS","MAHLOG.NS","TCI.NS","VRL.NS",
    # Telecom & Media
    "IDEA.NS","TATACOMM.NS","HFCL.NS","SUNTV.NS","PVRINOX.NS","SAREGAMA.NS","NAZARA.NS",
    # Defence & Aerospace
    "HAL.NS","BEL.NS","BHEL.NS","BEML.NS","PARAS.NS","MAZDOCK.NS","COCHINSHIP.NS",
    # Insurance & New-Age Financial
    "SBILIFE.NS","HDFCLIFE.NS","ICICIGI.NS","LICI.NS","MAXHEALTH.NS",
    "JIOFIN.NS","POLICYBZR.NS","PAYTM.NS","NAUKRI.NS","CARTRADE.NS",
    # Others / Diversified
    "ADANITRANS.NS","ATUL.NS",
    "BERGEPAINT.NS","CASTROLIND.NS","GSPL.NS","HONAUT.NS","IGL.NS","MGL.NS",
    "MCDOWELL-N.NS",
]

SECTOR_CONSTITUENTS = {
    "BANK": ["HDFCBANK.NS", "SBIN.NS", "ICICIBANK.NS", "AXISBANK.NS", "KOTAKBANK.NS", "INDUSINDBK.NS", "BANKBARODA.NS", "PNB.NS", "FEDERALBNK.NS", "AUBANK.NS"],
    "IT": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS", "LTIM.NS", "PERSISTENT.NS", "OFSS.NS", "MPHASIS.NS", "COFORGE.NS"],
    "AUTO": ["MARUTI.NS", "TATAMOTORS.NS", "M&M.NS", "BAJAJ-AUTO.NS", "HEROMOTOCO.NS", "EICHERMOT.NS", "TVSMOTOR.NS", "ASHOKLEY.NS", "MOTHERSON.NS", "BOSCHLTD.NS"],
    "FMCG": ["ITC.NS", "HINDUNILVR.NS", "NESTLEIND.NS", "BRITANNIA.NS", "TATACONSUM.NS", "GODREJCP.NS", "DABUR.NS", "MARICO.NS", "VBL.NS", "COLPAL.NS"],
    "PHARMA": ["SUNPHARMA.NS", "CIPLA.NS", "DRREDDY.NS", "DIVISLAB.NS", "LUPIN.NS", "AUROPHARMA.NS", "TORNTPHARM.NS", "ZYDUSLIFE.NS", "ALKEM.NS", "BIOCON.NS"],
    "METAL": ["TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "VEDL.NS", "COALINDIA.NS", "NMDC.NS", "SAIL.NS", "JINDALSTEL.NS", "NATIONALUM.NS", "RATNAMANI.NS"],
    "ENERGY": ["RELIANCE.NS", "ONGC.NS", "NTPC.NS", "POWERGRID.NS", "IOC.NS", "BPCL.NS", "GAIL.NS", "HINDPETRO.NS", "TATAPOWER.NS", "PETRONET.NS"],
    "FINANCIAL SERVICES": ["BAJFINANCE.NS", "BAJAJFINSV.NS", "CHOLAFIN.NS", "MUTHOOTFIN.NS", "RECLTD.NS", "PFC.NS", "HDFCAMC.NS", "SBICARD.NS", "ABCAPITAL.NS", "SHRIRAMFIN.NS"],
    "REALTY": ["DLF.NS", "LODHA.NS", "GODREJPROP.NS", "OBEROIRLTY.NS", "PRESTIGE.NS", "PHOENIXLTD.NS", "BRIGADE.NS", "SOBHA.NS", "MAHLIFE.NS", "SUNTECK.NS"],
    "MEDIA": ["PVRINOX.NS", "SUNTV.NS", "NETWORK18.NS", "NETWORK18.NS", "NAVNETEDUL.NS", "NDTV.NS", "HATHWAY.NS", "DISHTV.NS", "NAZARA.NS", "SAREGAMA.NS"],
    "PSU BANK": ["SBIN.NS", "BANKBARODA.NS", "PNB.NS", "CANBK.NS", "UNIONBANK.NS", "INDIANB.NS", "BANKINDIA.NS", "CENTRALBK.NS", "MAHABANK.NS", "UCOBANK.NS"],
    "INFRASTRUCTURE": ["LT.NS", "GRASIM.NS", "ULTRACEMCO.NS", "ADANIPORTS.NS", "AMBUJACEM.NS", "SHREECEM.NS", "ACC.NS", "GMRAIRPORT.NS", "IRB.NS", "HCC.NS"],
    "COMMODITIES": ["TATACHEM.NS", "UPL.NS", "PIIND.NS", "COROMANDEL.NS", "SRF.NS", "AARTIIND.NS", "DEEPAKNTR.NS", "TATASTEEL.NS", "JSWSTEEL.NS", "VEDL.NS"],
    "CONSUMPTION": ["ASIANPAINT.NS", "TITAN.NS", "TRENT.NS", "PAGEIND.NS", "ETERNAL.NS", "JUBLFOOD.NS", "BATAINDIA.NS", "VOLTAS.NS", "CROMPTON.NS", "DIXON.NS"],
    "MNC": ["MARUTI.NS", "NESTLEIND.NS", "BRITANNIA.NS", "CUMMINSIND.NS", "ABB.NS", "BOSCHLTD.NS", "SIEMENS.NS", "COLPAL.NS", "BATAINDIA.NS", "CASTROLIND.NS"],
    "PSE": ["NTPC.NS", "ONGC.NS", "POWERGRID.NS", "COALINDIA.NS", "IOC.NS", "BPCL.NS", "GAIL.NS", "NMDC.NS", "BHEL.NS", "HAL.NS", "BEL.NS"]
}

@st.cache_data(ttl=300)
def get_volume_split_stocks():
    """
    Scans Nifty 500 (NSE) for stocks with consistently high buying/selling volume
    on BOTH daily (preceding day) AND weekly (last 5 trading days) basis.
    Buying Volume  = Volume × (Close − Low)  / (High − Low)
    Selling Volume = Volume × (High − Close) / (High − Low)
    Only stocks that rank high on BOTH timeframes appear in each table.
    """
    try:
        live_tickers = get_nifty500_tickers()
        df = yf.download(live_tickers, period="30d", interval="1d", progress=False)
        all_results = []

        for t in live_tickers:
            try:
                if isinstance(df.columns, pd.MultiIndex):
                    if t not in df.columns.levels[1]:
                        continue
                    df_t = df.xs(t, axis=1, level=1).dropna()
                else:
                    df_t = df.dropna()

                if len(df_t) < 8:
                    continue

                # --- Daily: preceding completed trading day ---
                row      = df_t.iloc[-2]
                prev_row = df_t.iloc[-3]

                o = float(row['Open'])
                h = float(row['High'])
                l = float(row['Low'])
                c = float(row['Close'])
                vol_day = float(row['Volume'])
                prev_close = float(prev_row['Close'])

                if h == l or vol_day == 0:
                    continue

                day_buy_vol  = vol_day * (c - l) / (h - l)
                day_sell_vol = vol_day * (h - c) / (h - l)
                day_buy_pct  = round((day_buy_vol  / vol_day) * 100, 1)
                day_sell_pct = round((day_sell_vol / vol_day) * 100, 1)
                day_change   = round(((c / prev_close) - 1) * 100, 2)
                candle = "Green ▲" if c >= o else "Red ▼"

                # --- Weekly: sum of last 5 completed trading days ---
                week_rows = df_t.iloc[-6:-1]  # 5 days, excluding today
                week_buy_vol  = 0.0
                week_sell_vol = 0.0
                week_total_vol = 0.0
                for _, wr in week_rows.iterrows():
                    wh = float(wr['High']); wl = float(wr['Low'])
                    wc = float(wr['Close']); wv = float(wr['Volume'])
                    if wh == wl or wv == 0:
                        continue
                    week_buy_vol  += wv * (wc - wl) / (wh - wl)
                    week_sell_vol += wv * (wh - wc) / (wh - wl)
                    week_total_vol += wv

                if week_total_vol == 0:
                    continue

                week_buy_pct  = round((week_buy_vol  / week_total_vol) * 100, 1)
                week_sell_pct = round((week_sell_vol / week_total_vol) * 100, 1)

                all_results.append({
                    "stock": t.replace(".NS", ""),
                    "prev day close (NSE)": round(c, 2),
                    "day change %": day_change,
                    "candle": candle,
                    "daily buying vol": int(day_buy_vol),
                    "daily buying %": day_buy_pct,
                    "weekly buying vol": int(week_buy_vol),
                    "weekly buying %": week_buy_pct,
                    "daily selling vol": int(day_sell_vol),
                    "daily selling %": day_sell_pct,
                    "weekly selling vol": int(week_sell_vol),
                    "weekly selling %": week_sell_pct,
                    "_day_bvol":  day_buy_vol,
                    "_week_bvol": week_buy_vol,
                    "_day_svol":  day_sell_vol,
                    "_week_svol": week_sell_vol,
                })
            except Exception:
                pass

        if not all_results:
            return {"buying": [], "selling": []}

        # Split into two exclusive pools based on which side dominates on BOTH timeframes
        buying_pool  = []  # buying vol > selling vol on daily AND weekly
        selling_pool = []  # selling vol > buying vol on daily AND weekly

        for r in all_results:
            day_buy_dominant  = r["_day_bvol"]  > r["_day_svol"]
            week_buy_dominant = r["_week_bvol"] > r["_week_svol"]
            if day_buy_dominant and week_buy_dominant:
                buying_pool.append(r)
            elif not day_buy_dominant and not week_buy_dominant:
                selling_pool.append(r)
            # Mixed signals (one timeframe each) → excluded from both tables

        # Within each pool, rank by total buying/selling volume (daily + weekly combined)
        top_buying  = sorted(buying_pool,  key=lambda x: x["_day_bvol"] + x["_week_bvol"], reverse=True)[:10]
        top_selling = sorted(selling_pool, key=lambda x: x["_day_svol"] + x["_week_svol"], reverse=True)[:10]

        for i, r in enumerate(top_buying):
            r["sr. no."] = i + 1
        for i, r in enumerate(top_selling):
            r["sr. no."] = i + 1

        return {"buying": top_buying, "selling": top_selling}
    except Exception:
        return {"buying": [], "selling": []}

@st.cache_data(ttl=300)
def get_sector_data():
    import time as _time
    tickers = list(SECTORS.values())
    name_by_ticker = {v: k for k, v in SECTORS.items()}
    data = {}

    # ── Step 1: one batch download (single HTTP round-trip, reduces rate-limit hits) ──
    batch_df = pd.DataFrame()
    for attempt in range(3):
        try:
            batch_df = yf.download(tickers, period="1y", interval="1d", progress=False)
            if not batch_df.empty:
                break
        except Exception:
            pass
        _time.sleep(3)

    # ── Step 2: extract per-ticker series; fall back to individual fetch if missing ──
    for ticker, name in name_by_ticker.items():
        df_t = pd.DataFrame()
        try:
            if not batch_df.empty and isinstance(batch_df.columns, pd.MultiIndex):
                if ticker in batch_df.columns.get_level_values(1):
                    df_t = batch_df.xs(ticker, axis=1, level=1).dropna(subset=["Close"])
        except Exception:
            pass

        # Individual fallback if batch missed this ticker (rate-limited slot)
        if len(df_t) < 64:
            for retry in range(3):
                try:
                    _time.sleep(1.5 + retry * 2)
                    df_t = yf.Ticker(ticker).history(period="1y").dropna(subset=["Close"])
                    if len(df_t) >= 64:
                        break
                except Exception:
                    pass

        if len(df_t) < 64:
            continue

        try:
            data[name] = {
                "Daily":     float((df_t['Close'].iloc[-1] / df_t['Close'].iloc[-2])  - 1) * 100,
                "Weekly":    float((df_t['Close'].iloc[-1] / df_t['Close'].iloc[-5])  - 1) * 100,
                "Monthly":   float((df_t['Close'].iloc[-1] / df_t['Close'].iloc[-21]) - 1) * 100,
                "Quarterly": float((df_t['Close'].iloc[-1] / df_t['Close'].iloc[-63]) - 1) * 100,
                "Yearly":    float((df_t['Close'].iloc[-1] / df_t['Close'].iloc[0])   - 1) * 100,
            }
        except Exception:
            pass

    if "NIFTY 50" not in data:
        get_sector_data.clear()
    return data

@st.cache_data(ttl=300)
def fetch_rss_news(feed_url):
    feed = feedparser.parse(feed_url)
    entries = []
    for entry in feed.entries[:10]:
        entries.append({
            "Title": entry.title,
            "Link": entry.link,
            "Published": entry.published if hasattr(entry, 'published') else "Recent"
        })
    return entries

@st.cache_data(ttl=300)
def get_stock_data_daily():
    df = yf.download(NIFTY_50, period="1y", interval="1d", progress=False)
    return df

@st.cache_data(ttl=3600)
def get_stock_data_weekly():
    df = yf.download(NIFTY_50, period="2y", interval="1wk", progress=False)
    return df

@st.cache_data(ttl=3600)
def get_nifty500_weekly_rsi_scan():
    """Scan Nifty 500 universe for stocks with weekly RSI < 40 and price above 200-DMA.
    Returns top 20 sorted by RSI ascending."""
    tickers = get_nifty500_tickers()
    weekly_df = yf.download(tickers, period="2y", interval="1wk", progress=False)
    daily_df  = yf.download(tickers, period="1y",  interval="1d",  progress=False)
    candidates = []
    for t in tickers:
        try:
            if isinstance(weekly_df.columns, pd.MultiIndex):
                if t not in weekly_df.columns.get_level_values(1): continue
                w_df = weekly_df.xs(t, axis=1, level=1).dropna()
            else:
                w_df = weekly_df.dropna()
            if isinstance(daily_df.columns, pd.MultiIndex):
                if t not in daily_df.columns.get_level_values(1): continue
                d_df = daily_df.xs(t, axis=1, level=1).dropna()
            else:
                d_df = daily_df.dropna()
            if len(w_df) < 15 or len(d_df) < 200: continue
            w_rsi = float(ta.momentum.RSIIndicator(w_df['Close'], window=14).rsi().iloc[-1])
            d_200dma = float(d_df['Close'].tail(200).mean())
            current_price = float(d_df['Close'].iloc[-1])
            if w_rsi < 40 and current_price > d_200dma:
                candidates.append({
                    "Ticker": t.replace(".NS", ""),
                    "Weekly RSI": round(w_rsi, 1),
                    "Price": round(current_price, 2),
                    "200-DMA": round(d_200dma, 2),
                    "% Above 200-DMA": round((current_price / d_200dma - 1) * 100, 1),
                })
        except Exception:
            pass
    candidates.sort(key=lambda x: x["Weekly RSI"])
    return candidates[:20]

# ─────────────────────────────────────────────────────────────────────────────
# DCF Intrinsic Value Scanner — Nifty 500
# ─────────────────────────────────────────────────────────────────────────────

def _dcf(fcf, growth, terminal, discount, years=10):
    """Present value of projected FCF stream plus terminal value."""
    if fcf is None or fcf <= 0 or discount <= terminal:
        return None
    pv = sum(
        fcf * ((1 + growth) ** t) / ((1 + discount) ** t)
        for t in range(1, years + 1)
    )
    tv = fcf * ((1 + growth) ** years) * (1 + terminal) / (discount - terminal)
    pv += tv / ((1 + discount) ** years)
    return pv


def _dcf_remarks(symbol, price, base_iv, pct_off, pe, peg, fcf_yield, fcf_margin, eps_1y, g_base):
    """Generate expert investor insight string for a stock's DCF valuation."""
    parts = []

    if pct_off <= -20:
        parts.append(f"Trades {abs(pct_off):.0f}% below DCF intrinsic value — rare margin of safety; strong accumulation zone for patient, long-term capital.")
    elif pct_off <= -10:
        parts.append(f"Meaningful {abs(pct_off):.0f}% discount to intrinsic value — market yet to recognise full earnings power; accumulate in tranches.")
    elif pct_off <= -3:
        parts.append(f"Modestly undervalued ({abs(pct_off):.0f}% below DCF base case) — compelling entry as earnings visibility improves.")
    elif pct_off <= 5:
        parts.append(f"Fairly valued — DCF and market price are in tight alignment; ideal for SIP-style accumulation without timing risk.")
    else:
        parts.append(f"Trading {pct_off:.0f}% above base DCF — market pricing-in future growth; execution risk elevated at this premium.")

    if isinstance(pe, (int, float)):
        if pe < 10:
            parts.append(f"Single-digit PE ({pe}x) warrants earnings-quality check — verify whether it reflects a cyclical trough or structural impairment.")
        elif pe < 18:
            parts.append(f"Reasonable {pe}x PE leaves room for re-rating as cash flows compound.")
        elif pe < 30:
            parts.append(f"Mid-range PE of {pe}x reflects quality franchise; watch for operating-leverage unlock to justify valuation.")
        else:
            parts.append(f"Rich {pe}x PE demands consistent double-digit growth to avoid de-rating — monitor quarterly guidance closely.")

    if isinstance(peg, (int, float)):
        if peg < 0.8:
            parts.append(f"PEG of {peg}x is sub-1 — growth is gifted at a discount; classic GARP opportunity.")
        elif peg < 1.5:
            parts.append(f"PEG of {peg}x sits in fair-value range — growth is reasonably priced for the quality on offer.")
        elif peg > 2.0:
            parts.append(f"Elevated PEG of {peg}x — hold only if competitive moat is durable and widening.")

    if isinstance(fcf_yield, (int, float)):
        if fcf_yield > 7:
            parts.append(f"Exceptional FCF yield of {fcf_yield:.1f}% — cash machine capable of sustained buybacks or dividends.")
        elif fcf_yield > 4:
            parts.append(f"Healthy {fcf_yield:.1f}% FCF yield signals disciplined capital allocation and earnings quality.")
        elif fcf_yield > 1:
            parts.append(f"Positive FCF yield ({fcf_yield:.1f}%) — business self-funds growth without dilution risk.")
        else:
            parts.append(f"Sub-1% FCF yield flags heavy reinvestment phase — validate capex generates adequate return on capital.")

    if isinstance(fcf_margin, (int, float)) and fcf_margin > 0:
        if fcf_margin > 20:
            parts.append(f"Exceptional {fcf_margin:.0f}% FCF margin — asset-light model with strong pricing power.")
        elif fcf_margin > 10:
            parts.append(f"Solid {fcf_margin:.0f}% FCF margin confirms earnings reliably convert to cash.")

    if isinstance(eps_1y, (int, float)):
        if eps_1y > 25:
            parts.append(f"Accelerating {eps_1y:.0f}% EPS growth is the primary re-rating catalyst — momentum will follow earnings.")
        elif eps_1y > 0:
            parts.append(f"Steady {eps_1y:.0f}% EPS growth provides confidence in the DCF growth trajectory.")
        elif eps_1y < -10:
            parts.append(f"Earnings under pressure ({eps_1y:.0f}% YoY) — DCF assumes recovery; verify if cyclical or structural headwind.")

    return " ".join(parts) if parts else f"Monitor {symbol} for FCF consistency and earnings-visibility improvement before committing capital."


@st.cache_data(ttl=3600)
def get_dcf_valuation_stocks():
    """
    Scans Nifty 500 for stocks near their DCF intrinsic value.
    Three scenarios: Base (11% WACC), Bearish (12% WACC), Bear (13% WACC).
    Filters: -35% to +15% of base-case intrinsic value.
    """
    from concurrent.futures import ThreadPoolExecutor, as_completed

    # Reverse-map: ticker → sector
    stock_sector = {}
    for sec, constituents in SECTOR_CONSTITUENTS.items():
        for t in constituents:
            stock_sector[t] = sec

    tickers = get_nifty500_tickers()

    def fetch_one(ticker):
        try:
            yft  = yf.Ticker(ticker)
            info = yft.info

            price  = info.get("currentPrice") or info.get("regularMarketPrice") or info.get("previousClose")
            shares = info.get("sharesOutstanding")
            mkt_cap = info.get("marketCap")
            fcf    = info.get("freeCashflow")
            op_cf  = info.get("operatingCashflow")
            revenue = info.get("totalRevenue")

            if not price or price <= 0 or not shares or shares <= 0:
                return None

            # Fallback: estimate FCF from operating cash flow
            if (fcf is None or fcf <= 0) and op_cf and op_cf > 0:
                fcf = op_cf * 0.72
            if not fcf or fcf <= 0:
                return None

            pe         = info.get("trailingPE")
            book_value = info.get("bookValue")
            peg        = info.get("pegRatio")
            eps_1y_raw = info.get("earningsGrowth")   # decimal
            rev_growth = info.get("revenueGrowth") or 0.0

            # 3Y / 5Y EPS CAGR from annual income statement
            eps_3y, eps_5y = None, None
            try:
                inc = yft.income_stmt
                if inc is not None and not inc.empty:
                    ni_row = None
                    for rn in ["Net Income", "Net Income Common Stockholders", "NetIncome"]:
                        if rn in inc.index:
                            ni_row = inc.loc[rn].dropna()
                            break
                    if ni_row is not None and len(ni_row) >= 2:
                        ni_latest = float(ni_row.iloc[0])
                        if len(ni_row) >= 4:
                            ni_3ya = float(ni_row.iloc[3])
                            if ni_latest > 0 and ni_3ya > 0:
                                eps_3y = (ni_latest / ni_3ya) ** (1 / 3) - 1
                        if len(ni_row) >= 6:
                            ni_5ya = float(ni_row.iloc[5])
                            if ni_latest > 0 and ni_5ya > 0:
                                eps_5y = (ni_latest / ni_5ya) ** (1 / 5) - 1
            except Exception:
                pass

            # Base growth rate for DCF
            eps_1y = eps_1y_raw
            if eps_1y and eps_1y > 0:
                g_base = min(eps_1y, 0.30)
            elif rev_growth > 0:
                g_base = min(rev_growth, 0.25)
            elif eps_3y and eps_3y > 0:
                g_base = min(eps_3y, 0.25)
            else:
                g_base = 0.07
            g_base = max(g_base, 0.03)

            # ── Three DCF scenarios ───────────────────────────────────────────
            # Base:    moderate growth, 11% WACC, 4.0% terminal
            # Bearish: 60% of base growth, 12% WACC, 3.5% terminal
            # Bear:    30% of base growth, 13% WACC, 2.5% terminal
            base_total    = _dcf(fcf, g_base,                   0.040, 0.110)
            bearish_total = _dcf(fcf, g_base * 0.60,            0.035, 0.120)
            bear_total    = _dcf(fcf, max(g_base * 0.30, 0.01), 0.025, 0.130)

            if base_total is None or base_total <= 0:
                return None

            base_iv    = base_total    / shares
            bearish_iv = bearish_total / shares if bearish_total else None
            bear_iv    = bear_total    / shares if bear_total    else None

            # Filter: within -35% to +15% of base IV
            pct_off = (price / base_iv - 1) * 100
            if pct_off > 15 or pct_off < -35:
                return None

            fcf_yield  = (fcf / mkt_cap  * 100) if mkt_cap  and mkt_cap  > 0 else None
            fcf_margin = (fcf / revenue  * 100) if revenue  and revenue  > 0 else None

            sector = stock_sector.get(ticker, info.get("sector", "—"))
            name   = info.get("longName") or info.get("shortName") or ticker.replace(".NS", "")

            return {
                "_ticker":  ticker,
                "_sector":  sector,
                "_g_base":  g_base,
                "_pct_off": pct_off,
                "_pe":      pe,
                "_peg":     peg,
                "_fcfy":    fcf_yield,
                "_fcfm":    fcf_margin,
                "_eps1y":   (eps_1y * 100) if eps_1y is not None else None,
                "name":                   name,
                "price (₹)":              round(price, 2),
                "base case DCF IV (₹)":   round(base_iv, 2),
                "bearish DCF IV (₹)":     round(bearish_iv, 2) if bearish_iv else "N/A",
                "bear case DCF IV (₹)":   round(bear_iv,    2) if bear_iv    else "N/A",
                "% to intrinsic value":   round(pct_off, 1),
                "current PE":             round(pe, 1) if pe else "N/A",
                "current PEG":            round(peg, 2) if peg else "N/A",
                "1Y EPS growth %":        round(eps_1y * 100, 1) if eps_1y is not None else "N/A",
                "3Y EPS CAGR %":          round(eps_3y * 100, 1) if eps_3y is not None else "N/A",
                "5Y EPS CAGR %":          round(eps_5y * 100, 1) if eps_5y is not None else "N/A",
                "book value (₹)":         round(book_value, 2)   if book_value           else "N/A",
                "FCF yield %":            round(fcf_yield, 2)    if fcf_yield is not None else "N/A",
                "FCF margin %":           round(fcf_margin, 2)   if fcf_margin is not None else "N/A",
            }
        except Exception:
            return None

    # Parallel fetch with 18 workers
    raw = []
    with ThreadPoolExecutor(max_workers=18) as ex:
        futs = {ex.submit(fetch_one, t): t for t in tickers}
        for f in as_completed(futs):
            r = f.result()
            if r:
                raw.append(r)

    if not raw:
        return []

    # Compute industry median PE per sector from the results set
    sector_pes = {}
    for r in raw:
        pe_v = r["_pe"]
        if isinstance(pe_v, (int, float)) and 0 < pe_v < 200:
            sector_pes.setdefault(r["_sector"], []).append(pe_v)
    sector_median_pe = {
        s: round(sorted(v)[len(v) // 2], 1)
        for s, v in sector_pes.items() if v
    }

    # Build final display rows
    results = []
    for r in raw:
        symbol = r["_ticker"].replace(".NS", "")
        remarks = _dcf_remarks(
            symbol,
            r["price (₹)"],
            r["base case DCF IV (₹)"],
            r["_pct_off"],
            r["_pe"],
            r["_peg"],
            r["_fcfy"],
            r["_fcfm"],
            r["_eps1y"],
            r["_g_base"],
        )
        results.append({
            "name":                   r["name"],
            "price (₹)":              r["price (₹)"],
            "base case DCF IV (₹)":   r["base case DCF IV (₹)"],
            "bearish DCF IV (₹)":     r["bearish DCF IV (₹)"],
            "bear case DCF IV (₹)":   r["bear case DCF IV (₹)"],
            "industry PE":            sector_median_pe.get(r["_sector"], "N/A"),
            "current PE":             r["current PE"],
            "current PEG":            r["current PEG"],
            "1Y EPS growth %":        r["1Y EPS growth %"],
            "3Y EPS CAGR %":          r["3Y EPS CAGR %"],
            "5Y EPS CAGR %":          r["5Y EPS CAGR %"],
            "book value (₹)":         r["book value (₹)"],
            "FCF yield %":            r["FCF yield %"],
            "FCF margin %":           r["FCF margin %"],
            "% to intrinsic value":   r["% to intrinsic value"],
            "remarks":                remarks,
        })

    # Sort: most undervalued first
    results.sort(key=lambda x: x["% to intrinsic value"] if isinstance(x["% to intrinsic value"], (int, float)) else 0)
    for i, r in enumerate(results):
        r["sr. no."] = i + 1

    return results


@st.cache_data(ttl=3600)
def get_stock_info():
    info_dict = {}
    for t in NIFTY_50:
        try:
            ticker = yf.Ticker(t)
            info = ticker.info
            info_dict[t] = info
        except:
            pass
    return info_dict

@st.cache_data(ttl=300)
def get_global_markets_data():
    results = []
    tickers = list(GLOBAL_MARKETS.keys())
    try:
        df = yf.download(tickers, period="max", interval="1d", progress=False)
        for t in tickers:
            try:
                if isinstance(df.columns, pd.MultiIndex):
                    df_t = df.xs(t, axis=1, level=1).dropna()
                else:
                    df_t = df.dropna()
                
                if df_t.empty or len(df_t) < 2: continue
                
                current = float(df_t['Close'].iloc[-1])
                prev = float(df_t['Close'].iloc[-2])
                ath = float(df_t['High'].max())
                
                pct_day = ((current / prev) - 1) * 100
                pct_month = ((current / float(df_t['Close'].iloc[-21])) - 1) * 100 if len(df_t) >= 21 else 0
                pct_quarter = ((current / float(df_t['Close'].iloc[-63])) - 1) * 100 if len(df_t) >= 63 else 0
                pct_year = ((current / float(df_t['Close'].iloc[-252])) - 1) * 100 if len(df_t) >= 252 else 0
                pct_3year = ((current / float(df_t['Close'].iloc[-756])) - 1) * 100 if len(df_t) >= 756 else 0
                
                pct_ath = ((current / ath) - 1) * 100
                
                if pct_ath >= -2:
                    remark = "Trading near All-Time High; exceptionally strong momentum."
                elif pct_ath >= -5:
                    remark = "Slight consolidation just below ATH."
                elif pct_ath >= -10:
                    remark = "Healthy correction within a broader uptrend."
                elif pct_ath >= -20:
                    remark = "In a correction phase; watch for base formation."
                else:
                    remark = "In a bear market drawdown (>= 20% off ATH)."
                    
                results.append({
                    "name of country": GLOBAL_MARKETS[t]["Country"],
                    "name of index": GLOBAL_MARKETS[t]["Name"],
                    "indices current value": round(current, 2),
                    "% of current value from preceding day": round(pct_day, 2),
                    "monthly %": round(pct_month, 2),
                    "quarterly %": round(pct_quarter, 2),
                    "yearly %": round(pct_year, 2),
                    "3-year %": round(pct_3year, 2),
                    "its ATH": round(ath, 2),
                    "% from ATH": round(pct_ath, 2),
                    "remarks for insights from investor": remark,
                    "Ticker": t
                })
            except Exception:
                pass
                
        results = sorted(results, key=lambda x: GLOBAL_MARKETS[x["Ticker"]]["MarketCap"], reverse=True)
        for i, r in enumerate(results):
            r["sr no"] = i + 1
            
        return results
    except Exception:
        return []
@st.cache_data(ttl=300)
def get_sector_performers(sector_name):
    if sector_name not in SECTOR_CONSTITUENTS:
        return {"best": [], "worst": []}
    
    tickers = SECTOR_CONSTITUENTS[sector_name]
    try:
        df = yf.download(tickers, period="1y", interval="1d", progress=False)
        results = []
        for t in tickers:
            try:
                if isinstance(df.columns, pd.MultiIndex):
                    if t in df.columns.levels[1]:
                        df_t = df.xs(t, axis=1, level=1).dropna()
                    else: continue
                else:
                    df_t = df[[t]].dropna() if t in df.columns else pd.DataFrame()
                    
                if len(df_t) < 5: continue
                
                current = float(df_t['Close'].iloc[-1])
                
                daily = ((current / float(df_t['Close'].iloc[-2])) - 1) * 100 if len(df_t) >= 2 else 0
                weekly = ((current / float(df_t['Close'].iloc[-5])) - 1) * 100 if len(df_t) >= 5 else 0
                monthly = ((current / float(df_t['Close'].iloc[-21])) - 1) * 100 if len(df_t) >= 21 else 0
                quarterly = ((current / float(df_t['Close'].iloc[-63])) - 1) * 100 if len(df_t) >= 63 else 0
                yearly = ((current / float(df_t['Close'].iloc[0])) - 1) * 100
                
                if weekly >= 5:
                    remark = "Stellar breakout momentum driving the sector."
                elif weekly >= 2:
                    remark = "Solid outperformance."
                elif weekly >= 0:
                    remark = "Positive but soft momentum."
                elif weekly >= -3:
                    remark = "Lagging the sector's general rally."
                else:
                    remark = "Heavy underperformance; structural weakness."
                    
                results.append({
                    "stocks from sector": t,
                    "daily %": round(daily, 2),
                    "weekly %": round(weekly, 2),
                    "monthly %": round(monthly, 2),
                    "quarterly %": round(quarterly, 2),
                    "yearly %": round(yearly, 2),
                    "remark for insights": remark
                })
            except Exception:
                pass
        
        best = sorted(results, key=lambda x: x["weekly %"], reverse=True)[:10]
        worst = sorted(results, key=lambda x: x["weekly %"])[:10]
        
        for i, r in enumerate(best):
            r["sr. no."] = i + 1
        for i, r in enumerate(worst):
            r["sr. no."] = i + 1
            
        return {"best": best, "worst": worst}
    except Exception:
        return {"best": [], "worst": []}

@st.cache_data(ttl=300)
def get_range_breakout_stocks():
    all_tickers = list(set([t for constituents in SECTOR_CONSTITUENTS.values() for t in constituents] + NIFTY_50 + get_nifty500_tickers()))
    ticker_to_sector = {t: s for s, tickers in SECTOR_CONSTITUENTS.items() for t in tickers}

    try:
        df = yf.download(all_tickers, period="1y", interval="1d", progress=False)
        results = []

        for t in all_tickers:
            try:
                if isinstance(df.columns, pd.MultiIndex):
                    if t not in df.columns.levels[1]:
                        continue
                    df_t = df.xs(t, axis=1, level=1).dropna()
                else:
                    df_t = df.dropna()

                if len(df_t) < 50:
                    continue

                close = df_t['Close']
                current_price = float(close.iloc[-1])

                # --- Range highs ---
                high_20d = float(df_t['High'].tail(20).max())
                high_50d = float(df_t['High'].tail(50).max())
                high_52w = float(df_t['High'].tail(252).max())

                pct_from_20d = ((current_price / high_20d) - 1) * 100
                pct_from_50d = ((current_price / high_50d) - 1) * 100
                pct_from_52w = ((current_price / high_52w) - 1) * 100

                # --- Volume spike ---
                avg_vol_20d = float(df_t['Volume'].tail(20).mean())
                current_vol = float(df_t['Volume'].iloc[-1])
                vol_ratio = round(current_vol / avg_vol_20d, 2) if avg_vol_20d > 0 else 1.0
                vol_confirmed = vol_ratio >= 1.5
                vol_label = f"{vol_ratio}x ✅" if vol_confirmed else f"{vol_ratio}x ❌"

                # --- MACD bullish crossover ---
                macd_ind = ta.trend.MACD(close, window_slow=26, window_fast=12, window_sign=9)
                macd_line = macd_ind.macd()
                signal_line = macd_ind.macd_signal()
                if len(macd_line.dropna()) >= 2:
                    macd_now = float(macd_line.iloc[-1])
                    macd_prev = float(macd_line.iloc[-2])
                    sig_now = float(signal_line.iloc[-1])
                    sig_prev = float(signal_line.iloc[-2])
                    # Crossover: MACD crossed above signal in last 2 bars, or is above signal
                    macd_crossover = (macd_now > sig_now)
                    fresh_cross = (macd_prev <= sig_prev) and (macd_now > sig_now)
                    if fresh_cross:
                        macd_label = "Fresh Crossover ✅"
                    elif macd_crossover:
                        macd_label = "Bullish ✅"
                    else:
                        macd_label = "Bearish ❌"
                    macd_confirmed = macd_crossover
                else:
                    macd_label = "N/A"
                    macd_confirmed = False

                # --- Moving Average fanning (5 > 10 > 20 DMA, all rising) ---
                ma5  = close.rolling(5).mean()
                ma10 = close.rolling(10).mean()
                ma20 = close.rolling(20).mean()
                if ma20.dropna().shape[0] >= 2:
                    m5_now  = float(ma5.iloc[-1]);  m5_prev  = float(ma5.iloc[-2])
                    m10_now = float(ma10.iloc[-1]); m10_prev = float(ma10.iloc[-2])
                    m20_now = float(ma20.iloc[-1]); m20_prev = float(ma20.iloc[-2])
                    aligned  = m5_now > m10_now > m20_now
                    all_rising = (m5_now > m5_prev) and (m10_now > m10_prev) and (m20_now > m20_prev)
                    ma_confirmed = aligned and all_rising
                    ma_label = "Fanning Up ✅" if ma_confirmed else ("Aligned, Not Rising ⚠️" if aligned else "Flat/Mixed ❌")
                else:
                    ma_label = "N/A"
                    ma_confirmed = False

                # --- Daily RSI ---
                rsi_series = ta.momentum.RSIIndicator(close, window=14).rsi()
                if rsi_series.dropna().shape[0] >= 1:
                    rsi_val = round(float(rsi_series.iloc[-1]), 1)
                    if rsi_val >= 70:
                        rsi_label = f"{rsi_val} (Overbought)"
                    elif rsi_val >= 55:
                        rsi_label = f"{rsi_val} (Bullish) ✅"
                    elif rsi_val >= 45:
                        rsi_label = f"{rsi_val} (Neutral)"
                    else:
                        rsi_label = f"{rsi_val} (Weak) ❌"
                    rsi_confirmed = 55 <= rsi_val < 70
                else:
                    rsi_label = "N/A"
                    rsi_confirmed = False

                # --- Score & filter ---
                score = 0
                signals = []
                if pct_from_20d >= -3:
                    score += 2; signals.append("20D")
                if pct_from_50d >= -3:
                    score += 2; signals.append("50D")
                if pct_from_52w >= -3:
                    score += 4; signals.append("52W")
                if vol_confirmed:
                    score += 3
                if macd_confirmed:
                    score += 2
                if ma_confirmed:
                    score += 2
                if rsi_confirmed:
                    score += 2

                if score == 0 or not signals:
                    continue

                confirmations = sum([vol_confirmed, macd_confirmed, ma_confirmed, rsi_confirmed])
                if confirmations == 4:
                    overall = "Strong Breakout ✅✅✅✅"
                elif confirmations == 3:
                    overall = "Strong Breakout ✅✅✅"
                elif confirmations == 2:
                    overall = "Likely Breakout ✅✅"
                elif confirmations == 1:
                    overall = "Watch Closely ✅"
                else:
                    overall = "Unconfirmed ⚠️"

                results.append({
                    "_score": score,
                    "sr. no.": 0,
                    "stock": t.replace(".NS", ""),
                    "sector": ticker_to_sector.get(t, "LARGE CAP"),
                    "current price": round(current_price, 2),
                    "% to 52W high": round(pct_from_52w, 2),
                    "volume (vs 20D avg)": vol_label,
                    "MACD": macd_label,
                    "MA alignment": ma_label,
                    "RSI (14)": rsi_label,
                    "overall confirmation": overall,
                })
            except Exception:
                pass

        results = sorted(results, key=lambda x: (x["_score"], x["% to 52W high"]), reverse=True)[:10]
        for i, r in enumerate(results):
            r["sr. no."] = i + 1
            del r["_score"]
        return results
    except Exception:
        return []

@st.cache_data(ttl=300)
def get_top_10_overall_stocks():
    all_tickers = list(set([ticker for constituents in SECTOR_CONSTITUENTS.values() for ticker in constituents]))
    try:
        df = yf.download(all_tickers, period="1y", interval="1d", progress=False)
        results = []
        for t in all_tickers:
            try:
                if isinstance(df.columns, pd.MultiIndex):
                    if t in df.columns.levels[1]:
                        df_t = df.xs(t, axis=1, level=1).dropna()
                    else: continue
                else:
                    df_t = df[[t]].dropna() if t in df.columns else pd.DataFrame()
                    
                if len(df_t) < 5: continue
                current = float(df_t['Close'].iloc[-1])
                
                daily = ((current / float(df_t['Close'].iloc[-2])) - 1) * 100 if len(df_t) >= 2 else 0
                weekly = ((current / float(df_t['Close'].iloc[-5])) - 1) * 100 if len(df_t) >= 5 else 0
                monthly = ((current / float(df_t['Close'].iloc[-21])) - 1) * 100 if len(df_t) >= 21 else 0
                quarterly = ((current / float(df_t['Close'].iloc[-63])) - 1) * 100 if len(df_t) >= 63 else 0
                yearly = ((current / float(df_t['Close'].iloc[0])) - 1) * 100
                
                if weekly >= 5: remark = "Stellar breakout momentum driving entire market."
                elif weekly >= 2: remark = "Solid macro outperformance."
                elif weekly >= 0: remark = "Positive but soft momentum."
                elif weekly >= -3: remark = "Lagging the general rally."
                else: remark = "Heavy underperformance; structural weakness."
                    
                results.append({
                    "stock symbol": t,
                    "daily %": round(daily, 2),
                    "weekly %": round(weekly, 2),
                    "monthly %": round(monthly, 2),
                    "quarterly %": round(quarterly, 2),
                    "yearly %": round(yearly, 2),
                    "remark for insights": remark
                })
            except Exception:
                pass
        
        results = sorted(results, key=lambda x: x["weekly %"], reverse=True)[:10]
        for i, r in enumerate(results):
            r["sr. no."] = i + 1
            try:
                info = yf.Ticker(r["stock symbol"]).info
                qoq = info.get("earningsQuarterlyGrowth")
                yoy = info.get("earningsGrowth")
                r["EPS QoQ %"] = f"{round(qoq * 100, 1)}%" if qoq is not None else "N/A"
                r["EPS YoY %"] = f"{round(yoy * 100, 1)}%" if yoy is not None else "N/A"
            except Exception:
                r["EPS QoQ %"] = "N/A"
                r["EPS YoY %"] = "N/A"
        return results
    except Exception:
        return []

@st.cache_data(ttl=300)
def get_nifty_sensex_levels():
    import time as _time
    res = {"NIFTY 50": "N/A", "SENSEX": "N/A", "INDIA VIX": "N/A", "NIFTY RSI": "N/A", "NIFTY % to ATH": "N/A"}

    for ticker, key in [("^NSEI", "NIFTY 50"), ("^BSESN", "SENSEX"), ("^INDIAVIX", "INDIA VIX")]:
        for attempt in range(3):
            try:
                df_t = yf.Ticker(ticker).history(period="2y")
                if df_t.empty:
                    _time.sleep(2)
                    continue
                df_t = df_t.dropna(subset=["Close"])
                current = float(df_t["Close"].iloc[-1])
                res[key] = f"{current:,.2f}"
                if key == "NIFTY 50":
                    rsi_s = ta.momentum.RSIIndicator(df_t["Close"], window=14).rsi().dropna()
                    if not rsi_s.empty:
                        res["NIFTY RSI"] = f"{rsi_s.iloc[-1]:.1f}"
                    ath = float(df_t["High"].max())
                    res["NIFTY % to ATH"] = f"{((current / ath) - 1) * 100:.2f}%"
                break
            except Exception:
                _time.sleep(2)
        _time.sleep(0.5)

    if res["NIFTY 50"] == "N/A":
        get_nifty_sensex_levels.clear()
    return res


@st.cache_data(ttl=3600)
def get_nifty50_pe():
    """
    Fetch Nifty 50 trailing P/E ratio.
    Method 1: NSE allIndices API (authoritative, Indian IP preferred).
    Method 2: Calculated market-cap weighted P/E from Nifty 50 constituents via yfinance.
    """
    import requests
    from concurrent.futures import ThreadPoolExecutor, as_completed

    # ── Method 1: NSE allIndices API ─────────────────────────────────────────
    try:
        session = requests.Session()
        session.get("https://www.nseindia.com", timeout=8, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        })
        resp = session.get(
            "https://www.nseindia.com/api/allIndices",
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
                "Referer": "https://www.nseindia.com/",
                "Accept": "application/json",
            }
        )
        if resp.status_code == 200:
            for item in resp.json().get("data", []):
                if item.get("index") == "NIFTY 50":
                    pe = item.get("pe")
                    if pe:
                        return round(float(pe), 2)
    except Exception:
        pass

    # ── Method 2: Market-cap weighted P/E from constituents ──────────────────
    try:
        def _fetch(ticker):
            try:
                info = yf.Ticker(ticker).info
                mc = info.get("marketCap") or 0
                pe = info.get("trailingPE") or 0
                if mc > 0 and pe > 0:
                    return mc, mc / pe   # (market_cap, earnings)
            except Exception:
                pass
            return None

        total_mc = 0.0
        total_earn = 0.0
        with ThreadPoolExecutor(max_workers=10) as ex:
            futures = {ex.submit(_fetch, t): t for t in NIFTY_50}
            for f in as_completed(futures):
                res = f.result()
                if res:
                    total_mc += res[0]
                    total_earn += res[1]

        if total_earn > 0:
            return round(total_mc / total_earn, 2)
    except Exception:
        pass

    return None

@st.cache_data(ttl=3600)
def get_fiidii():
    # First try nsepython (works locally with Indian IP)
    try:
        from nsepython import nse_fiidii
        df = nse_fiidii()
        dii_net = float(df[df["category"] == "DII"]["netValue"].iloc[0])
        fii_net = float(df[df["category"] == "FII/FPI"]["netValue"].iloc[0])
        return {"FII": fii_net, "DII": dii_net}
    except Exception:
        pass

    # Fallback: direct NSE API call with browser headers (for cloud deployments)
    try:
        import requests
        session = requests.Session()
        session.get("https://www.nseindia.com", timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        })
        resp = session.get(
            "https://www.nseindia.com/api/fiidiiTradeReact",
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
                "Referer": "https://www.nseindia.com/",
                "Accept": "application/json",
            }
        )
        data = resp.json()
        fii_net, dii_net = None, None
        for item in data:
            cat = item.get("category", "")
            if "FII" in cat or "FPI" in cat:
                fii_net = float(item.get("netValue", 0))
            elif cat == "DII":
                dii_net = float(item.get("netValue", 0))
        if fii_net is not None and dii_net is not None:
            return {"FII": fii_net, "DII": dii_net}
    except Exception:
        pass

    return {"FII": None, "DII": None}

def _fii_json_mtime():
    import os
    p = os.path.join(os.path.dirname(__file__), "fii_stake_data.json")
    return os.path.getmtime(p) if os.path.exists(p) else 0

@st.cache_data(ttl=86400)  # quarterly data — refresh once a day
def get_fii_stake_increases(_mtime=None):
    """
    Returns top 10 NIFTY 50 stocks where FII/FPI increased stake last quarter.
    Primary source: fii_stake_data.json committed daily by GitHub Actions.
    Fallback: live NSE API call (works on Indian IPs only).
    """
    import json, os, requests

    # --- Primary: read from pre-fetched JSON (committed by GitHub Actions) ---
    json_path = os.path.join(os.path.dirname(__file__), "fii_stake_data.json")
    if os.path.exists(json_path):
        try:
            with open(json_path) as f:
                stored = json.load(f)
            data = stored.get("data", [])
            if data:
                return data
        except Exception:
            pass

    # --- Fallback: live NSE call (Indian IP only) ---
    results = []
    session = requests.Session()
    try:
        session.get("https://www.nseindia.com", timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        })
    except Exception:
        pass

    api_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        "Referer": "https://www.nseindia.com/",
        "Accept": "application/json",
    }

    for symbol in [t.replace(".NS", "") for t in NIFTY_50]:
        try:
            resp = session.get(
                f"https://www.nseindia.com/api/corporate-shareholding-patterns?index=equities&symbol={symbol}",
                timeout=10, headers=api_headers
            )
            records = resp.json()
            if isinstance(records, dict):
                records = records.get("data", [])
            if len(records) < 2:
                continue

            def extract_fii(rec):
                for key in ["fiiFpiHolding", "totalForeignPortfolioInvestors", "fii", "FII", "fiiHolding"]:
                    if key in rec:
                        try:
                            return float(str(rec[key]).replace("%", "").strip())
                        except Exception:
                            pass
                return None

            latest_fii = extract_fii(records[0])
            prev_fii   = extract_fii(records[1])
            if latest_fii is None or prev_fii is None:
                continue
            change = round(latest_fii - prev_fii, 2)
            if change > 0:
                results.append({
                    "sr. no.": 0,
                    "company": symbol,
                    "current FII %": round(latest_fii, 2),
                    "prev quarter %": round(prev_fii, 2),
                    "change (pp)": change,
                })
        except Exception:
            pass

    results = sorted(results, key=lambda x: float(str(x["change (pp)"]).replace("+", "")), reverse=True)[:10]
    for i, r in enumerate(results):
        r["sr. no."] = i + 1
    return results

COMMODITIES = {
    "CL=F":  {"name": "WTI Crude Oil",  "unit": "USD/bbl"},
    "BZ=F":  {"name": "Brent Crude",    "unit": "USD/bbl"},
    "NG=F":  {"name": "Natural Gas",    "unit": "USD/MMBtu"},
    "GC=F":  {"name": "Gold",           "unit": "USD/troy oz"},
    "SI=F":  {"name": "Silver",         "unit": "USD/troy oz"},
}

@st.cache_data(ttl=300)
def get_commodity_data():
    import time as _time
    # Live USD/INR for Gold & Silver INR conversion
    usdinr = None
    try:
        _fx = yf.Ticker("USDINR=X").history(period="5d")
        if not _fx.empty:
            usdinr = float(_fx["Close"].dropna().iloc[-1])
    except Exception:
        pass

    results = []
    for t, meta in COMMODITIES.items():
        try:
            df_t = yf.Ticker(t).history(period="5y")
            if df_t.empty or len(df_t) < 2:
                continue
            df_t = df_t.dropna(subset=["Close"])
            current = float(df_t["Close"].iloc[-1])
            prev    = float(df_t["Close"].iloc[-2])
            ath     = float(df_t["High"].max())
            name    = meta["name"]

            inr_price = None
            if usdinr:
                if name == "Gold":
                    inr_price = f"₹{round(current * usdinr / 31.1035 * 10):,} /10g"
                elif name == "Silver":
                    inr_price = f"₹{round(current * usdinr / 31.1035 * 1000):,} /kg"

            results.append({
                "commodity":     name,
                "unit":          meta["unit"],
                "current price": round(current, 2),
                "INR price (Latur)": inr_price if inr_price else "—",
                "day change %":  round((current / prev - 1) * 100, 2),
                "% from 5Y high": round((current / ath - 1) * 100, 2),
            })
            _time.sleep(0.3)
        except Exception:
            pass
    return results

MF_SCHEMES = {
    # Large Cap - Direct Growth
    120503: ("Axis Bluechip Fund",                  "Large Cap"),
    119598: ("HDFC Top 100 Fund",                   "Large Cap"),
    120586: ("ICICI Pru Bluechip Fund",             "Large Cap"),
    119286: ("SBI Bluechip Fund",                   "Large Cap"),
    118989: ("Mirae Asset Large Cap Fund",          "Large Cap"),
    122639: ("Nippon India Large Cap Fund",         "Large Cap"),
    # Flexi Cap - Direct Growth
    125354: ("Parag Parikh Flexi Cap Fund",         "Flexi Cap"),
    100170: ("HDFC Flexi Cap Fund",                 "Flexi Cap"),
    120505: ("Axis Focused 25 Fund",                "Flexi Cap"),
    118778: ("Motilal Oswal Flexi Cap Fund",        "Flexi Cap"),
    # Mid Cap - Direct Growth
    119551: ("HDFC Mid-Cap Opportunities",          "Mid Cap"),
    120594: ("ICICI Pru Midcap Fund",               "Mid Cap"),
    120829: ("Axis Midcap Fund",                    "Mid Cap"),
    120847: ("Kotak Emerging Equity Fund",          "Mid Cap"),
    # Small Cap - Direct Growth
    120828: ("Axis Small Cap Fund",                 "Small Cap"),
    125497: ("Nippon India Small Cap Fund",         "Small Cap"),
    119605: ("HDFC Small Cap Fund",                 "Small Cap"),
    125959: ("Quant Small Cap Fund",                "Small Cap"),
    # Index - Direct Growth
    120716: ("UTI Nifty 50 Index Fund",             "Index"),
    148627: ("Motilal Oswal Nifty 50 Index Fund",   "Index"),
    # Hybrid - Direct Growth
    125170: ("HDFC Balanced Advantage Fund",        "Hybrid"),
    119775: ("ICICI Pru Balanced Advantage Fund",   "Hybrid"),
}

@st.cache_data(ttl=3600)
def get_top_mutual_funds():
    import requests
    from concurrent.futures import ThreadPoolExecutor, as_completed

    def fetch_fund(scheme_code, name, category):
        try:
            resp = requests.get(
                f"https://api.mfapi.in/mf/{scheme_code}",
                timeout=15
            )
            if resp.status_code != 200:
                return None
            data = resp.json().get("data", [])
            if len(data) < 22:
                return None

            def nav(i):
                return float(data[i]["nav"])

            current = nav(0)
            daily   = round((current / nav(1)   - 1) * 100, 2) if len(data) > 1   else None
            weekly  = round((current / nav(5)   - 1) * 100, 2) if len(data) > 5   else None
            monthly = round((current / nav(21)  - 1) * 100, 2) if len(data) > 21  else None
            yearly  = round((current / nav(252) - 1) * 100, 2) if len(data) > 252 else None

            return {
                "fund name":    name,
                "category":     category,
                "NAV (₹)":      round(current, 2),
                "daily %":      daily,
                "weekly %":     weekly,
                "monthly %":    monthly,
                "yearly %":     yearly,
            }
        except Exception:
            return None

    results = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {
            executor.submit(fetch_fund, code, name, cat): code
            for code, (name, cat) in MF_SCHEMES.items()
        }
        for future in as_completed(futures):
            res = future.result()
            if res:
                results.append(res)

    results.sort(key=lambda x: x.get("weekly %") or 0, reverse=True)
    for i, r in enumerate(results):
        r["sr. no."] = i + 1
    return results

# ── Extended commodity list for the dedicated tab ─────────────────────────────
FULL_COMMODITIES = {
    "CL=F":  {"name": "WTI Crude Oil",   "unit": "USD/bbl"},
    "BZ=F":  {"name": "Brent Crude",     "unit": "USD/bbl"},
    "NG=F":  {"name": "Natural Gas",     "unit": "USD/MMBtu"},
    "GC=F":  {"name": "Gold",            "unit": "USD/troy oz"},
    "SI=F":  {"name": "Silver",          "unit": "USD/troy oz"},
    "HG=F":  {"name": "Copper",          "unit": "USD/lb"},
    "ZW=F":  {"name": "Wheat",           "unit": "USD/bushel"},
    "ZC=F":  {"name": "Corn",            "unit": "USD/bushel"},
    "PA=F":  {"name": "Palladium",       "unit": "USD/troy oz"},
    "ALI=F": {"name": "Aluminium",       "unit": "USD/lb"},
}

CURRENCY_PAIRS = {
    "USDINR=X": "USD / INR",
    "EURINR=X": "EUR / INR",
    "GBPINR=X": "GBP / INR",
    "JPYINR=X": "JPY / INR",
    "CNYINR=X": "CNY / INR",
    "DX-Y.NYB": "US Dollar Index (DXY)",
}

@st.cache_data(ttl=300)
def get_extended_commodity_data():
    import time as _time

    # Fetch live USD/INR rate for Gold & Silver INR conversion
    usdinr = None
    try:
        _fx = yf.Ticker("USDINR=X").history(period="5d")
        if not _fx.empty:
            usdinr = float(_fx["Close"].dropna().iloc[-1])
    except Exception:
        pass

    results = []
    for t, meta in FULL_COMMODITIES.items():
        try:
            df_t = yf.Ticker(t).history(period="5y")
            if df_t.empty or len(df_t) < 2:
                continue
            df_t = df_t.dropna(subset=["Close"])
            if len(df_t) < 2:
                continue
            c   = float(df_t["Close"].iloc[-1])
            ath = float(df_t["High"].max())

            def _p(n, _c=c, _df=df_t):
                return round((_c / float(_df["Close"].iloc[-(n + 1)]) - 1) * 100, 2) if len(_df) > n else None

            pct_ath = round((c / ath - 1) * 100, 2)
            wk      = _p(5) or 0
            name    = meta["name"]

            if "Crude" in name or "Oil" in name:
                if wk > 3:    insight = "Rising crude pressures India's CAD and fuel inflation — watch for RBI response."
                elif wk > 0:  insight = "Steady crude; manageable import bill for India in near term."
                elif wk > -3: insight = "Softening crude benefits India's trade deficit and eases inflation."
                else:         insight = "Sharp crude fall signals global demand weakness; positive for India inflation."
            elif "Gas" in name:
                if wk > 5:    insight = "Surging gas costs raise input costs for fertiliser and power sectors."
                elif wk > 0:  insight = "Gas prices firm; watch GAIL, IGL, Petronet margins."
                else:         insight = "Cooling gas prices ease energy costs for industry."
            elif "Gold" in name:
                if pct_ath >= -3: insight = "Gold near 5Y high — strong safe-haven bid; signals macro uncertainty."
                elif wk > 1:      insight = "Gold rising; defensive positioning increasing globally."
                elif wk < -2:     insight = "Gold retreating; risk appetite returning to equities."
                else:             insight = "Gold consolidating; watch DXY direction for next move."
            elif "Silver" in name:
                if wk > 3:    insight = "Silver outpacing gold (ratio compressing) — industrial demand strong."
                elif wk < -3: insight = "Silver underperforming; industrial demand concerns or gold weakness."
                else:         insight = "Silver tracking gold with higher volatility; watch industrial PMI data."
            elif "Copper" in name:
                if wk > 2:    insight = "Copper surge signals strong global industrial/construction activity."
                elif wk < -2: insight = "Copper weakness flags slowing global growth; monitor China PMI."
                else:         insight = "Copper range-bound; mixed signals on global manufacturing cycle."
            elif "Wheat" in name or "Corn" in name:
                if wk > 3:    insight = "Agri commodity spike raises food inflation risks; watch CPI prints."
                elif wk < -3: insight = "Agri prices easing; food inflation relief ahead."
                else:         insight = "Agri prices stable; benign food inflation environment."
            elif "Palladium" in name:
                if wk > 3:    insight = "Palladium rising; EV transition may be slower than expected (petrol catalysts)."
                elif wk < -3: insight = "Palladium weak; EV adoption accelerating, reducing autocatalyst demand."
                else:         insight = "Palladium range-bound; watch auto sector and EV penetration data."
            elif "Aluminium" in name:
                if wk > 2:    insight = "Aluminium rising; strong demand from EVs, infra, and packaging sectors."
                elif wk < -2: insight = "Aluminium under pressure; watch China industrial output and LME inventory."
                else:         insight = "Aluminium stable; balanced supply-demand globally."
            else:
                if pct_ath >= -5: insight = "Near 5Y high; exceptional momentum."
                elif wk > 0:      insight = "Positive trend; monitor for continuation."
                else:             insight = "Under pressure; watch key support levels."

            # INR price for Gold (₹/10g) and Silver (₹/kg) — Latur/MCX reference rate
            # 1 troy oz = 31.1035 g
            inr_price = None
            inr_unit  = None
            if usdinr:
                if name == "Gold":
                    inr_price = f"₹{round(c * usdinr / 31.1035 * 10):,} /10g"
                    inr_unit  = "₹/10g"
                elif name == "Silver":
                    inr_price = f"₹{round(c * usdinr / 31.1035 * 1000):,} /kg"
                    inr_unit  = "₹/kg"

            results.append({
                "commodity":  name,
                "unit":       meta["unit"],
                "price":      round(c, 2),
                "INR price (Latur)": inr_price if inr_price else "—",
                "day %":      _p(1),
                "week %":     _p(5),
                "month %":    _p(21),
                "quarter %":  _p(63),
                "yearly %":   _p(252),
                "% from 5Y high": pct_ath,
                "insight":    insight,
            })
            _time.sleep(0.3)
        except Exception:
            pass
    return results

@st.cache_data(ttl=300)
def get_currency_data():
    import time as _time
    results = []
    for t, pair in CURRENCY_PAIRS.items():
        try:
            df_t = yf.Ticker(t).history(period="5y")
            if df_t.empty or len(df_t) < 2:
                continue
            df_t = df_t.dropna(subset=["Close"])
            if len(df_t) < 2:
                continue
            c   = float(df_t["Close"].iloc[-1])
            ath = float(df_t["High"].max())

            def _p(n, _c=c, _df=df_t):
                return round((_c / float(_df["Close"].iloc[-(n + 1)]) - 1) * 100, 2) if len(_df) > n else None

            pct_ath = round((c / ath - 1) * 100, 2)
            wk      = _p(5) or 0

            if "USD / INR" in pair:
                if wk > 0.5:    insight = "Rupee depreciating vs USD — FII equity outflows likely; import costs rise."
                elif wk < -0.5: insight = "Rupee strengthening vs USD — positive for FII inflows and lower import inflation."
                else:           insight = "USD/INR stable; RBI likely managing range via interventions."
            elif "EUR / INR" in pair:
                if wk > 0.5:    insight = "EUR/INR rising; Euro-zone resilience or rupee weakness driving move."
                elif wk < -0.5: insight = "EUR/INR falling; watch ECB policy divergence vs RBI."
                else:           insight = "EUR/INR range-bound; eurozone and India macro in equilibrium."
            elif "GBP / INR" in pair:
                if wk > 0.5:    insight = "GBP gaining on INR; UK data beating or BoE hawkishness."
                elif wk < -0.5: insight = "GBP softening vs INR; UK growth concerns or dovish BoE signals."
                else:           insight = "GBP/INR stable; limited directional catalyst in near term."
            elif "JPY / INR" in pair:
                if wk > 0.5:    insight = "Yen strengthening; risk-off globally or BoJ hike — watch carry trade unwind."
                elif wk < -0.5: insight = "Yen weakening; carry trade intact; Japan keeping rates low."
                else:           insight = "JPY/INR flat; BoJ-RBI policy divergence on hold."
            elif "CNY / INR" in pair:
                if wk > 0.3:    insight = "Yuan gaining on INR; China stimulus or trade surplus driving strength."
                elif wk < -0.3: insight = "Yuan softening; China growth concerns or PBoC easing."
                else:           insight = "CNY/INR stable; China-India trade dynamics balanced."
            elif "DXY" in pair:
                if wk > 0.5:    insight = "Strong DXY pressures EM currencies and commodities — headwind for Indian equities."
                elif wk < -0.5: insight = "Weakening DXY boosts EM/commodities; supportive for Indian market inflows."
                else:           insight = "DXY neutral; global macro in wait-and-watch mode."
            else:
                insight = "Monitor trend for directional cues."

            results.append({
                "pair":           pair,
                "rate":           round(c, 4),
                "day %":          _p(1),
                "week %":         _p(5),
                "month %":        _p(21),
                "yearly %":       _p(252),
                "% from 5Y high": pct_ath,
                "insight":        insight,
            })
            _time.sleep(0.3)
        except Exception:
            pass
    return results

@st.cache_data(ttl=1800)
def get_market_breadth():
    tickers = get_nifty500_tickers()
    res = {
        "total": 0, "advances": 0, "declines": 0, "unchanged": 0,
        "above_200dma": 0, "above_50dma": 0,
        "new_52w_highs": 0, "new_52w_lows": 0,
        "high_stocks": [], "low_stocks": [],
    }
    try:
        df = yf.download(tickers, period="1y", interval="1d", progress=False)
        for t in tickers:
            try:
                if isinstance(df.columns, pd.MultiIndex):
                    if t not in df.columns.get_level_values(1):
                        continue
                    df_t = df.xs(t, axis=1, level=1).dropna()
                else:
                    df_t = df.dropna()
                if len(df_t) < 52:
                    continue

                close   = df_t["Close"]
                current = float(close.iloc[-1])
                prev    = float(close.iloc[-2])
                res["total"] += 1

                if current > prev:      res["advances"]  += 1
                elif current < prev:    res["declines"]  += 1
                else:                   res["unchanged"] += 1

                if len(df_t) >= 200 and current > float(close.iloc[-200:].mean()):
                    res["above_200dma"] += 1
                if len(df_t) >= 50 and current > float(close.iloc[-50:].mean()):
                    res["above_50dma"] += 1

                n = min(len(df_t), 252)
                high52 = float(df_t["High"].iloc[-n:].max())
                low52  = float(df_t["Low"].iloc[-n:].min())

                if high52 > 0 and (current / high52 - 1) * 100 >= -1.5:
                    res["new_52w_highs"] += 1
                    res["high_stocks"].append(t.replace(".NS", ""))
                if low52 > 0 and (current / low52 - 1) * 100 <= 1.5:
                    res["new_52w_lows"] += 1
                    res["low_stocks"].append(t.replace(".NS", ""))
            except Exception:
                pass
    except Exception:
        pass
    return res

@st.cache_data(ttl=300)
def get_options_snapshot(symbol="NIFTY"):
    import requests
    session = requests.Session()
    hdrs = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    try:
        session.get("https://www.nseindia.com", timeout=10, headers=hdrs)
        session.get("https://www.nseindia.com/option-chain", timeout=10, headers=hdrs)
    except Exception as e:
        return {"error": f"Cannot reach NSE — this feature requires an Indian IP address. ({type(e).__name__})"}
    try:
        resp = session.get(
            f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}",
            timeout=15,
            headers={**hdrs, "Referer": "https://www.nseindia.com/option-chain", "Accept": "application/json"},
        )
        if resp.status_code != 200:
            return {"error": f"NSE returned HTTP {resp.status_code} — this feature requires an Indian IP address."}
        data = resp.json()
    except Exception as e:
        return {"error": f"Option chain fetch failed — this feature requires an Indian IP address. ({type(e).__name__})"}
    try:
        records       = data["records"]["data"]
        expiry_dates  = data["records"]["expiryDates"]
        spot          = float(data["records"]["underlyingValue"])
        nearest_exp   = expiry_dates[0]
        chain         = [r for r in records if r.get("expiryDate") == nearest_exp]

        total_call_oi = sum(r.get("CE", {}).get("openInterest", 0) for r in records if "CE" in r)
        total_put_oi  = sum(r.get("PE", {}).get("openInterest", 0) for r in records if "PE" in r)
        pcr           = round(total_put_oi / total_call_oi, 2) if total_call_oi > 0 else None

        rows = []
        for r in chain:
            strike = r.get("strikePrice", 0)
            rows.append({
                "call OI":   int(r.get("CE", {}).get("openInterest", 0)),
                "call Δ OI": int(r.get("CE", {}).get("changeinOpenInterest", 0)),
                "call LTP":  r.get("CE", {}).get("lastPrice", "-"),
                "strike":    int(strike),
                "put LTP":   r.get("PE", {}).get("lastPrice", "-"),
                "put OI":    int(r.get("PE", {}).get("openInterest", 0)),
                "put Δ OI":  int(r.get("PE", {}).get("changeinOpenInterest", 0)),
            })
        rows.sort(key=lambda x: x["strike"])

        # Max pain
        strikes    = [r["strike"] for r in rows]
        call_oi_m  = {r["strike"]: r["call OI"] for r in rows}
        put_oi_m   = {r["strike"]: r["put OI"]  for r in rows}
        min_pain, max_pain = None, None
        for cand in strikes:
            pain = sum(
                max(0, s - cand) * call_oi_m.get(s, 0) +
                max(0, cand - s) * put_oi_m.get(s, 0)
                for s in strikes
            )
            if min_pain is None or pain < min_pain:
                min_pain, max_pain = pain, cand

        atm_rows = [r for r in rows if spot > 0 and abs(r["strike"] - spot) / spot <= 0.10]
        return {
            "error": None, "symbol": symbol, "spot": spot, "expiry": nearest_exp,
            "pcr": pcr, "max_pain": max_pain,
            "total_call_oi": total_call_oi, "total_put_oi": total_put_oi,
            "atm_rows": atm_rows,
        }
    except Exception as e:
        return {"error": f"Error parsing NSE data: {e}"}

@st.cache_data(ttl=3600)
def get_earnings_calendar():
    import requests
    from datetime import datetime, timezone

    # Method 1: NSE Event Calendar (Indian IP required)
    try:
        session = requests.Session()
        hdrs = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Referer": "https://www.nseindia.com/",
        }
        session.get("https://www.nseindia.com", timeout=10, headers={**hdrs, "Accept": "text/html"})
        resp = session.get("https://www.nseindia.com/api/event-calendar", timeout=15, headers=hdrs)
        if resp.status_code == 200:
            today = datetime.now(timezone.utc).date()
            results = []
            for e in resp.json():
                purpose = e.get("purpose", "")
                if any(k in purpose.lower() for k in ("result", "quarterly", "financial", "dividend")):
                    try:
                        ev_date = datetime.strptime(e.get("date", ""), "%d-%b-%Y").date()
                        if ev_date >= today:
                            results.append({
                                "company": e.get("symbol", ""),
                                "date":    e.get("date", ""),
                                "event":   purpose,
                            })
                    except Exception:
                        pass
            results.sort(key=lambda x: x["date"])
            if results:
                return {"data": results[:60], "source": "NSE Event Calendar", "error": None}
    except Exception:
        pass

    # Method 2: Yahoo Finance fallback (any IP)
    results = []
    for t in NIFTY_50:
        try:
            cal = yf.Ticker(t).calendar
            if cal is None:
                continue
            dates = cal.get("Earnings Date", []) if isinstance(cal, dict) else []
            if not isinstance(dates, list):
                dates = [dates]
            for d in dates:
                if d:
                    results.append({
                        "company": t.replace(".NS", ""),
                        "date":    str(d)[:10],
                        "event":   "Quarterly Results (est.)",
                    })
        except Exception:
            pass
    results.sort(key=lambda x: x.get("date", ""))
    if results:
        return {"data": results[:60], "source": "Yahoo Finance (estimates)", "error": None}

    return {"data": [], "source": None,
            "error": "Earnings data unavailable. NSE Event Calendar requires an Indian IP address."}

def _section(title, icon="", subtitle=""):
    """Render a styled section header with left accent bar."""
    sub_html = f'<div style="font-size:12px;color:#64748b;margin-top:3px;">{subtitle}</div>' if subtitle else ""
    st.markdown(f"""
    <div style="background:linear-gradient(90deg,rgba(59,130,246,.12) 0%,transparent 100%);
                border-left:3px solid #3b82f6;border-radius:0 8px 8px 0;
                padding:10px 16px;margin:18px 0 8px 0;">
        <div style="font-size:15px;font-weight:700;color:#e2e8f0;">{icon}&nbsp;{title}</div>
        {sub_html}
    </div>""", unsafe_allow_html=True)


def _color_pct(df):
    """Return a Styler with green/red text on numeric %-like and signal columns."""
    pct_cols = [c for c in df.columns if any(
        k in str(c).lower() for k in ['%', 'alpha', 'change', 'return'])]

    def _c(v):
        try:
            num = float(str(v).replace('%','').replace('₹','').replace(',','').replace('+','').strip())
            if num > 0:  return 'color:#00e676;font-weight:600'
            if num < 0:  return 'color:#ff5252;font-weight:600'
        except Exception: pass
        return ''

    def _candle_c(v):
        v = str(v)
        if 'Green' in v or '▲' in v: return 'color:#00e676;font-weight:700'
        if 'Red' in v or '▼' in v:   return 'color:#ff5252;font-weight:700'
        return ''

    def _signal_c(v):
        v = str(v)
        if any(k in v for k in ('✅✅✅✅', 'Strong', 'Fanning Up', 'Fresh Cross', 'Bullish ✅', 'Inflow')):
            return 'color:#00e676;font-weight:600'
        if any(k in v for k in ('❌', 'Bearish', 'Flat/Mixed', 'Weak', 'Unconfirmed', 'Outflow')):
            return 'color:#ff5252'
        if any(k in v for k in ('⚠️', 'Watch', 'Likely', 'Neutral', 'Overbought', 'Aligned, Not')):
            return 'color:#fbbf24'
        return ''

    try:
        s = df.style
        # Format all float columns to 2 decimal places
        float_cols = df.select_dtypes(include=['float64', 'float32', 'float16']).columns.tolist()
        if float_cols:
            s = s.format({col: "{:.2f}" for col in float_cols}, na_rep="-")
        for col in pct_cols:
            if col in df.columns:
                s = s.map(_c, subset=[col])
        if 'candle' in df.columns:
            s = s.map(_candle_c, subset=['candle'])
        for col in ('MACD', 'MA alignment', 'overall confirmation', 'RSI (14)', 'volume (vs 20D avg)'):
            if col in df.columns:
                s = s.map(_signal_c, subset=[col])
        return s
    except Exception:
        return df.style


def run_dashboard():
    # ── Global CSS ──────────────────────────────────────────────────────────
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"], .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    .stApp {
        background: linear-gradient(145deg,#060b18 0%,#0c1628 55%,#080f1e 100%) !important;
    }
    .block-container { padding-top: 1.2rem !important; max-width: 100% !important; }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: rgba(255,255,255,.04);
        border-radius: 14px;
        padding: 5px;
        border: 1px solid rgba(255,255,255,.07);
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border-radius: 9px;
        color: #64748b !important;
        font-size: 13px;
        font-weight: 500;
        padding: 7px 15px;
        border: none !important;
        white-space: nowrap;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg,#1d4ed8,#3b82f6) !important;
        color: #fff !important;
        box-shadow: 0 4px 18px rgba(59,130,246,.45) !important;
        font-weight: 700 !important;
    }
    .stTabs [data-baseweb="tab-highlight"] { display: none !important; }
    .stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {
        background: rgba(59,130,246,.12) !important;
        color: #93c5fd !important;
    }
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 18px !important;
    }

    /* ── Buttons ── */
    .stButton > button {
        background: linear-gradient(135deg,#1d4ed8,#3b82f6) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        padding: 9px 22px !important;
        box-shadow: 0 4px 18px rgba(59,130,246,.35) !important;
        transition: all .2s !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg,#2563eb,#60a5fa) !important;
        box-shadow: 0 6px 24px rgba(59,130,246,.55) !important;
        transform: translateY(-2px) !important;
    }

    /* ── Metrics ── */
    [data-testid="metric-container"] {
        background: rgba(255,255,255,.04);
        border: 1px solid rgba(255,255,255,.08);
        border-radius: 14px;
        padding: 14px 18px;
    }
    [data-testid="stMetricValue"] { font-size:1.55rem !important; font-weight:800 !important; color:#e2e8f0 !important; }
    [data-testid="stMetricLabel"] { font-size:.75rem !important; color:#64748b !important; font-weight:600 !important; letter-spacing:.6px; text-transform:uppercase; }
    [data-testid="stMetricDelta"] { font-size:.82rem !important; font-weight:600 !important; }

    /* ── Dataframes ── */
    .stDataFrame { border-radius: 12px !important; overflow: hidden; border: 1px solid rgba(255,255,255,.07) !important; }
    .stDataFrame table { background: rgba(10,14,26,.9) !important; color: #cbd5e1 !important; }
    .stDataFrame th {
        background: rgba(30,64,175,.35) !important;
        color: #93c5fd !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        letter-spacing: .5px !important;
        text-transform: uppercase;
        border-bottom: 1px solid rgba(59,130,246,.3) !important;
        padding: 10px 14px !important;
    }
    .stDataFrame td { font-size: 13px !important; padding: 8px 14px !important; border-bottom: 1px solid rgba(255,255,255,.04) !important; }
    .stDataFrame tr:hover td { background: rgba(59,130,246,.06) !important; }

    /* ── Alerts ── */
    .stInfo > div { background:rgba(59,130,246,.1) !important; border:1px solid rgba(59,130,246,.25) !important; border-radius:10px !important; color:#93c5fd !important; }
    .stWarning > div { background:rgba(245,158,11,.1) !important; border:1px solid rgba(245,158,11,.25) !important; border-radius:10px !important; }
    .stError > div { background:rgba(239,68,68,.1) !important; border:1px solid rgba(239,68,68,.25) !important; border-radius:10px !important; }
    .stSuccess > div { background:rgba(0,230,118,.1) !important; border:1px solid rgba(0,230,118,.25) !important; border-radius:10px !important; }

    /* ── Text ── */
    h1,h2,h3,h4 { color:#e2e8f0 !important; font-weight:700 !important; }
    p, li { color:#cbd5e1 !important; }
    .stCaption { color:#475569 !important; font-size:12px !important; }
    a { color:#60a5fa !important; }
    a:hover { color:#93c5fd !important; }

    /* ── Divider ── */
    hr { border:none !important; border-top:1px solid rgba(255,255,255,.06) !important; margin:20px 0 !important; }

    /* ── Spinner ── */
    .stSpinner > div { border-color:#3b82f6 transparent transparent transparent !important; }

    /* ── Radio ── */
    .stRadio > label { color:#94a3b8 !important; }
    .stRadio [data-baseweb="radio"] { gap: 16px; }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar { width:5px; height:5px; }
    ::-webkit-scrollbar-track { background:rgba(255,255,255,.02); }
    ::-webkit-scrollbar-thumb { background:rgba(59,130,246,.4); border-radius:3px; }
    ::-webkit-scrollbar-thumb:hover { background:rgba(59,130,246,.7); }

    /* ── News links ── */
    .news-item {
        background:rgba(255,255,255,.03);
        border:1px solid rgba(255,255,255,.07);
        border-radius:10px;
        padding:10px 14px;
        margin:6px 0;
        transition:background .2s;
    }
    .news-item:hover { background:rgba(59,130,246,.08); border-color:rgba(59,130,246,.25); }
    </style>
    """, unsafe_allow_html=True)

    # ── Branded header ───────────────────────────────────────────────────────
    import datetime as _dt
    _now = _dt.datetime.now().strftime("%d %b %Y, %I:%M %p")
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,rgba(29,78,216,.55) 0%,rgba(59,130,246,.25) 50%,rgba(124,58,237,.25) 100%);
                border:1px solid rgba(59,130,246,.3);border-radius:18px;padding:20px 28px;
                margin-bottom:18px;backdrop-filter:blur(12px);
                display:flex;align-items:center;justify-content:space-between;">
        <div>
            <div style="font-size:24px;font-weight:800;color:#fff;letter-spacing:-.5px;">
                📈 &nbsp;Advanced Investor Dashboard
            </div>
            <div style="font-size:13px;color:#93c5fd;margin-top:5px;font-weight:400;">
                Real-time Indian &amp; Global Market Intelligence &nbsp;·&nbsp; NSE &nbsp;·&nbsp; BSE &nbsp;·&nbsp; MCX &nbsp;·&nbsp; {_now}
            </div>
        </div>
        <div style="display:flex;gap:10px;align-items:center;">
            <div style="background:rgba(0,230,118,.12);border:1px solid rgba(0,230,118,.35);border-radius:20px;
                        padding:5px 14px;font-size:12px;color:#00e676;font-weight:700;letter-spacing:.6px;">
                ● &nbsp;LIVE
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_a, col_b = st.columns([9, 1])
    with col_b:
        if st.button("🔄 Refresh"):
            st.cache_data.clear()
            st.rerun()

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
        "🏭  Sectors",
        "📊  Scanners",
        "💎  Fundamentals",
        "📰  News & Macro",
        "🌐  Global Markets",
        "📡  Market Breadth",
        "🛢  Commodities",
        "⚡  Options",
        "📅  Earnings",
    ])

    # --- TAB 1: Sector Performance ---
    with tab1:
        
        levels = get_nifty_sensex_levels()
        nifty_lvl = levels.get("NIFTY 50", "N/A")
        sensex_lvl = levels.get("SENSEX", "N/A")
        vix_lvl = levels.get("INDIA VIX", "N/A")
        nifty_rsi = levels.get("NIFTY RSI", "N/A")
        nifty_ath = levels.get("NIFTY % to ATH", "N/A")
        _pe = get_nifty50_pe()
        nifty_pe  = f"{_pe:.2f}" if _pe else "N/A"
        
        fiidii = get_fiidii()

        fii_val = fiidii.get("FII")
        dii_val = fiidii.get("DII")

        fii_pos    = fii_val is not None and fii_val >= 0
        dii_pos    = dii_val is not None and dii_val >= 0
        fii_arrow  = "▲ Inflow"  if fii_pos else "▼ Outflow"
        dii_arrow  = "▲ Inflow"  if dii_pos else "▼ Outflow"
        fii_amount = f"₹{abs(fii_val):,.2f} Cr" if fii_val is not None else "N/A"
        dii_amount = f"₹{abs(dii_val):,.2f} Cr" if dii_val is not None else "N/A"
        fii_bg     = "rgba(0,230,118,.10)" if fii_pos else "rgba(255,82,82,.10)"
        dii_bg     = "rgba(0,230,118,.10)" if dii_pos else "rgba(255,82,82,.10)"
        fii_border = "rgba(0,230,118,.35)" if fii_pos else "rgba(255,82,82,.35)"
        dii_border = "rgba(0,230,118,.35)" if dii_pos else "rgba(255,82,82,.35)"
        fii_line   = "#00e676" if fii_pos else "#ff5252"
        dii_line   = "#00e676" if dii_pos else "#ff5252"
        fii_tc     = "#00e676" if fii_pos else "#ff5252"
        dii_tc     = "#00e676" if dii_pos else "#ff5252"

        st.markdown(f"""
        <div style="display:grid;grid-template-columns:repeat(6,1fr);gap:10px;margin-bottom:14px;">
            <div style="background:rgba(255,215,0,.08);border:1px solid rgba(255,215,0,.25);
                        border-radius:14px;padding:14px 10px;text-align:center;">
                <div style="font-size:11px;color:#ffd700;font-weight:700;letter-spacing:1px;margin-bottom:5px;">NIFTY 50</div>
                <div style="font-size:22px;font-weight:800;color:#fff;">{nifty_lvl}</div>
            </div>
            <div style="background:rgba(255,215,0,.05);border:1px solid rgba(255,215,0,.15);
                        border-radius:14px;padding:14px 10px;text-align:center;">
                <div style="font-size:11px;color:#fbbf24;font-weight:700;letter-spacing:1px;margin-bottom:5px;">SENSEX</div>
                <div style="font-size:22px;font-weight:800;color:#fff;">{sensex_lvl}</div>
            </div>
            <div style="background:rgba(0,212,255,.08);border:1px solid rgba(0,212,255,.25);
                        border-radius:14px;padding:14px 10px;text-align:center;">
                <div style="font-size:11px;color:#00d4ff;font-weight:700;letter-spacing:1px;margin-bottom:5px;">INDIA VIX</div>
                <div style="font-size:22px;font-weight:800;color:#fff;">{vix_lvl}</div>
            </div>
            <div style="background:rgba(147,197,253,.07);border:1px solid rgba(147,197,253,.2);
                        border-radius:14px;padding:14px 10px;text-align:center;">
                <div style="font-size:11px;color:#93c5fd;font-weight:700;letter-spacing:1px;margin-bottom:5px;">NIFTY RSI</div>
                <div style="font-size:22px;font-weight:800;color:#fff;">{nifty_rsi}</div>
            </div>
            <div style="background:rgba(167,139,250,.07);border:1px solid rgba(167,139,250,.2);
                        border-radius:14px;padding:14px 10px;text-align:center;">
                <div style="font-size:11px;color:#a78bfa;font-weight:700;letter-spacing:1px;margin-bottom:5px;">% FROM ATH</div>
                <div style="font-size:22px;font-weight:800;color:#fff;">{nifty_ath}</div>
            </div>
            <div style="background:rgba(251,191,36,.07);border:1px solid rgba(251,191,36,.2);
                        border-radius:14px;padding:14px 10px;text-align:center;">
                <div style="font-size:11px;color:#fbbf24;font-weight:700;letter-spacing:1px;margin-bottom:5px;">NIFTY P/E</div>
                <div style="font-size:22px;font-weight:800;color:#fff;">{nifty_pe}</div>
            </div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:22px;">
            <div style="background:{fii_bg};border:1px solid {fii_border};border-radius:14px;
                        padding:16px 18px;text-align:center;position:relative;overflow:hidden;">
                <div style="position:absolute;top:0;left:0;right:0;height:3px;background:{fii_line};"></div>
                <div style="font-size:11px;color:{fii_tc};font-weight:700;letter-spacing:1.2px;margin-bottom:7px;">
                    FII &nbsp;/&nbsp; FPI &nbsp;&nbsp; {fii_arrow}
                </div>
                <div style="font-size:28px;font-weight:800;color:#fff;">{fii_amount}</div>
            </div>
            <div style="background:{dii_bg};border:1px solid {dii_border};border-radius:14px;
                        padding:16px 18px;text-align:center;position:relative;overflow:hidden;">
                <div style="position:absolute;top:0;left:0;right:0;height:3px;background:{dii_line};"></div>
                <div style="font-size:11px;color:{dii_tc};font-weight:700;letter-spacing:1.2px;margin-bottom:7px;">
                    DII &nbsp;&nbsp; {dii_arrow}
                </div>
                <div style="font-size:28px;font-weight:800;color:#fff;">{dii_amount}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with _spinner("Fetching sector data..."):
            s_data = get_sector_data()
            if "NIFTY 50" in s_data:
                nifty = s_data["NIFTY 50"]
                results = []
                for s, v in s_data.items():
                    if s == "NIFTY 50": continue
                    results.append({
                        "Sector": s,
                        "Daily Alpha": round(v["Daily"] - nifty["Daily"], 2),
                        "Weekly Alpha": round(v["Weekly"] - nifty["Weekly"], 2),
                        "Monthly Alpha": round(v["Monthly"] - nifty["Monthly"], 2),
                        "Quarterly Alpha": round(v["Quarterly"] - nifty["Quarterly"], 2),
                        "Yearly Alpha": round(v["Yearly"] - nifty["Yearly"], 2)
                    })
                df_sectors = pd.DataFrame(results)
                
                alpha_cols = ["Sector", "Daily Alpha", "Weekly Alpha", "Monthly Alpha", "Quarterly Alpha", "Yearly Alpha"]
                out_week   = df_sectors[df_sectors["Weekly Alpha"] > 0].sort_values("Weekly Alpha", ascending=False)
                under_week = df_sectors[df_sectors["Weekly Alpha"] < 0].sort_values("Weekly Alpha")

                col1, col2 = st.columns(2)
                with col1:
                    _section("Sector Outperformance", "🟢", "Weekly Alpha > 0 vs Nifty 50")
                    if out_week.empty:
                        st.info("No sector outperformed Nifty 50 this week — market led by index heavyweights.")
                        st.caption("Least underperforming sectors this week:")
                        st.dataframe(_color_pct(df_sectors.sort_values("Weekly Alpha", ascending=False).head(5)[alpha_cols]),
                                     use_container_width=True, hide_index=True)
                    else:
                        st.dataframe(_color_pct(out_week[alpha_cols]), use_container_width=True, hide_index=True)

                with col2:
                    _section("Sector Underperformance", "🔴", "Weekly Alpha < 0 vs Nifty 50")
                    if under_week.empty:
                        st.info("All sectors outperforming Nifty 50 this week — broad-based rally.")
                    else:
                        st.dataframe(_color_pct(under_week[alpha_cols]), use_container_width=True, hide_index=True)
                    
                if not out_week.empty or not under_week.empty:
                    st.divider()
                    col_best, col_worst = st.columns(2)
                    cols = ["sr. no.", "stocks from sector", "daily %", "weekly %", 
                            "monthly %", "quarterly %", "yearly %", "remark for insights"]
                    
                    with col_best:
                        if not out_week.empty:
                            best_sector = out_week.iloc[0]["Sector"]
                            _section(f"Best Sector: {best_sector}", "🏆", "Top 10 by weekly return")
                            with _spinner(f"Fetching {best_sector}..."):
                                perf_best = get_sector_performers(best_sector)
                                if perf_best["best"]:
                                    df_best = pd.DataFrame(perf_best["best"])
                                    st.dataframe(_color_pct(df_best[cols]), use_container_width=True, hide_index=True)
                                else:
                                    st.info(f"Data unavailable for {best_sector}.")
                        else:
                            st.info("No outperforming sectors this week.")

                    with col_worst:
                        if not under_week.empty:
                            worst_sector = under_week.iloc[0]["Sector"]
                            _section(f"Worst Sector: {worst_sector}", "⚠️", "Bottom 10 by weekly return")
                            with _spinner(f"Fetching {worst_sector}..."):
                                perf_worst = get_sector_performers(worst_sector)
                                if perf_worst["worst"]:
                                    df_worst = pd.DataFrame(perf_worst["worst"])
                                    st.dataframe(_color_pct(df_worst[cols]), use_container_width=True, hide_index=True)
                                else:
                                    st.info(f"Data unavailable for {worst_sector}.")
                        else:
                            st.info("No underperforming sectors this week.")
                            
                    st.divider()
                    col_indices, col_fii_stake, col_commodities = st.columns([3, 2, 2])

                    with col_indices:
                        _section("All Indian Indices", "📊", "Sorted by weekly return")
                        all_indices_list = []
                        for name, v in s_data.items():
                            weekly_val = v["Weekly"]
                            if weekly_val >= 3: idx_remark = "Strong bullish trend leading the market."
                            elif weekly_val >= 0.5: idx_remark = "Steady positive momentum."
                            elif weekly_val >= -1.0: idx_remark = "Flat/consolidating."
                            elif weekly_val >= -3.0: idx_remark = "Healthy correction."
                            else: idx_remark = "Heavy drawdown; structural damage."

                            all_indices_list.append({
                                "index name": name,
                                "daily returns %": round(v["Daily"], 2),
                                "weekly returns %": round(v["Weekly"], 2),
                                "monthly returns %": round(v["Monthly"], 2),
                                "quarterly returns %": round(v["Quarterly"], 2),
                                "yearly returns %": round(v["Yearly"], 2),
                                "remark for insights": idx_remark
                            })

                        all_indices_list = sorted(all_indices_list, key=lambda x: x["weekly returns %"], reverse=True)
                        for i, r in enumerate(all_indices_list): r["sr. no."] = i + 1
                        df_all_indices = pd.DataFrame(all_indices_list)
                        cols_all = ["sr. no.", "index name", "daily returns %", "weekly returns %",
                                    "monthly returns %", "quarterly returns %", "yearly returns %", "remark for insights"]
                        st.dataframe(_color_pct(df_all_indices[cols_all]), use_container_width=True, hide_index=True)

                    with col_fii_stake:
                        _section("FII Stake Changes", "🏦", "Nifty 500 — top increases")
                        with _spinner("Fetching FII shareholding data..."):
                            fii_stake_data = get_fii_stake_increases(_mtime=_fii_json_mtime())

                        # Show last-updated timestamp from JSON if available
                        import json, os
                        json_path = os.path.join(os.path.dirname(__file__), "fii_stake_data.json")
                        if os.path.exists(json_path):
                            try:
                                with open(json_path) as f:
                                    meta = json.load(f)
                                universe = meta.get("universe", "")
                                st.caption(f"Last updated: {meta.get('fetched_at', 'unknown')}"
                                           + (f" · {universe}" if universe else ""))
                            except Exception:
                                pass

                        if fii_stake_data:
                            df_fii_stake = pd.DataFrame(fii_stake_data)
                            st.dataframe(
                                _color_pct(df_fii_stake[["sr. no.", "company", "current FII %", "prev quarter %", "change (pp)"]]),
                                use_container_width=True, hide_index=True
                            )
                        else:
                            st.info("FII shareholding data unavailable. GitHub Actions will populate this daily.")

                    with col_commodities:
                        _section("Commodities", "🛢")
                        with _spinner("Fetching commodity prices..."):
                            commodity_data = get_commodity_data()
                        if commodity_data:
                            df_comm = pd.DataFrame(commodity_data)
                            st.dataframe(
                                df_comm[["commodity", "unit", "current price", "INR price (Latur)", "day change %", "% from 5Y high"]],
                                use_container_width=True, hide_index=True
                            )
                        else:
                            st.info("Commodity data unavailable.")

                    st.divider()
                    _section("Top 10 Weekly Performers — Indian Market", "🚀", "Across all tracked sector constituents")
                    with _spinner("Scanning all tracked Indian sector constituents..."):
                        top_overall = get_top_10_overall_stocks()
                        if top_overall:
                            df_overall = pd.DataFrame(top_overall)
                            cols_overall = ["sr. no.", "stock symbol", "daily %", "weekly %", "monthly %", "quarterly %", "yearly %", "EPS QoQ %", "EPS YoY %", "remark for insights"]
                            st.dataframe(_color_pct(df_overall[cols_overall]), use_container_width=True, hide_index=True)
                        else:
                            st.info("Overall constituent tracking unavailable.")

                    st.divider()
                    _section("Top Mutual Funds — Direct Growth", "💰", "NAV returns sorted by weekly · Source: AMFI via mfapi.in")
                    with _spinner("Fetching mutual fund NAV data..."):
                        mf_data = get_top_mutual_funds()
                    if mf_data:
                        df_mf = pd.DataFrame(mf_data)
                        st.dataframe(
                            _color_pct(df_mf[["sr. no.", "fund name", "category", "NAV (₹)", "daily %", "weekly %", "monthly %", "yearly %"]]),
                            use_container_width=True, hide_index=True
                        )
                    else:
                        st.info("Mutual fund data unavailable. Check internet connectivity to api.mfapi.in.")

            else:
                st.error("Could not fetch NIFTY 50 data.")

    # --- TAB 2: Technical Scanners ---
    with tab2:
        _section("Range Breakout Scanner", "🔍", "Scans sector constituents across 20D / 50D / 52W highs · Ranked by proximity score + volume surge")
        with _spinner("Scanning for range breakout candidates..."):
            breakout_data = get_range_breakout_stocks()
            if breakout_data:
                df_breakout = pd.DataFrame(breakout_data)
                cols_b = ["sr. no.", "stock", "sector", "current price", "% to 52W high",
                          "volume (vs 20D avg)", "MACD", "MA alignment", "RSI (14)", "overall confirmation"]
                st.dataframe(_color_pct(df_breakout[cols_b]), use_container_width=True, hide_index=True)
            else:
                st.info("No breakout candidates found right now.")

        st.divider()
        _section("Weekly RSI Oversold — Nifty 500", "📉", "Weekly RSI < 40 while price is above 200-DMA · Top 20 sorted by lowest RSI")
        with _spinner("Scanning Nifty 500 for RSI oversold candidates..."):
            rsi_candidates = get_nifty500_weekly_rsi_scan()
        if rsi_candidates:
            st.dataframe(_color_pct(pd.DataFrame(rsi_candidates)), use_container_width=True, hide_index=True)
        else:
            st.info("No RSI < 40 candidates found above 200-DMA in Nifty 500 universe.")

        st.divider()
        _section("Volume Analysis — Nifty 500", "📦", "Buy Vol = Volume × (Close−Low)/(High−Low)  ·  Sell Vol = Volume × (High−Close)/(High−Low)")
        with _spinner("Scanning Nifty 500 universe for volume data..."):
            vol_data = get_volume_split_stocks()

            col_buy, col_sell = st.columns(2)

            with col_buy:
                st.markdown("**🟢 Top 10 — Highest Buying Volume (Daily + Weekly)**")
                if vol_data["buying"]:
                    df_buy = pd.DataFrame(vol_data["buying"])
                    cols_buy = ["sr. no.", "stock", "prev day close (NSE)", "day change %", "candle",
                                "daily buying vol", "daily buying %",
                                "weekly buying vol", "weekly buying %"]
                    st.dataframe(_color_pct(df_buy[cols_buy]), use_container_width=True, hide_index=True)
                else:
                    st.info("No data available.")

            with col_sell:
                st.markdown("**🔴 Top 10 — Highest Selling Volume (Daily + Weekly)**")
                if vol_data["selling"]:
                    df_sell = pd.DataFrame(vol_data["selling"])
                    cols_sell = ["sr. no.", "stock", "prev day close (NSE)", "day change %", "candle",
                                 "daily selling vol", "daily selling %",
                                 "weekly selling vol", "weekly selling %"]
                    st.dataframe(_color_pct(df_sell[cols_sell]), use_container_width=True, hide_index=True)
                else:
                    st.info("No data available.")

    # --- TAB 3: Fundamental Scanners ---
    with tab3:
        st.header("DCF Intrinsic Value Scanner — Nifty 500")
        st.caption(
            "Screens the Nifty 500 universe for stocks whose current market price is within "
            "**–35% to +15%** of their Base-Case DCF intrinsic value. "
            "Three scenarios are computed per stock using Free Cash Flow projections: "
            "**Base** (11% WACC · 4% terminal), "
            "**Bearish** (12% WACC · 3.5% terminal · 60% base growth), "
            "**Bear** (13% WACC · 2.5% terminal · 30% base growth). "
            "Industry PE is the median PE of sector peers. "
            "Results are sorted by largest discount to intrinsic value first. "
            "*1-hour cache — click 'Force Refresh' in the sidebar to reload.*"
        )

        with _spinner("Scanning Nifty 500 — fetching fundamentals & computing DCF for each stock (may take 60–90 s on first load)..."):
            dcf_data = get_dcf_valuation_stocks()

        if dcf_data:
            df_dcf = pd.DataFrame(dcf_data)
            # Column order matching user spec
            cols_order = [
                "sr. no.", "name", "price (₹)",
                "base case DCF IV (₹)", "bearish DCF IV (₹)", "bear case DCF IV (₹)",
                "industry PE", "current PE", "current PEG",
                "1Y EPS growth %", "3Y EPS CAGR %", "5Y EPS CAGR %",
                "book value (₹)", "FCF yield %", "FCF margin %",
                "% to intrinsic value", "remarks",
            ]
            # Only include columns that exist in the df
            cols_order = [c for c in cols_order if c in df_dcf.columns]
            st.success(f"Found **{len(df_dcf)}** Nifty 500 stocks near DCF intrinsic value.")
            st.dataframe(
                _color_pct(df_dcf[cols_order]),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.warning("No stocks matched the DCF filter — data may still be loading or all stocks are overvalued/undervalued beyond the filter range. Try refreshing.")

    # --- TAB 4: News & Macro ---
    with tab4:
        st.header("Live News Aggregator")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("4. Stocks in News (Upside Potential)")
            markets_news = fetch_rss_news(ET_RSS_FEEDS["Markets"])
            for n in markets_news:
                st.markdown(f"- **[{n['Title']}]({n['Link']})** ({n['Published']})")
                
            st.subheader("9. Recent Contracts / Bid Winners")
            comp_news = fetch_rss_news(ET_RSS_FEEDS["Companies"])
            for n in comp_news:
                st.markdown(f"- **[{n['Title']}]({n['Link']})** ({n['Published']})")
                
        with col2:
            st.subheader("5. Macroeconomic News")
            macro_news = fetch_rss_news(ET_RSS_FEEDS["Macro Economy"])
            for n in macro_news:
                st.markdown(f"- **[{n['Title']}]({n['Link']})** ({n['Published']})")
                
            st.subheader("8. Best & Worst Q2 Results (Earnings News)")
            earn_news = fetch_rss_news(ET_RSS_FEEDS["Earnings"])
            for n in earn_news:
                st.markdown(f"- **[{n['Title']}]({n['Link']})** ({n['Published']})")

    # --- TAB 5: Global Markets ---
    with tab5:
        st.header("Top 20 Global Markets Performance")
        with _spinner("Fetching maximum history for global indices to determine ATH..."):
            global_data = get_global_markets_data()
            if global_data:
                df_global = pd.DataFrame(global_data)
                cols = ["sr no", "name of country", "name of index", "indices current value", 
                        "% of current value from preceding day", "monthly %", "quarterly %", 
                        "yearly %", "3-year %", "its ATH", "% from ATH", 
                        "remarks for insights from investor"]
                st.dataframe(_color_pct(df_global[cols]), use_container_width=True, hide_index=True)
            else:
                st.error("Could not fetch global markets data.")

    # --- TAB 6: Market Breadth ---
    with tab6:
        st.header("Market Breadth — Nifty 500 Universe")
        st.caption("Scans ~500 NSE stocks. 30-min cache. 52W high/low = within 1.5% of the 52-week extreme.")
        with _spinner("Scanning ~500 NSE stocks for breadth indicators..."):
            breadth = get_market_breadth()

        total = breadth.get("total", 0)
        if total > 0:
            adv  = breadth["advances"]
            dec  = breadth["declines"]
            unch = breadth["unchanged"]
            ad_ratio = round(adv / dec, 2) if dec > 0 else None

            c1, c2, c3, c4, c5, c6 = st.columns(6)
            c1.metric("Stocks Scanned",    total)
            c2.metric("Advances",          adv,  f"{adv/total*100:.1f}%")
            c3.metric("Declines",          dec,  f"-{dec/total*100:.1f}%")
            c4.metric("A/D Ratio",         str(ad_ratio) if ad_ratio else "N/A")
            c5.metric("% Above 200-DMA",   f"{breadth['above_200dma']/total*100:.1f}%")
            c6.metric("% Above 50-DMA",    f"{breadth['above_50dma']/total*100:.1f}%")

            st.divider()
            col_h, col_l = st.columns(2)
            with col_h:
                st.subheader(f"Near 52-Week Highs  ({breadth['new_52w_highs']} stocks)")
                if breadth["high_stocks"]:
                    st.dataframe(pd.DataFrame({"stock": breadth["high_stocks"]}),
                                 use_container_width=True, hide_index=True)
                else:
                    st.info("No stocks within 1.5% of 52W high.")
            with col_l:
                st.subheader(f"Near 52-Week Lows  ({breadth['new_52w_lows']} stocks)")
                if breadth["low_stocks"]:
                    st.dataframe(pd.DataFrame({"stock": breadth["low_stocks"]}),
                                 use_container_width=True, hide_index=True)
                else:
                    st.info("No stocks within 1.5% of 52W low.")
        else:
            st.error("Market breadth data unavailable.")

    # --- TAB 7: Commodities & Currencies ---
    with tab7:
        st.header("Commodities & Currency Monitor")

        col_comm, col_curr = st.columns(2)

        with col_comm:
            st.subheader("Commodities")
            with _spinner("Fetching commodity prices..."):
                ext_comm = get_extended_commodity_data()
            if ext_comm:
                st.caption("Gold & Silver: INR price = MCX spot rate (Latur local market reference). "
                           "1 troy oz = 31.1035g · USD/INR fetched live.")
                st.dataframe(
                    _color_pct(pd.DataFrame(ext_comm)[["commodity", "unit", "price",
                                            "INR price (Latur)", "day %",
                                            "week %", "month %", "quarter %", "yearly %",
                                            "% from 5Y high", "insight"]]),
                    use_container_width=True, hide_index=True,
                )
            else:
                st.info("Commodity data unavailable.")

        with col_curr:
            st.subheader("Currencies vs Indian Rupee")
            with _spinner("Fetching currency rates..."):
                curr_data = get_currency_data()
            if curr_data:
                st.dataframe(
                    _color_pct(pd.DataFrame(curr_data)[["pair", "rate", "day %",
                                             "week %", "month %", "yearly %",
                                             "% from 5Y high", "insight"]]),
                    use_container_width=True, hide_index=True,
                )
            else:
                st.info("Currency data unavailable.")

    # --- TAB 8: Options Snapshot ---
    with tab8:
        st.header("Options Snapshot — Nifty & BankNifty")
        st.caption("PCR, Max Pain, and full OI chain for the nearest expiry. Sourced from NSE — requires an Indian IP address.")

        symbol_choice = st.radio("Select Index", ["NIFTY", "BANKNIFTY"], horizontal=True, key="opt_symbol")

        with _spinner(f"Fetching {symbol_choice} option chain from NSE..."):
            opt = get_options_snapshot(symbol_choice)

        if opt.get("error"):
            st.warning(f"⚠️  {opt['error']}")
            st.info("To use this feature, run the dashboard from a machine with an Indian IP address, "
                    "or connect via an India-based VPN.")
        else:
            spot     = opt["spot"]
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Spot Price",           f"{spot:,.2f}")
            c2.metric("Nearest Expiry",        opt["expiry"])
            pcr = opt["pcr"]
            c3.metric("PCR (All Expiries)",    str(pcr) if pcr else "N/A",
                      "Bullish >1" if pcr and pcr > 1 else ("Bearish <1" if pcr else ""))
            c4.metric("Max Pain",              f"{opt['max_pain']:,}" if opt["max_pain"] else "N/A")
            c5.metric("Total OI (Calls+Puts)", f"{opt['total_call_oi'] + opt['total_put_oi']:,}")

            st.divider()
            st.subheader(f"{symbol_choice} Option Chain — Expiry: {opt['expiry']}  (ATM ± 10%)")
            atm_rows = opt["atm_rows"]
            if atm_rows:
                df_opt = pd.DataFrame(atm_rows)
                st.dataframe(
                    df_opt[["call OI", "call Δ OI", "call LTP", "strike", "put LTP", "put OI", "put Δ OI"]],
                    use_container_width=True, hide_index=True,
                )
            else:
                st.info("No option chain rows found near ATM.")

    # --- TAB 9: Earnings Calendar ---
    with tab9:
        st.header("Earnings Calendar")
        st.caption("Upcoming quarterly results & board meetings. NSE calendar is authoritative but requires an Indian IP; "
                   "falls back to Yahoo Finance estimates automatically.")
        with _spinner("Fetching earnings calendar..."):
            earnings = get_earnings_calendar()

        if earnings.get("source"):
            st.caption(f"Source: **{earnings['source']}**")

        if earnings.get("data"):
            df_earn = pd.DataFrame(earnings["data"])
            st.dataframe(df_earn[["company", "date", "event"]],
                         use_container_width=True, hide_index=True)
        else:
            st.warning(f"⚠️  {earnings.get('error', 'No data available.')}")
            st.info("NSE Event Calendar requires an Indian IP address. "
                    "Connect via an India-based VPN to see the full calendar.")

if __name__ == "__main__":
    run_dashboard()
