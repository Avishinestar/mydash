"""
Fetches FII/FPI shareholding pattern data for Nifty 500 stocks from Screener.in.
Saves top 10 stocks by highest current FII % (absolute stake) to fii_stake_data.json.
Run by GitHub Actions daily at 8:00 AM IST.
"""

import json
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

# ~130 Nifty 500 representative symbols (NSE codes)
NIFTY_500_SYMBOLS = [
    # Large Cap / Nifty 50
    "RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "BHARTIARTL", "SBIN", "INFY",
    "LICI", "ITC", "HINDUNILVR", "LT", "BAJFINANCE", "HCLTECH", "MARUTI",
    "SUNPHARMA", "ADANIENT", "KOTAKBANK", "TITAN", "ONGC", "TATAMOTORS",
    "NTPC", "AXISBANK", "POWERGRID", "M&M", "ULTRACEMCO", "ASIANPAINT",
    "BAJAJFINSV", "WIPRO", "NESTLEIND", "TECHM", "BAJAJ-AUTO",
    # Banking & Finance
    "INDUSINDBK", "BANKBARODA", "PNB", "FEDERALBNK", "IDFCFIRSTB", "CANBK",
    "UNIONBANK", "CHOLAFIN", "MUTHOOTFIN", "RECLTD", "PFC", "HDFCAMC",
    "SBICARD", "SHRIRAMFIN", "LICHSGFIN", "PNBHOUSING",
    # IT & Tech
    "LTIM", "COFORGE", "PERSISTENT", "MPHASIS", "KPITTECH", "LTTS",
    "OFSS", "TATAELXSI", "CYIENT", "BIRLASOFT", "TANLA",
    # Auto & Ancillaries
    "HEROMOTOCO", "EICHERMOT", "TVSMOTOR", "ASHOKLEY", "MOTHERSON",
    "BOSCHLTD", "APOLLOTYRE", "MRF", "BALKRISIND", "EXIDEIND", "AMARARAJA",
    # Pharma & Healthcare
    "CIPLA", "DRREDDY", "DIVISLAB", "LUPIN", "AUROPHARMA", "TORNTPHARM",
    "ZYDUSLIFE", "ALKEM", "BIOCON", "IPCA", "GLENMARK", "LAURUSLABS",
    # FMCG & Consumer
    "BRITANNIA", "TATACONSUM", "GODREJCP", "DABUR", "MARICO", "VBL",
    "COLPAL", "EMAMILTD", "RADICO",
    # Metals & Mining
    "TATASTEEL", "JSWSTEEL", "HINDALCO", "VEDL", "COALINDIA", "NMDC",
    "SAIL", "HINDZINC", "JSPL",
    # Energy & Power
    "IOC", "BPCL", "GAIL", "HINDPETRO", "TATAPOWER", "PETRONET",
    "ADANIGREEN", "ADANIPOWER", "TORNTPOWER", "NHPC", "SJVN",
    # Infra, Cement & Capital Goods
    "GRASIM", "ADANIPORTS", "AMBUJACEM", "SHREECEM", "ACC", "ABB",
    "SIEMENS", "HAVELLS", "POLYCAB", "CUMMINSIND", "THERMAX",
    # Realty
    "DLF", "MACROTECH", "GODREJPROP", "OBEROIRLTY", "PRESTIGE",
    # Chemicals & Specialty
    "PIDILITIND", "SRF", "DEEPAKNTR", "NAVINFLUOR", "UPL", "PIIND",
    "AARTIIND", "COROMANDEL",
    # Consumption & Retail
    "TRENT", "PAGEIND", "BATAINDIA", "DIXON", "DMART", "ZOMATO",
    "JUBLFOOD", "NAUKRI", "POLICYBZR",
    # Defence & Aerospace
    "HAL", "BEL", "BHEL",
    # Diversified
    "IGL", "MGL", "NAUKRI",
]

# NSE symbol → Screener.in slug where they differ
SCREENER_SYMBOL_MAP = {
    "M&M":       "M&M",       # handled via URL encoding
    "BAJAJ-AUTO": "BAJAJ-AUTO",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def make_session():
    s = requests.Session()
    s.headers.update(HEADERS)
    return s


def parse_fii_from_table(table):
    """Return (latest_fii, prev_fii) floats from a Screener shareholding table."""
    tbody = table.find("tbody")
    if not tbody:
        return None, None
    for row in tbody.find_all("tr"):
        cells = row.find_all("td")
        if not cells:
            continue
        label = cells[0].get_text(strip=True).upper()
        if "FII" in label or "FPI" in label:
            values = []
            for cell in cells[1:]:
                text = cell.get_text(strip=True).replace("%", "").replace(",", "").strip()
                try:
                    values.append(float(text))
                except ValueError:
                    pass
            if len(values) >= 2:
                return values[-1], values[-2]
    return None, None


def fetch_fii(nse_symbol):
    """Fetch FII data for one symbol; creates its own session (thread-safe)."""
    session = make_session()
    slug = SCREENER_SYMBOL_MAP.get(nse_symbol, nse_symbol)
    for variant in ["consolidated", ""]:
        path = f"{variant}/" if variant else ""
        url = f"https://www.screener.in/company/{slug}/{path}"
        try:
            resp = session.get(url, timeout=20)
            if resp.status_code == 404:
                continue
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "lxml")
            section = soup.find("section", {"id": "shareholding"})
            if not section:
                continue
            table = section.find("table")
            if not table:
                continue
            latest, prev = parse_fii_from_table(table)
            if latest is not None:
                time.sleep(0.4)   # polite delay per successful fetch
                return latest, prev
        except requests.RequestException as e:
            print(f"    {nse_symbol} [{variant or 'standalone'}] request error: {e}")
    return None, None


def main():
    print(f"Starting Nifty 500 FII fetch at {datetime.now(timezone.utc)} UTC")
    # Deduplicate while preserving order
    symbols = list(dict.fromkeys(NIFTY_500_SYMBOLS))
    results = []
    failed = []

    with ThreadPoolExecutor(max_workers=4) as executor:
        future_to_sym = {executor.submit(fetch_fii, sym): sym for sym in symbols}
        for future in as_completed(future_to_sym):
            sym = future_to_sym[future]
            try:
                latest_fii, prev_fii = future.result()
                if latest_fii is None or prev_fii is None:
                    print(f"  {sym}: FII data not found")
                    failed.append(sym)
                else:
                    change = round(latest_fii - prev_fii, 2)
                    change_str = f"+{change}" if change >= 0 else str(change)
                    print(f"  {sym}: {prev_fii:.2f}% → {latest_fii:.2f}% ({change_str}pp)")
                    results.append({
                        "sr. no.":       0,
                        "company":       sym,
                        "current FII %": round(latest_fii, 2),
                        "prev quarter %": round(prev_fii, 2),
                        "change (pp)":   change_str,
                    })
            except Exception as e:
                print(f"  {sym}: FAILED — {e}")
                failed.append(sym)

    # Top 10 by highest current FII stake (absolute %)
    results = sorted(results, key=lambda x: x["current FII %"], reverse=True)[:10]
    for i, r in enumerate(results):
        r["sr. no."] = i + 1

    output = {
        "fetched_at":     datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "source":         "screener.in",
        "universe":       f"{len(symbols)} Nifty 500 stocks",
        "data":           results,
        "failed_symbols": failed,
    }

    with open("fii_stake_data.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nDone. Top 10 by FII stake from {len(symbols) - len(failed)} successful fetches. "
          f"Failed: {len(failed)}")
    if results:
        print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
