# Auditoría de datos (fase 1)

Fuente: Yahoo Finance vía `yfinance` (no oficial). Descarga con `auto_adjust=False`.
Todo lo marcado como *hipótesis* no está probado.

## Universo y roles
- **Universo (10):** VUSA.AS, LYXIB.MC, IWDA.AS, EXSA.DE, IS3N.DE, CNDX.AS, EUNH.DE, IEAC.AS, IWDP.AS, 4GLD.DE.
- **Validación:** VUSA.DE, VUAA.DE, IWDP.MI, AMES.DE.
- **Referencia:** ^IBEX (índice de precios, sin dividendos).
- **Excluido:** IUSN.DE (historia desde 2018-04-26).
- Todo cotiza en EUR (comprobado con `fast_info`). Bolsa principal: Euronext Ámsterdam;
  excepciones (Xetra, Madrid) porque el ETF no aparece en Yahoo en Ámsterdam o no cotiza en EUR.
- 4GLD.DE es Xetra-Gold, un ETC (no un UCITS ETF).

## Periodo y calendario
- Periodo de estudio: desde 2014-10-06 (inicio de CNDX.AS). 2008-2013 queda fuera:
  alta iliquidez (días con volumen cero) en varios ETFs.
- Fechas comunes del universo: 3.055; con algún volumen 0: 14; **válidas: 3.041**
  (por año: 2017: 4, 2018: 6, 2023: 3, 2024: 1).
- Regla: una fecha es válida solo si ningún activo del universo tiene volumen 0.
  El retorno que cruza una fecha descartada es faltante (no se fusionan días).

## Hallazgos
1. **Filas obsoletas en Xetra:** 2017-10-03, 2017-10-31, 2018-05-21 y 2023-12-04/05/06 tienen
   volumen 0 y retorno exactamente 0 en 4-7 tickers (hipótesis: relleno sin cotización real).
2. **IWDP.MI:** precio repetido con volumen 0 el 2022-09-19 y 20, se pone al día el 21.
   Se usa IWDP.AS (0 días de volumen 0 en la ventana frente a 7).
3. **LYXIB.MC (ETF IBEX 35):** 12 días con diferencia de más de 2 puntos frente a ^IBEX,
   con patrón de error y corrección (2018-09-24, 2020-03-12/13, 2022-09-19/20, 2024-05-28/29,
   2024-08-19, 2024-09-02/03, 2024-12-10/11). Causa desconocida (dato de Yahoo o desfase real).
   Se mantiene con una columna de calidad; los resultados se reportan con y sin esos días.
   La regla de marcado se fija solo con el periodo de entrenamiento.
4. **Dividendos y Adj Close:** bonos (EUNH.DE, IEAC.AS) 17 de 17 en el día esperado.
   VUSA frente a VUAA.DE: 7 de 7, solo 2025-2026 (VUAA.DE desde 2024-12-30).
   LYXIB.MC frente a AMES.DE: 2 de 2 mal fechados un día antes (2024-12-10 y 2025-12-09).
   EXSA.DE e IWDP.AS: no verificados.
5. **Validación cruzada:** VUSA.AS frente a VUSA.DE, correlación 0,9957 (retornos desde precios alineados).
6. **Eventos conocidos:** los mayores movimientos coinciden con marzo de 2020, agosto de 2015,
   el 2016-06-24 y abril de 2025 (verificar contra fuente externa).

## Limitaciones
- Fuente no oficial; condiciones de uso por revisar.
- La auditoría inspeccionó todo el periodo, incluido el futuro conjunto de prueba. Fue una
  revisión de calidad de datos, sin resultados de modelos.
- Los ETFs sobre EE. UU. cierran en Europa antes que Wall Street (cierres asíncronos):
  cuidado con fugas temporales al usar un ETF como variable de otro.
- Calendarios distintos por bolsa: se usan fechas comunes.
- Historia: panel de ~12 años; IUSN.DE y otros candidatos quedaron fuera por historia corta.