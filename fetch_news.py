"""Collect recent Indian market headlines (title, source, link, time) from public RSS feeds."""
import calendar, html, re, time
import feedparser, requests

GN = "https://news.google.com/rss/search?hl=en-IN&gl=IN&ceid=IN:en&q="
FEEDS = [
    ("Economic Times", "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms"),
    ("Economic Times", "https://economictimes.indiatimes.com/markets/stocks/news/rssfeeds/2146842.cms"),
    ("Moneycontrol", "https://www.moneycontrol.com/rss/marketreports.xml"),
    ("Moneycontrol", "https://www.moneycontrol.com/rss/business.xml"),
    ("Moneycontrol", "https://www.moneycontrol.com/rss/buzzingstocks.xml"),
    ("Mint", "https://www.livemint.com/rss/markets"),
    ("Mint", "https://www.livemint.com/rss/companies"),
    ("Business Standard", "https://www.business-standard.com/rss/markets-106.rss"),
    ("Business Standard", "https://www.business-standard.com/rss/companies-101.rss"),
    (None, GN + "(Sensex OR Nifty OR \"stock market\") when:1d"),
    (None, GN + "(shares OR stock) (surge OR jump OR fall OR slump OR rally) NSE when:1d"),
    (None, GN + "(\"Q2 results\" OR \"quarterly results\" OR \"order win\" OR acquisition OR merger) India company when:1d"),
    (None, GN + "(RBI OR SEBI OR \"finance ministry\" OR GST OR budget) market when:1d"),
    (None, GN + "(\"Federal Reserve\" OR \"crude oil\" OR tariff OR rupee OR \"US markets\") India stocks when:1d"),
]
UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"}

def clean(t):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", t or ""))).strip()

def collect(max_age_h=36, limit=220):
    now, seen, out, stats = time.time(), set(), [], []
    for src, url in FEEDS:
        try:
            r = requests.get(url.replace(" ", "+"), headers=UA, timeout=25)
            r.raise_for_status()
            f = feedparser.parse(r.content)
        except Exception as e:
            stats.append(f"{src or 'Google News'}: error {type(e).__name__}"); continue
        n = 0
        for e in f.entries:
            title = clean(e.get("title"))
            s = src
            if src is None:
                s = clean((e.get("source") or {}).get("title")) or "Google News"
                if title.endswith(" - " + s): title = title[: -len(s) - 3]
            ts = e.get("published_parsed") or e.get("updated_parsed")
            p = calendar.timegm(ts) if ts else now
            key = re.sub(r"[^a-z0-9]", "", title.lower())[:90]
            if not title or len(title) < 25 or key in seen or now - p > max_age_h * 3600: continue
            seen.add(key); n += 1
            out.append({"t": title[:220], "s": s[:40], "u": e.get("link", ""), "p": int(p)})
        stats.append(f"{src or 'Google News'}: {n}")
    out.sort(key=lambda x: -x["p"])
    print("News feeds ->", "; ".join(stats))
    return out[:limit]

if __name__ == "__main__":
    items = collect(); print(len(items)); [print("-", i["s"], "|", i["t"]) for i in items[:15]]
