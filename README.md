# Agentic Trader Starter Kit

Educational starter project for a risk-first, human-approvable trading agent.

## Strategy chosen for v1

**ETF trend-following / risk-on-risk-off rotation** using liquid ETFs. This is intentionally boring:
- fewer symbols
- avoids options and leverage
- easier to backtest
- lower turnover than intraday trading
- easier risk controls

Default universe:
- SPY: US large-cap equities
- QQQ: growth/tech equities
- TLT: long-duration Treasuries
- BIL: cash-like Treasury bill ETF

Signal:
- Compute fast and slow moving averages.
- Rank assets by momentum.
- Hold top risk asset only if it is above its slow moving average.
- Otherwise hold BIL.

## Architecture

```
Market data -> Strategy -> Risk manager -> Approval gate -> Broker adapter -> Ledger/logs
                          ^                              |
                          |                              v
                         Audit log <------------------ Execution reports
```

## Safety defaults

- Paper mode by default.
- No margin, no options, no leverage.
- Max one trade per run.
- Position cap per symbol.
- Daily loss guard placeholder.
- Human approval required unless explicitly disabled.

## Install

```bash
cd agentic_trader
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run with bundled sample data

```bash
python -m agentic_trader.cli --config configs/config.example.yaml --paper
```

## Add real data

The starter uses a CSV file with columns:

```text
date,symbol,close
```

You can replace `data/sample_prices.csv` with your own exported data.

## Robinhood integration

Robinhood currently has official crypto trading API docs, and Agentic Trading/MCP support for third-party agents. This kit includes a broker interface plus paper broker. The `RobinhoodMCPBroker` is a placeholder because MCP connection details happen inside Robinhood/your agent client and should not be hardcoded here.

Do not put credentials in code. Use environment variables or your agent client's secure connector.

## Important

This is not financial advice. Backtest and paper trade before using real money.

## Testing ecosystem

Run the full research harness:

```bash
PYTHONPATH=src python -m agentic_trader.cli test --config configs/config.example.yaml --out reports/latest
```

This creates a Markdown report, charts, backtest metrics, trade logs, parameter sweeps, walk-forward results, and Monte Carlo stress-test outputs. See `docs/TESTING_ECOSYSTEM.md` for details.

## Dashboard

A local Streamlit dashboard is included for viewing live-style performance, metrics, risk diagnostics, trades, parameter sweeps, walk-forward tests, Monte Carlo robustness, and strategy insights.

Run fresh tests:

```bash
PYTHONPATH=src python -m agentic_trader.cli test --config configs/config.example.yaml --out reports/latest
```

Start the dashboard:

```bash
streamlit run dashboard.py
```

Open the local URL printed by Streamlit.

## Visual architecture

Open these files for a polished flowchart of the trading and learning loop:

- `docs/assets/agentic_trader_flowchart.png`
- `docs/assets/agentic_trader_flowchart.svg`

The feedback loop is intentionally gated: results create improvement candidates, candidates are backtested/walk-forward tested/stress tested, and only then can a human approve deployment. The live bot should not rewrite its own risk constraints.
