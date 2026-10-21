"""Auditoría de los CSV crudos descargados (data/raw)."""
from pathlib import Path

import pandas as pd
import yfinance as yf

RAW = Path("data/raw")


def cargar(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, index_col=0, parse_dates=True).sort_index()


series = {p.stem: cargar(p) for p in sorted(RAW.glob("*.csv"))}

for t, h in series.items():
    print(f"\n=== {t} ===")
    ret = h["Close"].pct_change()
    z = h.index[h["Volume"] == 0]
    print("Volumen cero por año:", pd.Series(z.year).value_counts().sort_index().to_dict() or "ninguno")
    top = ret.abs().nlargest(5)
    print("Top 5 |ret|:", [(d.date().isoformat(), round(float(ret[d]), 4)) for d in top.index])
    dif = h.index.to_series().diff().dt.days
    huecos = dif[dif > 7]
    print("Huecos > 7 días:", [(d.date().isoformat(), int(v)) for d, v in huecos.items()] or "ninguno")
    print("Cierres repetidos:", int((h["Close"].diff() == 0).sum()))


def comparar(a, b, desde=None):
    c = pd.concat({k: series[k]["Close"] for k in (a, b)}, axis=1, join="inner", sort=True).dropna()
    if desde:
        c = c.loc[desde:]
    r = c.pct_change().dropna()
    d = (r[a] - r[b]).abs()
    print(
        f"\n{a} vs {b} (desde {desde or 'inicio'}): {len(r)} días | corr {r[a].corr(r[b]):.4f} | "
        f"dif abs media {d.mean():.5f} | máx {d.max():.4f} el {d.idxmax().date()}"
    )


def ver_fechas(a, b, fechas):
    c = pd.concat({k: series[k]["Close"] for k in (a, b)}, axis=1, join="inner", sort=True).dropna()
    r = c.pct_change()
    print(r.loc[r.index.intersection(pd.to_datetime(fechas))].round(4))


comparar("VUSA.AS", "VUSA.DE")
comparar("LYXIB.MC", "IBEX")
comparar("LYXIB.MC", "IBEX", desde="2014-01-01")
ver_fechas("LYXIB.MC", "IBEX", ["2008-10-13", "2008-10-14", "2020-03-12", "2020-03-13", "2016-06-24", "2010-05-10"])
ver_fechas("VUSA.AS", "VUSA.DE", ["2018-12-24", "2018-12-27"])

for t in ("LYXIB.MC", "EUNH.DE"):
    div = series[t]["Dividends"]
    div = div[div > 0]
    print(t, "dividendos por año:", div.groupby(div.index.year).size().to_dict())


# --- diagnósticos adicionales ---
INICIO = "2014-01-01"
cero = {t: set(h.loc[INICIO:].index[h.loc[INICIO:, "Volume"] == 0]) for t, h in series.items() if "." in t}
todas = pd.Series([d for s in cero.values() for d in s]).value_counts()
print("\nFechas (desde 2014) con volumen cero en >=3 tickers:")
print(todas[todas >= 3].sort_index().to_string())

print("\nPrimer dividendo por ticker:")
for t, h in series.items():
    d = h.index[h["Dividends"] > 0]
    print(t, d.min().date() if len(d) else "ninguno")

c = pd.concat({k: series[k]["Close"] for k in ("LYXIB.MC", "IBEX")}, axis=1, join="inner", sort=True).dropna().loc[INICIO:]
r = c.pct_change().dropna()
print("\nLYXIB.MC vs IBEX desde 2014:")
print("corr mismo día:", round(r["LYXIB.MC"].corr(r["IBEX"]), 4))
print("corr ETF(t) con IBEX(t-1):", round(r["LYXIB.MC"].corr(r["IBEX"].shift(1)), 4))
print("corr ETF(t-1) con IBEX(t):", round(r["LYXIB.MC"].shift(1).corr(r["IBEX"]), 4))
dif = (r["LYXIB.MC"] - r["IBEX"]).abs()
print("días con |dif| > 1%:", int((dif > 0.01).sum()), "de", len(dif))
print(dif.nlargest(8).round(4).to_string())

if "AMES.DE" in series:
    comparar("AMES.DE", "IBEX", desde=INICIO)
    comparar("AMES.DE", "LYXIB.MC", desde=INICIO)


# --- diagnóstico v3 ---
INICIO = "2014-10-06"
UNIV = ["VUSA.AS", "LYXIB.MC", "IWDA.AS", "EXSA.DE", "IS3N.DE", "CNDX.AS", "EUNH.DE", "IEAC.AS", "IWDP.MI", "4GLD.DE"]

d = pd.concat(
    [series["LYXIB.MC"][["Close", "Adj Close", "Volume", "Dividends"]].add_prefix("etf_"),
     series["IBEX"][["Close"]].add_prefix("idx_")],
    axis=1, join="inner", sort=True,
).dropna().loc[INICIO:]
r = pd.DataFrame({
    "etf_close": d["etf_Close"].pct_change(),
    "etf_adj": d["etf_Adj Close"].pct_change(),
    "idx": d["idx_Close"].pct_change(),
}).dropna()
r["dif_close"] = r["etf_close"] - r["idx"]
r["dif_adj"] = r["etf_adj"] - r["idx"]
r["dif_adj_sig"] = r["dif_adj"].shift(-1)
r["div"] = d["etf_Dividends"].reindex(r.index)
r["vol"] = d["etf_Volume"].reindex(r.index)

print("\ncorr Close:", round(r["etf_close"].corr(r["idx"]), 4), "| corr Adj Close:", round(r["etf_adj"].corr(r["idx"]), 4))
peores = r["dif_adj"].abs().nlargest(12).index.sort_values()
print("\nPeores 12 días (Adj Close):")
print(r.loc[peores, ["etf_close", "etf_adj", "idx", "dif_adj", "dif_adj_sig", "div", "vol"]].round(4).to_string())
resto = r.drop(peores)
print("corr sin esos 12 días:", round(resto["etf_adj"].corr(resto["idx"]), 4))
print("días |dif_adj| > 1%:", int((r["dif_adj"].abs() > 0.01).sum()), "de", len(r))
print("\nDías ex-dividendo:")
print(r.loc[r["div"] > 0, ["etf_close", "etf_adj", "idx", "dif_close", "dif_adj", "div"]].round(4).to_string())

print("\nVolumen cero en varios tickers:")
for f in pd.to_datetime(["2017-10-03", "2017-10-31", "2018-05-21", "2023-12-04", "2023-12-05", "2023-12-06"]):
    fila = {}
    for t, h in series.items():
        if "." in t and f in h.index and h.loc[f, "Volume"] == 0:
            i = h.index.get_loc(f)
            fila[t] = round(float(h["Close"].iloc[i] / h["Close"].iloc[i - 1] - 1), 4)
    print(f.date(), fila)

print("\nEstadísticas desde", INICIO)
comun = series[UNIV[0]].loc[INICIO:].index
for t in UNIV:
    h = series[t].loc[INICIO:]
    comun = comun.intersection(h.index)
    rr = h["Adj Close"].pct_change()
    print(t, "filas", len(h), "| vol0", int((h["Volume"] == 0).sum()),
          "| cierres repetidos", int((h["Close"].diff() == 0).sum()),
          "| max|ret adj|", round(float(rr.abs().max()), 4))
print("Fechas comunes:", len(comun), comun.min().date(), comun.max().date())


