# Stock Scenario Lab: daily NSE prices

Every weekday at about 4:30 PM IST, GitHub Actions downloads 2 years of daily prices for the Nifty 100
(plus anything in `extra.txt`) and 60 days of 5-minute candles for the stocks in `intraday.txt`.
It builds the simulator page with the data embedded and saves it on the `data` branch.
A scheduled Claude task then republishes the Stock Scenario Lab artifact from that branch.

- Add stocks: put NSE symbols in `extra.txt` (one per line).
- Run now: Actions tab → "Fetch NSE prices" → Run workflow.

Data comes from Yahoo Finance and is for education only. It isn't investment advice.
