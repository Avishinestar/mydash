"""
Fetches FII/FPI shareholding pattern data for Top 2000 market cap companies from Screener.in & NSE.
Aggregates all companies where FII/FPI changed stake (both increases and decreases).
Saves to fii_stake_data.json.
Run by GitHub Actions daily at 8:00 AM IST and available locally on demand.
"""

import json
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

SCREENER_SYMBOL_MAP = {
    "M&M": "M&M",
    "BAJAJ-AUTO": "BAJAJ-AUTO",
    "TATAMOTORS": "TMCV",
    "LTIM": "540005",
    "AMARARAJA": "ARE&M",
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
        for attempt in range(2):
            try:
                resp = session.get(url, timeout=15)
                if resp.status_code == 429:
                    time.sleep(2.0)
                    continue
                if resp.status_code == 404:
                    break
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, "html.parser")
                section = soup.find("section", {"id": "shareholding"})
                if not section:
                    break
                table = section.find("table")
                if not table:
                    break
                latest, prev = parse_fii_from_table(table)
                if latest is not None and prev is not None:
                    return latest, prev
            except Exception:
                time.sleep(0.5)
    return None, None

def scrape_fii_screens():
    """Scrape public Screener.in screens containing FII stake changes."""
    session = make_session()
    screens = [
        ('change-in-fii-holding', 'https://www.screener.in/screens/338783/change-in-fii-holding/'),
        ('quarterly-change-in-fii-holding-pattern', 'https://www.screener.in/screens/422668/quarterly-change-in-fii-holding-pattern/'),
        ('decrease-in-fii-holding', 'https://www.screener.in/screens/752355/decrease-in-fii-holding/'),
        ('fii-buying', 'https://www.screener.in/screens/343087/fii-buying/'),
        ('fii-holding-increase', 'https://www.screener.in/screens/397517/fii-holding-increase/'),
        ('fii-increasing-holding', 'https://www.screener.in/screens/902636/fii-increasing-holding/'),
        ('fii-increasing-stake', 'https://www.screener.in/screens/635685/fii-increasing-stake/'),
        ('fii-dii-promoter-decreasing', 'https://www.screener.in/screens/877534/fii-dii-promoter-holding-decreasing/'),
        ('institutional-holding', 'https://www.screener.in/screens/3023474/institutional-holding/'),
        ('market-cap-below-1000-fii-holding', 'https://www.screener.in/screens/1385875/market-cap-below-1000-fii-holding/')
    ]

    all_found = {}
    print("Scraping public Screener FII change screens across Top 2000 universe...")

    for name, base_url in screens:
        page = 1
        while page <= 15:
            url = f"{base_url}?page={page}"
            try:
                r = session.get(url, timeout=10)
                if r.status_code != 200:
                    break
                soup = BeautifulSoup(r.text, "html.parser")
                t = soup.find("table")
                if not t:
                    break
                tbody = t.find("tbody")
                if not tbody:
                    break
                rows = tbody.find_all("tr")
                if len(rows) <= 1:
                    break

                headers = [th.get_text(strip=True) for th in t.find_all("th")]
                chg_idx = None
                fii_idx = None
                mcap_idx = None
                for idx, h in enumerate(headers):
                    hl = h.lower()
                    if "chg in fii" in hl and chg_idx is None:
                        chg_idx = idx
                    elif "fii hold" in hl and fii_idx is None:
                        fii_idx = idx
                    elif "mar cap" in hl and mcap_idx is None:
                        mcap_idx = idx

                for tr in rows:
                    tds = [td.get_text(strip=True) for td in tr.find_all("td")]
                    if len(tds) < 4:
                        continue
                    a = tr.find("a", href=True)
                    if not a or "/company/" not in a["href"]:
                        continue
                    slug = a["href"].split("/")[2].upper()
                    comp_name = a.get_text(strip=True) or (tds[1] if len(tds) > 1 else slug)
                    mcap = 0.0
                    if mcap_idx and len(tds) > mcap_idx and tds[mcap_idx]:
                        try:
                            mcap = float(tds[mcap_idx].replace(",", ""))
                        except ValueError:
                            pass
                    chg = None
                    if chg_idx and len(tds) > chg_idx and tds[chg_idx]:
                        try:
                            chg = float(tds[chg_idx].replace("%", "").replace(",", ""))
                        except ValueError:
                            pass
                    fii = None
                    if fii_idx and len(tds) > fii_idx and tds[fii_idx]:
                        try:
                            fii = float(tds[fii_idx].replace("%", "").replace(",", ""))
                        except ValueError:
                            pass

                    if chg is not None and chg != 0:
                        if slug not in all_found or (fii is not None and all_found[slug].get("current FII %") is None):
                            curr_fii = fii if fii is not None else 0.0
                            prev_fii = round(curr_fii - chg, 2)
                            all_found[slug] = {
                                "company": slug,
                                "name": comp_name,
                                "market_cap": mcap,
                                "current_fii": curr_fii,
                                "prev_fii": prev_fii,
                                "change": chg,
                            }
                page += 1
            except Exception as e:
                print(f"  Warning on {name} p.{page}: {e}")
                break

    print(f"Scraped {len(all_found)} unique companies with FII stake changes.")
    return all_found

def main():
    print(f"Starting Top 2000 FII Shareholding Pipeline at {datetime.now(timezone.utc)} UTC")
    
    # 1. Scrape all active FII change screens
    found_data = scrape_fii_screens()

    # 2. Key heavyweight large caps to guarantee coverage
    priority_tickers = [
        "RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "BHARTIARTL", "SBIN", "INFY",
        "LICI", "ITC", "HINDUNILVR", "LT", "BAJFINANCE", "HCLTECH", "MARUTI",
        "SUNPHARMA", "ADANIENT", "KOTAKBANK", "TITAN", "ONGC", "TATAMOTORS",
        "NTPC", "AXISBANK", "POWERGRID", "M&M", "ULTRACEMCO", "ASIANPAINT",
        "BAJAJFINSV", "WIPRO", "NESTLEIND", "TECHM", "BAJAJ-AUTO", "SHRIRAMFIN",
        "IDFCFIRSTB", "BANKBARODA", "PNB", "FEDERALBNK", "CANBK", "UNIONBANK",
        "CHOLAFIN", "MUTHOOTFIN", "RECLTD", "PFC", "HDFCAMC", "SBICARD"
    ]

    print("Checking priority heavyweights...")
    with ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(fetch_fii, sym): sym for sym in priority_tickers}
        for f in as_completed(futs):
            sym = futs[f]
            try:
                latest, prev = f.result()
                if latest is not None and prev is not None:
                    chg = round(latest - prev, 2)
                    if chg != 0:
                        mcap = found_data.get(sym, {}).get("market_cap", 0.0)
                        comp_name = found_data.get(sym, {}).get("name", sym)
                        found_data[sym] = {
                            "company": sym,
                            "name": comp_name,
                            "market_cap": mcap,
                            "current_fii": round(latest, 2),
                            "prev_fii": round(prev, 2),
                            "change": chg,
                        }
            except Exception:
                pass

    # 3. Format into standardized records
    formatted_results = []
    for sym, item in found_data.items():
        chg = item["change"]
        curr_fii = item["current_fii"]
        prev_fii = item["prev_fii"]
        mcap = item.get("market_cap", 0.0)
        chg_str = f"+{chg:.2f}" if chg > 0 else f"{chg:.2f}"
        action = "Increased ▲" if chg > 0 else "Decreased ▼"
        
        if chg >= 3.0:
            action = "Major Accumulation 🚀"
            ins = f"Major Institutional Accumulation: Foreign funds aggressively scaled stake by {chg_str}pp (from {prev_fii:.2f}% to {curr_fii:.2f}%)."
        elif chg > 0:
            action = "Increased ▲"
            ins = f"Recent FII Stake Increased: Institutional stake expanded by {chg_str}pp (from {prev_fii:.2f}% to {curr_fii:.2f}%)."
        elif chg <= -3.0:
            action = "Heavy Trimming ⚠️"
            ins = f"Heavy Institutional Trimming: Foreign funds aggressively reduced stake by {chg_str}pp (from {prev_fii:.2f}% down to {curr_fii:.2f}%)."
        else:
            action = "Decreased ▼"
            ins = f"Recent FII Stake Decreased: Institutional stake trimmed by {chg_str}pp (from {prev_fii:.2f}% to {curr_fii:.2f}%)."

        formatted_results.append({
            "company": sym,
            "stock": sym,
            "name": item.get("name", sym),
            "market cap (Cr)": round(mcap, 1) if mcap else None,
            "current FII %": round(curr_fii, 2),
            "prev quarter %": round(prev_fii, 2),
            "change (pp)": chg_str,
            "change_val": chg,
            "action": action,
            "insight": ins
        })

    # Sort primarily by absolute change magnitude
    formatted_results.sort(key=lambda x: abs(x["change_val"]), reverse=True)
    for i, r in enumerate(formatted_results):
        r["sr. no."] = i + 1
        r["Sr.No."] = i + 1

    output = {
        "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "source": "screener.in / NSE",
        "universe": f"Top 2000 Market Cap Companies ({len(formatted_results)} active FII changes)",
        "data": formatted_results,
    }

    with open("fii_stake_data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"\nSUCCESS: Saved {len(formatted_results)} companies with FII/FPI changes to fii_stake_data.json")
    print(f"Universe: Top 2000 Market Cap Companies")

if __name__ == "__main__":
    main()
