"""Download daily (2y) and 5-minute (60d) NSE prices via Yahoo Finance into data/*.json."""
import io, json, os, sys, time, datetime
import pandas as pd, requests, yfinance as yf

def read_list(path):
    if not os.path.exists(path): return []
    return [l.strip().upper() for l in open(path) if l.strip() and not l.lstrip().startswith("#")]

def universe():
    names = {}
    try:
        r = requests.get("https://niftyindices.com/IndexConstituent/ind_nifty100list.csv",
                         headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
        r.raise_for_status()
        df = pd.read_csv(io.StringIO(r.text))
        syms = [s.strip() for s in df["Symbol"]]
        names = dict(zip(syms, [n.strip() for n in df["Company Name"]]))
        if len(syms) >= 90:
            print(f"Official Nifty 100 list: {len(syms)} symbols")
            return syms, names
    except Exception as e:
        print("Could not get official list, using symbols.txt:", e)
    return read_list("symbols.txt"), names

def download(tickers, **kw):
    for attempt in range(3):
        try:
            df = yf.download(tickers, group_by="ticker", auto_adjust=False, threads=True, progress=False, **kw)
            if df is not None and len(df): return df
        except Exception as e:
            print("download error:", e)
        time.sleep(20 * (attempt + 1))
    return pd.DataFrame()

def frame(df, t):
    try:
        x = df[t] if isinstance(df.columns, pd.MultiIndex) else df
        return x.dropna(subset=["Close"])
    except KeyError:
        return pd.DataFrame()

r2 = lambda s: [round(float(v), 2) for v in s]

def main():
    syms, names = universe()
    syms = list(dict.fromkeys(syms + read_list("extra.txt")))
    os.makedirs("data", exist_ok=True)
    daily, missing = {}, []
    tick = [s + ".NS" for s in syms]
    df = download(tick, period="2y", interval="1d")
    for s, t in zip(syms, tick):
        x = frame(df, t)
        if len(x) < 60: missing.append(s); continue
        daily[s] = {"n": names.get(s, ""), "d": [d.strftime("%Y-%m-%d") for d in x.index],
                    "o": r2(x["Open"]), "h": r2(x["High"]), "l": r2(x["Low"]), "c": r2(x["Close"]),
                    "v": [int(v) if v == v else 0 for v in x["Volume"]]}
    print(f"Daily: {len(daily)} ok, missing: {missing}")
    if len(daily) < 40:
        sys.exit("Too few stocks downloaded; keeping yesterday's data.")
    intra = {}
    isyms = read_list("intraday.txt")
    idf = download([s + ".NS" for s in isyms], period="60d", interval="5m")
    for s in isyms:
        x = frame(idf, s + ".NS")
        if len(x) < 200: continue
        idx = x.index.tz_convert("Asia/Kolkata") if x.index.tz is not None else x.index
        intra[s] = {"t": [d.strftime("%Y-%m-%d %H:%M") for d in idx],
                    "o": r2(x["Open"]), "h": r2(x["High"]), "l": r2(x["Low"]), "c": r2(x["Close"])}
    print(f"Intraday: {len(intra)} ok")
    asof = max(v["d"][-1] for v in daily.values())
    meta = {"updated": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="minutes"),
            "asof": asof, "count": len(daily), "missing": missing}
    json.dump({"meta": meta, "daily": daily, "intraday": intra}, open("data/market.json", "w"), separators=(",", ":"))
    print("as of", asof)

if __name__ == "__main__":
    main()
