"""
Fetches FII/FPI shareholding pattern data for NIFTY 50 stocks from Screener.in.
Compares latest quarter vs previous quarter and saves top 10 increases to fii_stake_data.json.
Run by GitHub Actions daily at 8:00 AM IST.
"""

import json
import requests
import time
from bs4 import BeautifulSoup
from datetime import datetime, timezone

NIFTY_50_SYMBOLS = [
    "RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "BHARTIARTL",
    "SBIN", "INFY", "LICI", "ITC", "HINDUNILVR", "LT",
    "BAJFINANCE", "HCLTECH", "MARUTI", "SUNPHARMA", "ADANIENT",
    "KOTAKBANK", "TITAN", "ONGC", "TATAMOTORS", "NTPC",
    "AXISBANK", "POWERGRID", "M&M", "ULTRACEMCO", "ASIANPAINT",
    "BAJAJFINSV", "WIPRO", "NESTLEIND", "TECHM", "BAJAJ-AUTO",
]

# NSE symbol → Screener.in slug where they differ
SCREENER_SYMBOL_MAP = {
    "TATAMOTORS": "TMCV",  # Screener uses BSE code for Tata Motors
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
    session = requests.Session()
    session.headers.update(HEADERS)
    return session


def parse_fii_from_table(table):
    """Return (latest_fii, prev_fii) floats from a Screener shareholding table, or (None, None)."""
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


def fetch_fii(session, nse_symbol):
    slug = SCREENER_SYMBOL_MAP.get(nse_symbol, nse_symbol)

    # Try consolidated first, then standalone
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
                return latest, prev

        except requests.RequestException as e:
            print(f"    [{variant or 'standalone'}] request error: {e}")

    return None, None


def main():
    print(f"Starting FII shareholding fetch at {datetime.now(timezone.utc)} UTC")
    session = make_session()
    results = []
    failed = []

    for symbol in NIFTY_50_SYMBOLS:
        try:
            latest_fii, prev_fii = fetch_fii(session, symbol)

            if latest_fii is None or prev_fii is None:
                print(f"  {symbol}: FII data not found")
                failed.append(symbol)
            else:
                change = round(latest_fii - prev_fii, 2)
                print(f"  {symbol}: {prev_fii:.2f}% -> {latest_fii:.2f}% ({change:+.2f}pp)")
                if change > 0:
                    results.append({
                        "sr. no.": 0,
                        "company": symbol,
                        "current FII %": round(latest_fii, 2),
                        "prev quarter %": round(prev_fii, 2),
                        "change (pp)": f"+{change}",
                    })

        except Exception as e:
            print(f"  {symbol}: FAILED — {e}")
            failed.append(symbol)

        time.sleep(1.5)  # be polite to Screener.in

    results = sorted(
        results,
        key=lambda x: float(str(x["change (pp)"]).lstrip("+")),
        reverse=True,
    )[:10]

    for i, r in enumerate(results):
        r["sr. no."] = i + 1

    output = {
        "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "source": "screener.in",
        "data": results,
        "failed_symbols": failed,
    }

    with open("fii_stake_data.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nDone. {len(results)} stocks with FII increase. Failed: {len(failed)}")
    if results:
        print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
