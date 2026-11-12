# CEO Key-Person Exposure Index (KPEI)

> How much of a company's stock price walks out the door if the CEO does?

A tongue-in-cheek but honest attempt to score key-person risk, inspired by
Nvidia's November 2026 leadership crisis.

## How it works

KPEI (0-10) =
- 50% Key-person impact: founder status, visibility, valuation premium,
  governance/control, succession depth (scored by hand, 1-10)
- 30% Volatility: beta (live, via yfinance)
- 15% Valuation: forward P/E vs. the S&P 500
- 5% Size: market cap, inverted

It also computes the abnormal return (stock minus sector ETF) around an
event, so sector-wide moves aren't blamed on the CEO.

## Run it

    pip install -r requirements.txt
    python kpei.py

## Caveats (seriously)

- Not investment advice. This is a meme repo and a learning project.
- The impact scores are subjective and were set with hindsight.
- It measures how exposed a stock is to its CEO, not how likely a scandal is.
  It makes no claims about any individual's private conduct.
- n = 1 backtest. Statistically, this proves nothing.

PRs with better weights, more tickers or an actual event study are welcome.