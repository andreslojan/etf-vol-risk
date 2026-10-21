"""Diagnóstico v4: fechas de dividendo, filas obsoletas y calendario común."""
from pathlib import Path

import pandas as pd

RAW = Path("data/raw")
INICIO = "2014-10-06"
UNIV = ["VUSA.AS", "LYXIB.MC", "IWDA.AS", "EXSA.DE", "IS3N.DE", "CNDX.AS", "EUNH.DE", "IEAC.AS", "IWDP.MI", "4GLD.DE"]
DIST = ["VUSA.AS", "LYXIB.MC", "EXSA.DE", "EUNH.DE", "IEAC.AS", "IWDP.MI"]

series = {
    t: pd.read_csv(RAW / f"{t}.csv", index_col=0, parse_dates=True).sort_index().loc[INICIO:]
    for t in UNIV
}

print("Dividendos >= 0,8 % del precio previo: ¿dónde cae el Close?")
for t in DIST:
    h = series[t]
    rc = h["Close"].pct_change()
    y_all = h["Dividends"] / h["Close"].shift(1)
    n = alineados = dia_sig = ninguno = 0
    raros = []
    for f in h.index[y_all >= 0.008]:
        i = h.index.get_loc(f)
        y = float(y_all.loc[f])
        r0 = float(rc.iloc[i])
        r1 = float(rc.iloc[i + 1]) if i + 1 < len(rc) else float("nan")
        n += 1
        if r0 <= -0.5 * y:
            alineados += 1
        else:
            if r1 <= -0.5 * y:
                dia_sig += 1
            else:
                ninguno += 1
            raros.append((f.date().isoformat(), round(y, 4), round(r0, 4), round(r1, 4)))
    print(f"\n{t}: {n} dividendos | caída en t: {alineados} | caída en t+1: {dia_sig} | ninguna: {ninguno}")
    for x in raros:
        print("   (fecha, yield, ret t, ret t+1):", x)

cl = pd.concat({t: series[t]["Close"] for t in UNIV}, axis=1, join="inner", sort=True).dropna()
vol = pd.concat({t: series[t]["Volume"] for t in UNIV}, axis=1, join="inner", sort=True).loc[cl.index]
r = cl.pct_change()
z = vol == 0
malas = vol.index[z.any(axis=1)]
print("\nFechas comunes:", len(cl))
print("Fechas con algún volumen 0:", len(malas), "| válidas:", len(cl) - len(malas))
print("Por año:", pd.Series(malas.year).value_counts().sort_index().to_dict())
print("Filas con volumen 0:", int(z.to_numpy().sum()), "| con retorno exactamente 0:", int(((r == 0) & z).to_numpy().sum()))