# Dashboard

This project includes a local Streamlit dashboard for viewing performance, metrics, risk diagnostics, trades, parameter sweeps, walk-forward tests, and Monte Carlo results.

## Run the testing suite first

```bash
PYTHONPATH=src python -m agentic_trader.cli test --config configs/config.example.yaml --out reports/latest
```

## Start the dashboard

```bash
streamlit run dashboard.py
```

Then open the local Streamlit URL shown in your terminal.

## What it shows

- Current performance snapshot: total return, CAGR, Sharpe, max drawdown, volatility
- Equity curve and drawdown chart
- Benchmark comparison
- Best parameter sets from the sweep
- Walk-forward results
- Monte Carlo robustness summary
- Recent trades
- Learning-loop explanation

## Live performance note

The dashboard reads the latest generated files from `reports/latest`. For true live performance, schedule the trader/paper-trader to append portfolio state and trades to the same folder or a database, then refresh the dashboard. The first production-grade upgrade would be to replace CSV files with SQLite/Postgres and add a scheduled data collector.
