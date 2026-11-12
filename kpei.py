"""
CEO Key-Person Exposure Index (KPEI)
A meme / research project. Not investment advice.
"""
from dataclasses import dataclass, field
import math
import sys

import yfinance as yf

IMPACT_WEIGHTS = {
    "founder": 0.25, "visibility": 0.20, "premium": 0.10,
    "control": 0.30, "succession": 0.15,
}
KPEI_WEIGHTS = {"impact": 0.50, "volatility": 0.30, "valuation": 0.15, "size": 0.05}
BENCHMARK_PE = 18.7  # S&P 500 forward P/E, update periodically


@dataclass
class Company:
    ticker: str
    impact: dict
    sector_etf: str = "SOXX"
    overrides: dict = field(default_factory=dict)
    data: dict = field(default_factory=dict)


def fetch(c):
    try:
        info = yf.Ticker(c.ticker).info
        c.data = {
            "forward_pe": info.get("forwardPE"),
            "beta": info.get("beta"),
            "market_cap": info.get("marketCap"),
        }
    except Exception as e:
        print(f"[warn] {c.ticker}: live data failed ({e})", file=sys.stderr)
        c.data = {}
    c.data.update(c.overrides)


def clamp(x, lo=0.0, hi=10.0):
    return max(lo, min(hi, x))


def impact_score(c):
    return sum(c.impact[k] * w for k, w in IMPACT_WEIGHTS.items())


def valuation_score(c):
    pe = c.data.get("forward_pe")
    if not pe or pe <= 0:
        return 5.0
    return clamp((pe / BENCHMARK_PE - 0.5) * 5)


def volatility_score(c):
    beta = c.data.get("beta")
    if beta is None:
        return 5.0
    return clamp((beta - 0.5) / 2.0 * 10)


def size_score(c):
    cap = c.data.get("market_cap")
    if not cap:
        return 5.0
    lo, hi = math.log10(10e9), math.log10(5e12)
    return clamp((hi - math.log10(cap)) / (hi - lo) * 10)


def kpei(c):
    p = {"impact": impact_score(c), "valuation": valuation_score(c),
         "volatility": volatility_score(c), "size": size_score(c)}
    p["KPEI"] = sum(p[k] * w for k, w in KPEI_WEIGHTS.items())
    return p


def abnormal_return(ticker, etf, start, end):
    px = yf.download([ticker, etf], start=start, end=end,
                     auto_adjust=True, progress=False)["Close"]
    rets = px.iloc[-1] / px.iloc[0] - 1
    return rets[ticker] - rets[etf]


COMPANIES = [
    Company("NVDA",
            {"founder": 10, "visibility": 9, "premium": 7, "control": 8, "succession": 8},
            overrides={"forward_pe": 17.9, "market_cap": 5.85e12}),
    Company("MSTR",
            {"founder": 10, "visibility": 10, "premium": 10, "control": 9, "succession": 7},
            sector_etf="IBIT"),
    Company("AMD",
            {"founder": 2, "visibility": 7, "premium": 8, "control": 3, "succession": 6}),
    Company("GOOGL",
            {"founder": 2, "visibility": 5, "premium": 3, "control": 4, "succession": 3},
            sector_etf="XLC"),
    Company("AAPL",
            {"founder": 1, "visibility": 3, "premium": 3, "control": 2, "succession": 2},
            sector_etf="XLK"),
]


def main():
    for c in COMPANIES:
        fetch(c)

    print(f"{'Ticker':<8}{'Impact':>8}{'Val':>6}{'Vol':>6}{'Size':>6}{'KPEI':>7}")
    for c in sorted(COMPANIES, key=lambda c: kpei(c)["KPEI"], reverse=True):
        r = kpei(c)
        print(f"{c.ticker:<8}{r['impact']:>8.1f}{r['valuation']:>6.1f}"
              f"{r['volatility']:>6.1f}{r['size']:>6.1f}{r['KPEI']:>7.1f}")

    try:
        ar = abnormal_return("NVDA", "SOXX", "2026-11-10", "2026-11-13")
        print(f"\nNVDA vs SOXX, scandal window: {ar:+.1%}")
    except Exception as e:
        print(f"[warn] abnormal return failed ({e})", file=sys.stderr)


if __name__ == "__main__":
    main()