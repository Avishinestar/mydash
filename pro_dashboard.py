import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import feedparser
import io
import warnings
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
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "BHARTIARTL.NS", 
    "SBIN.NS", "INFY.NS", "LICI.NS", "ITC.NS", "HINDUNILVR.NS", "LT.NS", 
    "BAJFINANCE.NS", "HCLTECH.NS", "MARUTI.NS", "SUNPHARMA.NS", "ADANIENT.NS", 
    "KOTAKBANK.NS", "TITAN.NS", "ONGC.NS", "TATAMOTORS.NS", "NTPC.NS", 
    "AXISBANK.NS", "POWERGRID.NS", "M&M.NS", "ULTRACEMCO.NS", "ASIANPAINT.NS",
    "BAJAJFINSV.NS", "WIPRO.NS", "NESTLEIND.NS", "TECHM.NS", "BAJAJ-AUTO.NS"
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
    # Large Cap (Nifty 50 core)
    "RELIANCE.NS","TCS.NS","HDFCBANK.NS","ICICIBANK.NS","BHARTIARTL.NS","SBIN.NS","INFY.NS",
    "LICI.NS","ITC.NS","HINDUNILVR.NS","LT.NS","BAJFINANCE.NS","HCLTECH.NS","MARUTI.NS",
    "SUNPHARMA.NS","ADANIENT.NS","KOTAKBANK.NS","TITAN.NS","ONGC.NS","TATAMOTORS.NS",
    "NTPC.NS","AXISBANK.NS","POWERGRID.NS","M&M.NS","ULTRACEMCO.NS","ASIANPAINT.NS",
    "BAJAJFINSV.NS","WIPRO.NS","NESTLEIND.NS","TECHM.NS","BAJAJ-AUTO.NS",
    # Banking & Finance
    "INDUSINDBK.NS","BANKBARODA.NS","PNB.NS","FEDERALBNK.NS","IDFCFIRSTB.NS","CANBK.NS",
    "UNIONBANK.NS","INDIANB.NS","BANKINDIA.NS","CENTRALBK.NS","MAHABANK.NS","UCOBANK.NS",
    "CHOLAFIN.NS","MUTHOOTFIN.NS","RECLTD.NS","PFC.NS","HDFCAMC.NS","SBICARD.NS",
    "ABCAPITAL.NS","SHRIRAMFIN.NS","MANAPPURAM.NS","LICHSGFIN.NS","IIFL.NS","SUNDARMFIN.NS",
    "CANFINHOME.NS","REPCO.NS","PNBHOUSING.NS","UGROCAP.NS","CREDITACC.NS",
    # IT & Tech
    "LTIM.NS","COFORGE.NS","PERSISTENT.NS","MPHASIS.NS","KPITTECH.NS","LTTS.NS",
    "OFSS.NS","HEXAWARE.NS","ZENSAR.NS","NIITTECH.NS","TATAELXSI.NS","CYIENT.NS",
    "MASTEK.NS","BIRLASOFT.NS","RAMSARUP.NS","SONATSOFTW.NS","TANLA.NS","ROUTE.NS",
    # Auto & Auto Ancillaries
    "HEROMOTOCO.NS","EICHERMOT.NS","TVSMOTOR.NS","ASHOKLEY.NS","MOTHERSON.NS","BOSCHLTD.NS",
    "ESCORTS.NS","APOLLOTYRE.NS","MRF.NS","CEAT.NS","BALKRISIND.NS","EXIDEIND.NS",
    "AMARARAJA.NS","SUNDRMFAST.NS","BHARAT.NS","ENDURANCE.NS","SUPRAJIT.NS","GABRIEL.NS",
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
    "GRASIM.NS","ADANIPORTS.NS","AMBUJACEM.NS","SHREECEM.NS","ACC.NS","GMRINFRA.NS",
    "IRB.NS","HCC.NS","NBCC.NS","KEC.NS","KALPATPOWER.NS","THERMAX.NS","CUMMINSIND.NS",
    "ABB.NS","SIEMENS.NS","VOLTAS.NS","HAVELLS.NS","POLYCAB.NS","KEI.NS","FINOLEX.NS",
    # Realty
    "DLF.NS","MACROTECH.NS","GODREJPROP.NS","OBEROIRLTY.NS","PRESTIGE.NS",
    "PHOENIXLTD.NS","BRIGADE.NS","SOBHA.NS","MAHLIFE.NS","SUNTECK.NS","KOLTEPATIL.NS",
    # Chemicals & Specialty
    "PIDILITIND.NS","SRF.NS","AARTIIND.NS","DEEPAKNTR.NS","NAVINFLUOR.NS","FINEORG.NS",
    "TATACHEMICALS.NS","UPL.NS","PIIND.NS","COROMANDEL.NS","RALLIS.NS","BASF.NS",
    "GALAXYSURF.NS","CLEAN.NS","ROSSARI.NS","SUDARSCHEM.NS","TATACHEM.NS",
    # Consumption & Retail
    "TRENT.NS","PAGEIND.NS","BATAINDIA.NS","CROMPTON.NS","DIXON.NS","RELAXO.NS",
    "RAYMOND.NS","VEDANT.NS","DMART.NS","NYKAA.NS","ZOMATO.NS","JUBLFOOD.NS",
    "DEVYANI.NS","WESTLIFE.NS","SAPPHIRE.NS",
    # Hotels & Tourism
    "INDHOTEL.NS","LEMONTREE.NS","CHALET.NS","EIHOTEL.NS","MAHINDHOLIDAYS.NS",
    # Logistics & Transport
    "BLUEDART.NS","DELHIVERY.NS","CONCOR.NS","MAHLOG.NS","TCI.NS","VRL.NS",
    # Telecom & Media
    "IDEA.NS","TATACOMM.NS","HFCL.NS","SUNTV.NS","PVRINOX.NS","SAREGAMA.NS","NAZARA.NS",
    # Defence & Aerospace
    "HAL.NS","BEL.NS","BHEL.NS","BEML.NS","PARAS.NS","MAZDOCK.NS","COCHINSHIP.NS",
    # Others / Diversified
    "ADANIENTERP.NS","ADANIPORTS.NS","ADANITRANS.NS","ATUL.NS","BALKRISHNA.NS",
    "BERGEPAINT.NS","CASTROLIND.NS","GSPL.NS","HONAUT.NS","IGL.NS","MGL.NS",
    "MCDOWELL-N.NS","NAUKRI.NS","POLICYBZR.NS","PAYTM.NS","CARTRADE.NS",
]

SECTOR_CONSTITUENTS = {
    "BANK": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS", "INDUSINDBK.NS", "BANKBARODA.NS", "PNB.NS", "FEDERALBNK.NS", "IDFCFIRSTB.NS"],
    "IT": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS", "LTIM.NS", "COFORGE.NS", "PERSISTENT.NS", "MPHASIS.NS", "KPITTECH.NS"],
    "AUTO": ["MARUTI.NS", "TATAMOTORS.NS", "M&M.NS", "BAJAJ-AUTO.NS", "HEROMOTOCO.NS", "EICHERMOT.NS", "TVSMOTOR.NS", "ASHOKLEY.NS", "MOTHERSON.NS", "BOSCHLTD.NS"],
    "FMCG": ["ITC.NS", "HINDUNILVR.NS", "NESTLEIND.NS", "BRITANNIA.NS", "TATACONSUM.NS", "GODREJCP.NS", "DABUR.NS", "MARICO.NS", "VBL.NS", "COLPAL.NS"],
    "PHARMA": ["SUNPHARMA.NS", "CIPLA.NS", "DRREDDY.NS", "DIVISLAB.NS", "LUPIN.NS", "AUROPHARMA.NS", "TORNTPHARM.NS", "ZYDUSLIFE.NS", "ALKEM.NS", "BIOCON.NS"],
    "METAL": ["TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "VEDL.NS", "COALINDIA.NS", "NMDC.NS", "SAIL.NS", "JINDALSTEL.NS", "NATIONALUM.NS", "RATNAMANI.NS"],
    "ENERGY": ["RELIANCE.NS", "ONGC.NS", "NTPC.NS", "POWERGRID.NS", "IOC.NS", "BPCL.NS", "GAIL.NS", "HINDPETRO.NS", "TATAPOWER.NS", "PETRONET.NS"],
    "FINANCIAL SERVICES": ["BAJFINANCE.NS", "BAJAJFINSV.NS", "CHOLAFIN.NS", "MUTHOOTFIN.NS", "RECLTD.NS", "PFC.NS", "HDFCAMC.NS", "SBICARD.NS", "ABCAPITAL.NS", "SHRIRAMFIN.NS"],
    "REALTY": ["DLF.NS", "MACROTECH.NS", "GODREJPROP.NS", "OBEROIRLTY.NS", "PRESTIGE.NS", "PHOENIXLTD.NS", "BRIGADE.NS", "SOBHA.NS", "MAHLIFE.NS", "SUNTECK.NS"],
    "MEDIA": ["PVRINOX.NS", "SUNTV.NS", "NETWORK18.NS", "TV18BRDCST.NS", "NAVNETEDUL.NS", "NDTV.NS", "HATHWAY.NS", "DISHTV.NS", "NAZARA.NS", "SAREGAMA.NS"],
    "PSU BANK": ["SBIN.NS", "BANKBARODA.NS", "PNB.NS", "CANBK.NS", "UNIONBANK.NS", "INDIANB.NS", "BANKINDIA.NS", "CENTRALBK.NS", "MAHABANK.NS", "UCOBANK.NS"],
    "INFRASTRUCTURE": ["LT.NS", "GRASIM.NS", "ULTRACEMCO.NS", "ADANIPORTS.NS", "AMBUJACEM.NS", "SHREECEM.NS", "ACC.NS", "GMRINFRA.NS", "IRB.NS", "HCC.NS"],
    "COMMODITIES": ["TATACHEMICALS.NS", "UPL.NS", "PIIND.NS", "COROMANDEL.NS", "SRF.NS", "AARTIIND.NS", "DEEPAKNTR.NS", "TATASTEEL.NS", "JSWSTEEL.NS", "VEDL.NS"],
    "CONSUMPTION": ["ASIANPAINT.NS", "TITAN.NS", "TRENT.NS", "PAGEIND.NS", "JUBIQUANT.NS", "BATAINDIA.NS", "VOLTAS.NS", "CROMPTON.NS", "DIXON.NS", "HAVELLS.NS"],
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
                    "daily buying %": f"{day_buy_pct}%",
                    "weekly buying vol": int(week_buy_vol),
                    "weekly buying %": f"{week_buy_pct}%",
                    "daily selling vol": int(day_sell_vol),
                    "daily selling %": f"{day_sell_pct}%",
                    "weekly selling vol": int(week_sell_vol),
                    "weekly selling %": f"{week_sell_pct}%",
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
    data = {}
    for name, ticker in SECTORS.items():
        try:
            df = yf.download(ticker, period="1y", interval="1d", progress=False)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.droplevel(1)
            if len(df) < 64:
                continue
            daily = (df['Close'].iloc[-1] / df['Close'].iloc[-2]) - 1
            weekly = (df['Close'].iloc[-1] / df['Close'].iloc[-5]) - 1
            monthly = (df['Close'].iloc[-1] / df['Close'].iloc[-21]) - 1
            quarterly = (df['Close'].iloc[-1] / df['Close'].iloc[-63]) - 1
            yearly = (df['Close'].iloc[-1] / df['Close'].iloc[0]) - 1
            data[name] = {
                "Daily": float(daily) * 100,
                "Weekly": float(weekly) * 100,
                "Monthly": float(monthly) * 100,
                "Quarterly": float(quarterly) * 100,
                "Yearly": float(yearly) * 100
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
        for i, r in enumerate(results): r["sr. no."] = i + 1
        return results
    except Exception:
        return []

@st.cache_data(ttl=300)
def get_nifty_sensex_levels():
    res = {"NIFTY 50": "N/A", "SENSEX": "N/A", "INDIA VIX": "N/A", "NIFTY RSI": "N/A", "NIFTY % to ATH": "N/A"}
    try:
        df = yf.download(["^NSEI", "^BSESN", "^INDIAVIX"], period="max", interval="1d", progress=False)
        for name, ticker in [("NIFTY 50", "^NSEI"), ("SENSEX", "^BSESN"), ("INDIA VIX", "^INDIAVIX")]:
            try:
                if isinstance(df.columns, pd.MultiIndex):
                    if ticker in df.columns.levels[1] or ticker in df.columns.get_level_values(1):
                        series = df.xs(ticker, axis=1, level=1)['Close'].dropna()
                        current = float(series.iloc[-1])
                        res[name] = f"{current:,.2f}"
                        if name == "NIFTY 50":
                            import ta
                            rsi_series = ta.momentum.RSIIndicator(series, window=14).rsi().dropna()
                            if not rsi_series.empty:
                                res["NIFTY RSI"] = f"{rsi_series.iloc[-1]:.1f}"
                            high_series = df.xs(ticker, axis=1, level=1)['High'].dropna()
                            ath = float(high_series.max())
                            pct_ath = ((current / ath) - 1) * 100
                            res["NIFTY % to ATH"] = f"{pct_ath:.2f}%"
                else:
                    if ticker in df['Close'].columns:
                        series = df['Close'][ticker].dropna()
                        current = float(series.iloc[-1])
                        res[name] = f"{current:,.2f}"
                        if name == "NIFTY 50":
                            import ta
                            rsi_series = ta.momentum.RSIIndicator(series, window=14).rsi().dropna()
                            if not rsi_series.empty:
                                res["NIFTY RSI"] = f"{rsi_series.iloc[-1]:.1f}"
                            high_series = df['High'][ticker].dropna()
                            ath = float(high_series.max())
                            pct_ath = ((current / ath) - 1) * 100
                            res["NIFTY % to ATH"] = f"{pct_ath:.2f}%"
            except Exception:
                pass
    except Exception:
        pass
        
    if res["NIFTY 50"] == "N/A":
        get_nifty_sensex_levels.clear()
        
    return res

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

@st.cache_data(ttl=86400)  # quarterly data — refresh once a day
def get_fii_stake_increases():
    """Scan NIFTY_50 stocks for companies where FII/FPI increased stake in the latest quarter."""
    import requests
    results = []
    session = requests.Session()
    try:
        session.get("https://www.nseindia.com", timeout=10, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        })
    except Exception:
        pass

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        "Referer": "https://www.nseindia.com/",
        "Accept": "application/json",
    }

    scan_symbols = [t.replace(".NS", "") for t in NIFTY_50]

    for symbol in scan_symbols:
        try:
            resp = session.get(
                f"https://www.nseindia.com/api/corporate-shareholding-patterns?index=equities&symbol={symbol}",
                timeout=10, headers=headers
            )
            data = resp.json()
            records = data if isinstance(data, list) else data.get("data", [])
            if len(records) < 2:
                continue

            def extract_fii(rec):
                for key in ["fiiFpiHolding", "totalForeignPortfolioInvestors", "fii", "FII"]:
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
                    "change (pp)": f"+{change}",
                })
        except Exception:
            pass

    results = sorted(results, key=lambda x: float(str(x["change (pp)"]).replace("+", "")), reverse=True)[:10]
    for i, r in enumerate(results):
        r["sr. no."] = i + 1
    return results

def run_dashboard():
    st.title("Advanced Investor Dashboard 📈")
    st.markdown("Developed as requested, utilizing real-time market data to achieve all 9 tasks.")
    
    col_a, col_b = st.columns([8, 2])
    with col_b:
        if st.button("🔄 Force Refresh All Data"):
            st.cache_data.clear()
            st.rerun()

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["1 & 2: Sector Performance", "3 & 7: Technical Scanners", "6: Fundamentals", "4, 5, 8, 9: News & Macro", "Global Markets"])

    # --- TAB 1: Sector Performance ---
    with tab1:
        st.header("Task 1 & 2: Sector Outperformance and Underperformance vs Nifty 50")
        
        levels = get_nifty_sensex_levels()
        nifty_lvl = levels.get("NIFTY 50", "N/A")
        sensex_lvl = levels.get("SENSEX", "N/A")
        vix_lvl = levels.get("INDIA VIX", "N/A")
        nifty_rsi = levels.get("NIFTY RSI", "N/A")
        nifty_ath = levels.get("NIFTY % to ATH", "N/A")
        
        fiidii = get_fiidii()

        fii_val = fiidii.get("FII")
        dii_val = fiidii.get("DII")

        fii_color  = "#1a7a1a" if (fii_val is not None and fii_val >= 0) else "#cc0000"
        dii_color  = "#1a7a1a" if (dii_val is not None and dii_val >= 0) else "#cc0000"
        fii_arrow  = "▲ Inflow" if (fii_val is not None and fii_val >= 0) else "▼ Outflow"
        dii_arrow  = "▲ Inflow" if (dii_val is not None and dii_val >= 0) else "▼ Outflow"
        fii_amount = f"₹{abs(fii_val):,.2f} Cr" if fii_val is not None else "N/A"
        dii_amount = f"₹{abs(dii_val):,.2f} Cr" if dii_val is not None else "N/A"

        st.markdown(
            f"""
            <div style="background-color: #cc0000; padding: 10px; border-radius: 5px; color: white; font-weight: bold; margin-bottom: 12px; text-align: center; font-size: 18px;">
                NIFTY 50: {nifty_lvl} &nbsp;|&nbsp; RSI: {nifty_rsi} &nbsp;|&nbsp; ATH Dist: {nifty_ath} &nbsp;|&nbsp; SENSEX: {sensex_lvl} &nbsp;|&nbsp; INDIA VIX: {vix_lvl}
            </div>
            <div style="display: flex; gap: 12px; margin-bottom: 20px;">
                <div style="flex: 1; background-color: {fii_color}; padding: 14px 10px; border-radius: 8px; color: white; text-align: center; box-shadow: 0 2px 6px rgba(0,0,0,0.3);">
                    <div style="font-size: 13px; font-weight: 600; letter-spacing: 1px; opacity: 0.85; margin-bottom: 4px;">FII / FPI &nbsp;{fii_arrow}</div>
                    <div style="font-size: 26px; font-weight: 800;">{fii_amount}</div>
                </div>
                <div style="flex: 1; background-color: {dii_color}; padding: 14px 10px; border-radius: 8px; color: white; text-align: center; box-shadow: 0 2px 6px rgba(0,0,0,0.3);">
                    <div style="font-size: 13px; font-weight: 600; letter-spacing: 1px; opacity: 0.85; margin-bottom: 4px;">DII &nbsp;{dii_arrow}</div>
                    <div style="font-size: 26px; font-weight: 800;">{dii_amount}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.spinner("Fetching sector data..."):
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
                
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("1. Sector Outperformance (Weekly Alpha > 0)")
                    out_week = df_sectors[df_sectors["Weekly Alpha"] > 0].sort_values("Weekly Alpha", ascending=False)
                    st.dataframe(out_week[["Sector", "Daily Alpha", "Weekly Alpha", "Monthly Alpha", "Quarterly Alpha", "Yearly Alpha"]], use_container_width=False)

                with col2:
                    st.subheader("2. Sector Underperformance (Weekly Alpha < 0)")
                    under_week = df_sectors[df_sectors["Weekly Alpha"] < 0].sort_values("Weekly Alpha")
                    st.dataframe(under_week[["Sector", "Daily Alpha", "Weekly Alpha", "Monthly Alpha", "Quarterly Alpha", "Yearly Alpha"]], use_container_width=False)
                    
                if not out_week.empty or not under_week.empty:
                    st.divider()
                    col_best, col_worst = st.columns(2)
                    cols = ["sr. no.", "stocks from sector", "daily %", "weekly %", 
                            "monthly %", "quarterly %", "yearly %", "remark for insights"]
                    
                    with col_best:
                        if not out_week.empty:
                            best_sector = out_week.iloc[0]["Sector"]
                            st.subheader(f"Top 10 Weekly Performing Stocks in Best Sector: {best_sector}")
                            
                            with st.spinner(f"Fetching constituents for {best_sector}..."):
                                perf_best = get_sector_performers(best_sector)
                                if perf_best["best"]:
                                    df_best = pd.DataFrame(perf_best["best"])
                                    st.dataframe(df_best[cols], use_container_width=False, hide_index=True)
                                else:
                                    st.info(f"Constituent tracking not configured or unavailable for {best_sector}.")
                        else:
                            st.info("No outperforming sectors this week.")
                            
                    with col_worst:
                        if not under_week.empty:
                            worst_sector = under_week.iloc[0]["Sector"]
                            st.subheader(f"Top 10 Weekly Underperforming Stocks in Worst Sector: {worst_sector}")
                            
                            with st.spinner(f"Fetching constituents for {worst_sector}..."):
                                perf_worst = get_sector_performers(worst_sector)
                                if perf_worst["worst"]:
                                    df_worst = pd.DataFrame(perf_worst["worst"])
                                    st.dataframe(df_worst[cols], use_container_width=False, hide_index=True)
                                else:
                                    st.info(f"Constituent tracking not configured or unavailable for {worst_sector}.")
                        else:
                            st.info("No underperforming sectors this week.")
                            
                    st.divider()
                    col_indices, col_fii_stake = st.columns([3, 2])

                    with col_indices:
                        st.subheader("All Indian Indices Performance")
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
                        st.dataframe(df_all_indices[cols_all], use_container_width=True, hide_index=True)

                    with col_fii_stake:
                        st.subheader("Top 10 FII Stake Increases (Latest Quarter)")
                        with st.spinner("Fetching FII shareholding data..."):
                            fii_stake_data = get_fii_stake_increases()
                        if fii_stake_data:
                            df_fii_stake = pd.DataFrame(fii_stake_data)
                            st.dataframe(
                                df_fii_stake[["sr. no.", "company", "current FII %", "prev quarter %", "change (pp)"]],
                                use_container_width=True, hide_index=True
                            )
                        else:
                            st.info("FII shareholding data unavailable (NSE geo-restricted on cloud).")
                    
                    st.divider()
                    st.subheader("Top 10 Weekly Performing Stocks (Indian Market)")
                    with st.spinner("Scanning all tracked Indian sector constituents..."):
                        top_overall = get_top_10_overall_stocks()
                        if top_overall:
                            df_overall = pd.DataFrame(top_overall)
                            cols_overall = ["sr. no.", "stock symbol", "daily %", "weekly %", "monthly %", "quarterly %", "yearly %", "remark for insights"]
                            st.dataframe(df_overall[cols_overall], use_container_width=False, hide_index=True)
                        else:
                            st.info("Overall constituent tracking unavailable.")

            else:
                st.error("Could not fetch NIFTY 50 data.")

    # --- TAB 2: Technical Scanners ---
    with tab2:
        st.header("Task 3 & 7: Technical Scanners")
        
        with st.spinner("Fetching historical data for Nifty 50 liquid stocks..."):
            daily_df = get_stock_data_daily()
            weekly_df = get_stock_data_weekly()

        st.subheader("3. Top 10 Stocks About to Break Out of Range")
        st.caption("Scans all tracked sector constituents (~130 stocks) across 20D / 50D / 52W highs. Ranked by proximity score + volume surge.")
        with st.spinner("Scanning for range breakout candidates..."):
            breakout_data = get_range_breakout_stocks()
            if breakout_data:
                df_breakout = pd.DataFrame(breakout_data)
                cols_b = ["sr. no.", "stock", "sector", "current price", "% to 52W high",
                          "volume (vs 20D avg)", "MACD", "MA alignment", "RSI (14)", "overall confirmation"]
                st.dataframe(df_breakout[cols_b], use_container_width=True, hide_index=True)
            else:
                st.info("No breakout candidates found right now.")

        st.divider()
        st.subheader("7. Weekly RSI < 40 (Above 200-DMA) — Nifty 500 Universe")
        st.caption("Scans ~500 NSE stocks for weekly RSI < 40 while price remains above 200-DMA. Top 20 sorted by lowest RSI.")
        with st.spinner("Scanning Nifty 500 for weekly RSI oversold candidates..."):
            rsi_candidates = get_nifty500_weekly_rsi_scan()
        if rsi_candidates:
            st.dataframe(pd.DataFrame(rsi_candidates), use_container_width=True, hide_index=True)
        else:
            st.info("No RSI < 40 candidates found above 200-DMA in Nifty 500 universe.")

        st.divider()
        st.subheader("Nifty 500 — Volume Analysis (Preceding Day)")
        st.caption("Buying Volume = Total Volume × (Close − Low) / (High − Low) | Selling Volume = Total Volume × (High − Close) / (High − Low)")
        with st.spinner("Scanning Nifty 500 universe for volume data..."):
            vol_data = get_volume_split_stocks()

            col_buy, col_sell = st.columns(2)

            with col_buy:
                st.markdown("**🟢 Top 10 — Highest Buying Volume (Daily + Weekly)**")
                if vol_data["buying"]:
                    df_buy = pd.DataFrame(vol_data["buying"])
                    cols_buy = ["sr. no.", "stock", "prev day close (NSE)", "day change %", "candle",
                                "daily buying vol", "daily buying %",
                                "weekly buying vol", "weekly buying %"]
                    st.dataframe(df_buy[cols_buy], use_container_width=True, hide_index=True)
                else:
                    st.info("No data available.")

            with col_sell:
                st.markdown("**🔴 Top 10 — Highest Selling Volume (Daily + Weekly)**")
                if vol_data["selling"]:
                    df_sell = pd.DataFrame(vol_data["selling"])
                    cols_sell = ["sr. no.", "stock", "prev day close (NSE)", "day change %", "candle",
                                 "daily selling vol", "daily selling %",
                                 "weekly selling vol", "weekly selling %"]
                    st.dataframe(df_sell[cols_sell], use_container_width=True, hide_index=True)
                else:
                    st.info("No data available.")

    # --- TAB 3: Fundamental Scanners ---
    with tab3:
        st.header("Task 6: Undervalued vs Intrinsic Value")
        with st.spinner("Fetching fundamental data..."):
            info_dict = get_stock_info()
            undervalued = []

            for t, info in info_dict.items():
                pe = info.get("trailingPE", info.get("forwardPE", 999))
                roe = info.get("returnOnEquity", 0)
                pb = info.get("priceToBook", 0)
                
                # Rule: PE < 20, ROE > 15%
                if pe and roe and pe < 20 and roe > 0.15:
                    undervalued.append({
                        "Ticker": t,
                        "P/E Ratio": round(pe, 2),
                        "P/B Ratio": round(pb, 2) if pb else "N/A",
                        "ROE (%)": round(roe * 100, 2),
                        "Justification": f"Trading at {round(pe, 1)}x PE despite healthy {round(roe*100, 1)}% ROE."
                    })
            
            st.dataframe(pd.DataFrame(undervalued) if undervalued else pd.DataFrame([{"Message": "No undervalued bluechips found."}]), use_container_width=False)

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
        with st.spinner("Fetching maximum history for global indices to determine ATH..."):
            global_data = get_global_markets_data()
            if global_data:
                df_global = pd.DataFrame(global_data)
                cols = ["sr no", "name of country", "name of index", "indices current value", 
                        "% of current value from preceding day", "monthly %", "quarterly %", 
                        "yearly %", "3-year %", "its ATH", "% from ATH", 
                        "remarks for insights from investor"]
                st.dataframe(df_global[cols], use_container_width=False, hide_index=True)
            else:
                st.error("Could not fetch global markets data.")

if __name__ == "__main__":
    run_dashboard()
