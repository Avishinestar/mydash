import yfinance as yf
import pandas as pd
import ta
import streamlit as st
import plotly.express as px
import requests

# ================= CONFIG =================
STOCKS = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS"]

SECTORS = {
    "NIFTY": "^NSEI",
    "BANK": "^NSEBANK",
    "IT": "^CNXIT",
    "AUTO": "^CNXAUTO",
    "FMCG": "^CNXFMCG",
    "PHARMA": "^CNXPHARMA"
}

STOCK_SECTOR = {
    "RELIANCE.NS": "ENERGY",
    "TCS.NS": "IT",
    "INFY.NS": "IT",
    "HDFCBANK.NS": "BANK",
    "ICICIBANK.NS": "BANK",
    "SBIN.NS": "BANK"
}

BOT_TOKEN = ""
CHAT_ID = ""

# ================= DATA FUNCTIONS =================
def get_data(ticker):
    return yf.download(ticker, period="6mo", interval="1d")

def add_indicators(df):
    df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()
    df['200DMA'] = df['Close'].rolling(200).mean()
    df['20HIGH'] = df['High'].rolling(20).max()
    return df

# ================= LOGIC =================
def detect_breakout(df):
    price = df['Close'].iloc[-1]
    high = df['20HIGH'].iloc[-1]

    if price > high:
        return "Confirmed Breakout"
    elif price > high * 0.98:
        return "Near Breakout"
    return "No Breakout"

def relative_strength(stock_df, nifty_df):
    stock_ret = stock_df['Close'].pct_change().fillna(0)
    nifty_ret = nifty_df['Close'].pct_change().fillna(0)

    rs = (1 + stock_ret).cumprod() / (1 + nifty_ret).cumprod()
    return rs.iloc[-1]

def score_stock(rsi, breakout, rs):
    score = 0

    if breakout == "Confirmed Breakout":
        score += 3
    elif breakout == "Near Breakout":
        score += 2

    if 40 < rsi < 60:
        score += 2
    elif rsi < 40:
        score += 1

    if rs > 1:
        score += 2

    return score

def ai_reason(score, breakout, rs, rsi):
    reasons = []

    if score >= 4:
        reasons.append("High conviction")

    if breakout == "Confirmed Breakout":
        reasons.append("Breakout")

    if rs > 1:
        reasons.append("Outperforming market")

    if rsi < 40:
        reasons.append("Oversold")

    return " | ".join(reasons)

# ================= SECTOR =================
def get_sector_data():
    data = {}

    for name, ticker in SECTORS.items():
        df = yf.download(ticker, period="1y")

        weekly = (df['Close'].iloc[-1] / df['Close'].iloc[-5]) - 1
        monthly = (df['Close'].iloc[-1] / df['Close'].iloc[-21]) - 1
        yearly = (df['Close'].iloc[-1] / df['Close'].iloc[0]) - 1

        data[name] = {
            "weekly": weekly * 100,
            "monthly": monthly * 100,
            "yearly": yearly * 100
        }

    return data

def sector_alpha(data):
    nifty = data["NIFTY"]
    result = []

    for s, v in data.items():
        if s == "NIFTY":
            continue

        result.append({
            "sector": s,
            "weekly_alpha": v["weekly"] - nifty["weekly"],
            "monthly_alpha": v["monthly"] - nifty["monthly"],
            "yearly_alpha": v["yearly"] - nifty["yearly"]
        })

    return result

# ================= FII/DII =================
def get_fii_dii():
    try:
        tables = pd.read_html("https://www.moneycontrol.com/stocks/marketstats/fii_dii_activity/index.php")
        df = tables[0]
        latest = df.iloc[0]
        return latest[3], latest[6]
    except:
        return None, None

# ================= TELEGRAM =================
def send_telegram(msg):
    if BOT_TOKEN == "":
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.get(url, params={"chat_id": CHAT_ID, "text": msg})

# ================= ANALYSIS =================
def analyze():
    results = []
    nifty = get_data("^NSEI")

    for stock in STOCKS:
        try:
            df = get_data(stock)
            df = add_indicators(df)

            rsi = df['RSI'].iloc[-1]
            breakout = detect_breakout(df)
            price = df['Close'].iloc[-1]
            rs = relative_strength(df, nifty)

            score = score_stock(rsi, breakout, rs)
            reason = ai_reason(score, breakout, rs, rsi)

            results.append({
                "Stock": stock,
                "Price": round(price, 2),
                "RSI": round(rsi, 2),
                "RS": round(rs, 2),
                "Score": score,
                "Breakout": breakout,
                "Reason": reason
            })
        except:
            pass

    return sorted(results, key=lambda x: x["Score"], reverse=True)

# ================= STREAMLIT UI =================
st.title("📊 PRO MARKET DASHBOARD")

@st.cache_data(ttl=300)
def get_nifty_sensex():
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
        get_nifty_sensex.clear()
        
    return res

@st.cache_data(ttl=3600)
def get_fiidii():
    try:
        from nsepython import nse_fiidii
        df = nse_fiidii()
        dii_net = float(df[df["category"] == "DII"]["netValue"].iloc[0])
        fii_net = float(df[df["category"] == "FII/FPI"]["netValue"].iloc[0])
        return {"FII": fii_net, "DII": dii_net}
    except Exception:
        get_fiidii.clear()
        return {"FII": None, "DII": None}

levels = get_nifty_sensex()
fiidii = get_fiidii()
if fiidii.get("FII") is not None:
    fii_val = fiidii["FII"]
    fii_text = f"FII Inflow: ₹{fii_val}Cr" if fii_val >= 0 else f"FII Outflow: ₹{abs(fii_val)}Cr"
else:
    fii_text = "FII: N/A"

if fiidii.get("DII") is not None:
    dii_val = fiidii["DII"]
    dii_text = f"DII Inflow: ₹{dii_val}Cr" if dii_val >= 0 else f"DII Outflow: ₹{abs(dii_val)}Cr"
else:
    dii_text = "DII: N/A"

st.markdown(
    f"""
    <div style="background-color: red; padding: 10px; border-radius: 5px; color: white; font-weight: bold; margin-bottom: 20px; text-align: center; font-size: 18px;">
        NIFTY 50: {levels.get('NIFTY 50', 'N/A')} (RSI: {levels.get('NIFTY RSI', 'N/A')} | ATH Dist: {levels.get('NIFTY % to ATH', 'N/A')}) &nbsp;|&nbsp; SENSEX: {levels.get('SENSEX', 'N/A')} &nbsp;|&nbsp; INDIA VIX: {levels.get('INDIA VIX', 'N/A')} &nbsp;|&nbsp; {fii_text} &nbsp;|&nbsp; {dii_text}
    </div>
    """, 
    unsafe_allow_html=True
)

if st.button("Run Analysis"):
    results = analyze()
    df = pd.DataFrame(results)

    st.subheader("Top Stocks")
    st.dataframe(df)

    st.subheader("Top Opportunities")
    for r in results[:3]:
        st.write(r)

    # Sector
    sector_data = get_sector_data()
    alpha = sector_alpha(sector_data)

    st.subheader("Sector Heatmap")
    df_alpha = pd.DataFrame(alpha)

    fig = px.imshow(
        df_alpha[["weekly_alpha", "monthly_alpha", "yearly_alpha"]],
        labels=dict(x="Timeframe", y="Sector"),
        x=["Weekly", "Monthly", "Yearly"],
        y=df_alpha["sector"],
        text_auto=True
    )

    st.plotly_chart(fig)

    # FII DII
    fii, dii = get_fii_dii()
    st.subheader("Institutional Flow")
    st.write(f"FII: {fii} | DII: {dii}")

    # Telegram
    msg = "Top Stocks:\n"
    for r in results[:3]:
        msg += f"{r['Stock']} | Score {r['Score']}\n"

    send_telegram(msg)
    