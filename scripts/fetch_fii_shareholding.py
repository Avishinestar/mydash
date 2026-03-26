"""
Fetches FII/FPI shareholding pattern data for NIFTY 50 stocks from NSE India.
Compares latest quarter vs previous quarter and saves top 10 increases to fii_stake_data.json.
Run by GitHub Actions daily at 8:30 AM IST.
"""

import json
import requests
import time
from datetime import datetime

NIFTY_50_SYMBOLS = [
    "RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "BHARTIARTL",
    "SBIN", "INFY", "LICI", "ITC", "HINDUNILVR", "LT",
    "BAJFINANCE", "HCLTECH", "MARUTI", "SUNPHARMA", "ADANIENT",
    "KOTAKBANK", "TITAN", "ONGC", "TATAMOTORS", "NTPC",
    "AXISBANK", "POWERGRID", "M&M", "ULTRACEMCO", "ASIANPAINT",
    "BAJAJFINSV", "WIPRO", "NESTLEIND", "TECHM", "BAJAJ-AUTO"
]

def get_session():
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    try:
        session.get("https://www.nseindia.com", timeout=15, headers=headers)
        time.sleep(2)
    except Exception as e:
        print(f"Warning: Could not load NSE homepage: {e}")
    return session

def extract_fii(record):
    for key in ["fiiFpiHolding", "totalForeignPortfolioInvestors", "fii", "FII", "fiiHolding"]:
        if key in record:
            try:
                return float(str(record[key]).replace("%", "").strip())
            except Exception:
                pass
    return None

def fetch_shareholding(session, symbol):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        "Referer": "https://www.nseindia.com/",
        "Accept": "application/json",
        "X-Requested-With": "XMLHttpRequest",
    }
    url = f"https://www.nseindia.com/api/corporate-shareholding-patterns?index=equities&symbol={symbol}"
    resp = session.get(url, timeout=15, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    return data if isinstance(data, list) else data.get("data", [])

def main():
    print(f"Starting FII shareholding fetch at {datetime.utcnow()} UTC")
    session = get_session()
    results = []
    failed = []

    for symbol in NIFTY_50_SYMBOLS:
        try:
            records = fetch_shareholding(session, symbol)
            if len(records) < 2:
                print(f"  {symbol}: not enough quarters ({len(records)})")
                continue

            latest_fii = extract_fii(records[0])
            prev_fii   = extract_fii(records[1])

            if latest_fii is None or prev_fii is None:
                print(f"  {symbol}: FII field not found. Keys: {list(records[0].keys())}")
                continue

            change = round(latest_fii - prev_fii, 2)
            print(f"  {symbol}: {prev_fii}% -> {latest_fii}% (change: {change:+.2f}pp)")

            if change > 0:
                results.append({
                    "sr. no.": 0,
                    "company": symbol,
                    "current FII %": round(latest_fii, 2),
                    "prev quarter %": round(prev_fii, 2),
                    "change (pp)": f"+{change}",
                })
            time.sleep(0.5)  # be polite to NSE
        except Exception as e:
            print(f"  {symbol}: FAILED — {e}")
            failed.append(symbol)

    results = sorted(results, key=lambda x: float(str(x["change (pp)"]).replace("+", "")), reverse=True)[:10]
    for i, r in enumerate(results):
        r["sr. no."] = i + 1

    output = {
        "fetched_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
        "data": results,
        "failed_symbols": failed,
    }

    with open("fii_stake_data.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nDone. {len(results)} stocks with FII increase. Failed: {len(failed)}")
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
