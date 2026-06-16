# Testing Ecosystem

This project now includes a research/testing harness so you can evaluate the strategy before letting any broker adapter touch real money.

## What it tests

1. **Historical backtest**
   - Daily close-to-close simulation
   - Weekly Friday rebalance by default
   - Transaction-cost assumption in basis points
   - Strategy equity curve vs equal-weight risk benchmark

2. **Parameter sweep**
   - Tests combinations of fast moving average, slow moving average, and momentum lookback
   - Sorts by Sharpe, CAGR, and drawdown
   - Helps identify whether the strategy is robust or just lucky with one parameter set

3. **Walk-forward test**
   - Optimizes parameters on a rolling training window
   - Tests those chosen parameters on future unseen windows
   - Better approximation of how you would have selected settings in real time

4. **Monte Carlo bootstrap**
   - Resamples daily strategy returns to estimate uncertainty
   - Produces percentile ranges for returns, CAGR, drawdown, Sharpe, and ending value

5. **Report output**
   - Markdown report
   - Equity chart
   - Drawdown chart
   - CSVs for deeper analysis

## Run the full test suite

From the project root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=src python -m agentic_trader.cli test \
  --config configs/config.example.yaml \
  --out reports/latest
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:PYTHONPATH="src"
python -m agentic_trader.cli test --config configs/config.example.yaml --out reports/latest
```

## Key files generated

- `reports/latest/REPORT.md` — readable summary
- `reports/latest/equity_curve.png` — strategy vs benchmark
- `reports/latest/drawdown.png` — drawdown over time
- `reports/latest/equity_curve.csv` — daily portfolio values
- `reports/latest/trades.csv` — simulated allocation changes
- `reports/latest/strategy_metrics.csv` — strategy metrics
- `reports/latest/benchmark_metrics.csv` — benchmark metrics
- `reports/latest/parameter_sweep.csv` — all parameter combinations
- `reports/latest/monte_carlo.csv` — all Monte Carlo simulation outputs
- `reports/latest/monte_carlo_summary.csv` — percentile summary
- `reports/latest/walk_forward_windows.csv` — rolling out-of-sample windows
- `reports/latest/walk_forward_equity.csv` — walk-forward equity curve when enough data exists

## Try alternate assumptions

Higher costs:

```bash
PYTHONPATH=src python -m agentic_trader.cli test \
  --config configs/config.example.yaml \
  --out reports/high_cost \
  --cost-bps 10
```

More parameter combinations:

```bash
PYTHONPATH=src python -m agentic_trader.cli test \
  --config configs/config.example.yaml \
  --out reports/wide_sweep \
  --fast-ma 10 20 50 \
  --slow-ma 100 150 200 250 \
  --momentum 30 60 90 120 180
```

More Monte Carlo simulations:

```bash
PYTHONPATH=src python -m agentic_trader.cli test \
  --config configs/config.example.yaml \
  --out reports/mc_5000 \
  --simulations 5000
```

## Bring your own market data

Use a CSV with these columns:

```csv
date,symbol,close
2020-01-02,SPY,324.87
2020-01-02,QQQ,216.16
```

Then run:

```bash
PYTHONPATH=src python -m agentic_trader.cli test \
  --config configs/config.example.yaml \
  --prices data/your_prices.csv \
  --out reports/your_test
```

## Evaluation rules of thumb

Do not consider a strategy promising unless it passes most of these checks:

- Outperforms benchmark after transaction costs
- Lower max drawdown than benchmark
- Reasonable trade count, not hyperactive churn
- Parameter sweep shows a broad cluster of decent results, not one isolated winner
- Walk-forward test is still acceptable out of sample
- Monte Carlo 5th percentile drawdown is survivable

## Next upgrades

- Add taxes and wash-sale tracking
- Add dividends and total-return price data
- Add slippage based on asset liquidity
- Add market regime filters
- Add a Streamlit dashboard
- Add broker-paper shadow mode: real signals, fake execution, daily emailed report
