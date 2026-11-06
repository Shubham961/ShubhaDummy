"""Embed data/market.json into the simulator page -> site/index.html"""
import json, os
src = open("web/src.html", encoding="utf-8").read()
lib = open("web/chart.umd.js", encoding="utf-8").read()
data = open("data/market.json", encoding="utf-8").read() if os.path.exists("data/market.json") else ""
if os.path.exists("data/news_ai.json") and data:
    d = json.loads(data); d["news_ai"] = json.load(open("data/news_ai.json", encoding="utf-8")); data = json.dumps(d, separators=(",", ":"))
json.loads(data or "{}")
out = src.replace("/*CHARTJS*/", lib, 1).replace("/*DATA*/", data.replace("</", "<\\/"), 1)
os.makedirs("site", exist_ok=True)
open("site/index.html", "w", encoding="utf-8").write(out)
print("site/index.html", len(out) // 1024, "KB")
