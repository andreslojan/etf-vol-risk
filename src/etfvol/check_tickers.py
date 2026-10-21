"""Comprueba qué tickers de Yahoo devuelven datos y resume su calidad básica."""
from pathlib import Path

import pandas as pd
import yfinance as yf

CSV = Path("config/universe.csv")
RAW = Path("data/raw")
RAW.mkdir(parents=True, exist_ok=True)


def resumen(ticker: str) -> dict:
    h = yf.Ticker(ticker).history(period="max", auto_adjust=False, actions=True)
    if h.empty:
        return {"ticker": ticker, "filas": 0}
    h.index = pd.to_datetime(h.index).tz_localize(None).normalize()
    h.to_csv(RAW / f"{ticker.replace('^', '')}.csv")
    ret = h["Close"].pct_change()
    return {
        "ticker": ticker,
        "filas": len(h),
        "primera": h.index.min().date(),
        "ultima": h.index.max().date(),
        "max_hueco_dias": int(h.index.to_series().diff().dt.days.max()),
        "vol_cero": int((h["Volume"] == 0).sum()),
        "dups_fecha": int(h.index.duplicated().sum()),
        "max_ret_abs": round(float(ret.abs().max()), 4),
        "n_dividendos": int((h["Dividends"] > 0).sum()),
    }


df = pd.read_csv(CSV)
filas = []
for t in df["ticker_yahoo"].dropna().unique():
    print("Descargando", t)
    filas.append(resumen(t))
print(pd.DataFrame(filas).to_string(index=False))