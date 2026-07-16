import json
import yfinance as yf
from nsepython import nse_eq_symbols
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_mcap(ticker):
    try:
        info = yf.Ticker(ticker).fast_info
        mcap = info.get('marketCap', 0)
        if mcap is None:
            mcap = 0
        return {"ticker": ticker, "mcap": mcap}
    except Exception:
        return {"ticker": ticker, "mcap": 0}

def main():
    print("Fetching active NSE equities...")
    try:
        symbols = nse_eq_symbols()
        if not symbols:
            print("No symbols fetched.")
            return
    except Exception as e:
        print(f"Error fetching symbols: {e}")
        return

    tickers = [s.strip() + ".NS" for s in symbols if s.strip()]
    print(f"Total tickers to process: {len(tickers)}")
    
    results = []
    print("Fetching market caps...")
    with ThreadPoolExecutor(max_workers=50) as executor:
        futs = [executor.submit(fetch_mcap, t) for t in tickers]
        for i, f in enumerate(as_completed(futs)):
            results.append(f.result())
            if (i+1) % 100 == 0:
                print(f"Processed {i+1}/{len(tickers)}")
                
    results.sort(key=lambda x: x["mcap"], reverse=True)
    top_2000 = [x["ticker"] for x in results[:2000]]
    
    with open("top_2000_tickers.json", "w") as f:
        json.dump(top_2000, f)
        
    print(f"Saved {len(top_2000)} tickers to top_2000_tickers.json")

if __name__ == "__main__":
    main()
