   # Contexto del proyecto
   - Usuario: Andrés, nivel intermedio en DS, vive en España, Windows, 32 GB RAM, conda (Miniforge), PowerShell + gh.
   - Proyecto: predicción de volatilidad realizada a 5 días de 10-12 ETFs UCITS, VaR/ES con backtesting.
   - Benchmarks: ingenuo, EWMA, HAR, GARCH. ML: Ridge, random forest, gradient boosting.
   - Stack: Python, PostgreSQL (Docker Compose), SQLAlchemy, scikit-learn, FastAPI, MLflow, GitHub Actions.
   - Reglas: español; partición temporal con embargo antes de transformar; test tocado una vez; hipótesis marcadas; sin afirmar causalidad; no ejecutar nada en mi máquina (yo ejecuto y devuelvo resultados).
   - Estado actual: fase 0 cerrada (Docker, Postgres 16, entorno conda, repo en GitHub). Siguiente: fase 1.
   - Último resultado: Postgres 16.15 responde desde Python (SQLAlchemy + psycopg). pytest 9.1.1.