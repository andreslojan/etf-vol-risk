"""Diagnóstico v6: IWDP, pares Dist vs Acc y calendario común con IWDP.AS."""
from pathlib import Path

import pandas as pd
import yfinance as yf

RAW = Path("data/raw")
INICIO = "2014-10-06"


def cargar(t):
    return pd.read_csv(RAW / f"{t}.csv", index_col=0, parse_dates=True).sort_index()


# 1) IWDP.AS: fecha del movimiento extremo y comparación con IWDP.MI
a, m = cargar("IWDP.AS"), cargar("IWDP.MI")
rc = a["Close"].pct_change()
print("IWDP.AS top 5 |ret Close| (todo el histórico):")
print(rc.abs().nlargest(5).round(4).to_string())
print("Máx |ret Close| desde", INICIO, ":", round(float(rc.loc[INICIO:].abs().max()), 4))

x = pd.concat({"AS": a["Close"], "MI": m["Close"]}, axis=1, join="inner", sort=True).dropna()
v = pd.concat({"vol_AS": a["Volume"], "vol_MI": m["Volume"]}, axis=1, join="inner", sort=True).reindex(x.index)
f = x.index[(x.index >= "2022-09-19") & (x.index <= "2022-09-22")]
print("\nIWDP.AS vs IWDP.MI, 19-22 sep 2022:")
print(pd.concat([x.loc[f], x.pct_change().loc[f].add_prefix("ret_"), v.loc[f]], axis=1).round(4).to_string())


# 2) Pares Dist vs Acc: la diferencia debe ser ≈ -yield el día ex-dividendo
def par(dist, acc):
    try:
        d, c = cargar(dist), cargar(acc)
    except FileNotFoundError:
        print(f"\n{dist} / {acc}: falta algún CSV")
        return
    px = pd.concat({"dist": d["Close"], "acc": c["Close"]}, axis=1, join="inner", sort=True).dropna()
    r = px.pct_change().dropna()
    dif = r["dist"] - r["acc"]
    div, prev = d["Dividends"], d["Close"].shift(1)
    fechas = [t for t in r.index if t in div.index and div.loc[t] > 0]
    sin = dif.drop(fechas)
    print(f"\n{dist} (Dist) vs {acc} (Acc): {len(r)} días desde {r.index.min().date()}")
    print("días sin dividendo: dif media", round(float(sin.mean()), 5), "| desv.", round(float(sin.std()), 5))
    cuenta = {"t": 0, "t+1": 0, "ninguna": 0}
    filas = []
    for t in fechas:
        y = float(div.loc[t] / prev.loc[t])
        i = dif.index.get_loc(t)
        d0 = float(dif.iloc[i])
        d1 = float(dif.iloc[i + 1]) if i + 1 < len(dif) else float("nan")
        est = "t" if d0 <= -0.5 * y else ("t+1" if d1 <= -0.5 * y else "ninguna")
        cuenta[est] += 1
        filas.append((t.date().isoformat(), round(y, 4), round(d0, 4), round(d1, 4), est))
    print("resumen:", cuenta)
    print("(fecha, yield, dif t, dif t+1, estado)")
    for fila in filas:
        print("  ", fila)


par("LYXIB.MC", "AMES.DE")
par("VUSA.DE", "VUAA.DE")
par("VUSA.AS", "VUAA.DE")

# 3) Moneda de VUAA.DE
try:
    print("\nMoneda VUAA.DE:", yf.Ticker("VUAA.DE").fast_info["currency"])
except Exception as e:
    print("\nMoneda VUAA.DE: error:", e)

# 4) Calendario común con IWDP.AS en lugar de IWDP.MI
UNIV = ["VUSA.AS", "LYXIB.MC", "IWDA.AS", "EXSA.DE", "IS3N.DE", "CNDX.AS", "EUNH.DE", "IEAC.AS", "IWDP.AS", "4GLD.DE"]
S = {t: cargar(t).loc[INICIO:] for t in UNIV}
cl = pd.concat({t: S[t]["Close"] for t in UNIV}, axis=1, join="inner", sort=True).dropna()
vol = pd.concat({t: S[t]["Volume"] for t in UNIV}, axis=1, join="inner", sort=True).loc[cl.index]
malas = vol.index[(vol == 0).any(axis=1)]
print("\nFechas comunes:", len(cl), "| con algún volumen 0:", len(malas), "| válidas:", len(cl) - len(malas))
print("Por año:", pd.Series(malas.year).value_counts().sort_index().to_dict())