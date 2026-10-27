"""Diagnóstico v5: IWDP.AS vs IWDP.MI y dividendos de VUSA.AS vs VUSA.DE."""
from pathlib import Path

import pandas as pd

RAW = Path("data/raw")
INICIO = "2014-10-06"


def cargar(t):
    return pd.read_csv(RAW / f"{t}.csv", index_col=0, parse_dates=True).sort_index().loc[INICIO:]


def resumen(t):
    h = cargar(t)
    r = h["Adj Close"].pct_change()
    print(
        f"{t}: filas {len(h)} | vol0 {int((h['Volume'] == 0).sum())} | "
        f"cierres repetidos {int((h['Close'].diff() == 0).sum())} | "
        f"max|ret adj| {r.abs().max():.4f} | primera {h.index.min().date()}"
    )


def par(a, b):
    ha, hb = cargar(a), cargar(b)
    cl = pd.concat({a: ha["Close"], b: hb["Close"]}, axis=1, join="inner", sort=True).dropna()
    aj = pd.concat({a: ha["Adj Close"], b: hb["Adj Close"]}, axis=1, join="inner", sort=True).dropna()
    rc, ra = cl.pct_change().dropna(), aj.pct_change().dropna()
    d_c, d_a = rc[a] - rc[b], ra[a] - ra[b]
    ex = ha.index[ha["Dividends"] > 0].union(hb.index[hb["Dividends"] > 0]).intersection(ra.index)
    print(f"\n{a} vs {b}: {len(ra)} días | corr adj {ra[a].corr(ra[b]):.4f} | n ex-div {len(ex)}")
    print(
        f"dif abs media | todas (adj): {d_a.abs().mean():.5f} | "
        f"ex-div (adj): {d_a.reindex(ex).abs().mean():.5f} | ex-div (close): {d_c.reindex(ex).abs().mean():.5f}"
    )
    print("Top 6 |dif adj| en fechas ex-div:")
    print(d_a.reindex(ex).abs().nlargest(6).round(4).to_string())
    print("Top 6 |dif adj| en todas las fechas:")
    print(d_a.abs().nlargest(6).round(4).to_string())


for t in ("IWDP.AS", "IWDP.MI", "VUSA.AS", "VUSA.DE"):
    resumen(t)
par("IWDP.AS", "IWDP.MI")
par("VUSA.AS", "VUSA.DE")