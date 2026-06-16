from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import pandas as pd

from .strategy import TrendRotationStrategy
from .metrics import summarize_equity


@dataclass(frozen=True)
class BacktestResult:
    equity: pd.DataFrame
    trades: pd.DataFrame
    metrics: dict[str, float]
    benchmark_metrics: dict[str, float]


def _equal_weight_benchmark(px: pd.DataFrame, initial_cash: float, symbols: list[str]) -> pd.Series:
    daily_rets = px[symbols].pct_change().fillna(0.0).mean(axis=1)
    return initial_cash * (1 + daily_rets).cumprod()


def run_backtest(
    px: pd.DataFrame,
    strategy: TrendRotationStrategy,
    initial_cash: float = 10_000.0,
    rebalance_frequency: str = "W-FRI",
    transaction_cost_bps: float = 2.0,
    benchmark_symbols: list[str] | None = None,
) -> BacktestResult:
    """Daily close-to-close backtest.

    Signal is generated on scheduled rebalance days using data through that day's close.
    Allocation changes are applied for the next trading day to reduce lookahead bias.
    """
    if px.empty:
        raise ValueError("price matrix is empty")
    px = px.dropna(how="all").ffill().dropna()
    rebalance_dates = set(px.resample(rebalance_frequency).last().index)
    target_by_day: list[str] = []
    pending_target = strategy.defensive_symbol
    current_target = strategy.defensive_symbol
    trades = []
    equity_values = [initial_cash]
    current_value = initial_cash
    cost_rate = transaction_cost_bps / 10_000

    for i, date in enumerate(px.index):
        if i > 0:
            prev = px.index[i - 1]
            ret = px.loc[date, current_target] / px.loc[prev, current_target] - 1.0
            current_value *= 1.0 + float(ret)

        # Apply pending target after return calculation, meaning tomorrow receives today's signal.
        if pending_target != current_target:
            current_value *= 1.0 - cost_rate
            trades.append({
                "date": date,
                "from": current_target,
                "to": pending_target,
                "cost_bps": transaction_cost_bps,
                "equity_after_cost": current_value,
            })
            current_target = pending_target

        if date in rebalance_dates:
            signal = strategy.generate_signal(px.loc[:date, strategy.universe])
            pending_target = signal.target_symbol

        target_by_day.append(current_target)
        equity_values.append(current_value)

    equity = pd.DataFrame({
        "date": px.index,
        "equity": equity_values[1:],
        "holding": target_by_day,
    }).set_index("date")

    bench_syms = benchmark_symbols or [s for s in strategy.universe if s != strategy.defensive_symbol]
    benchmark = _equal_weight_benchmark(px, initial_cash, bench_syms)
    equity["benchmark"] = benchmark.reindex(equity.index).ffill()
    metrics = summarize_equity(equity["equity"])
    metrics["num_trades"] = float(len(trades))
    metrics["turnover_per_year"] = float(len(trades) / max((equity.index[-1] - equity.index[0]).days / 365.25, 1 / 365.25))
    benchmark_metrics = summarize_equity(equity["benchmark"])
    trades_df = pd.DataFrame(trades)
    return BacktestResult(equity=equity, trades=trades_df, metrics=metrics, benchmark_metrics=benchmark_metrics)


def save_backtest_result(result: BacktestResult, out_dir: str | Path) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    result.equity.to_csv(out / "equity_curve.csv")
    result.trades.to_csv(out / "trades.csv", index=False)
    pd.Series(result.metrics, name="strategy").to_csv(out / "strategy_metrics.csv")
    pd.Series(result.benchmark_metrics, name="benchmark").to_csv(out / "benchmark_metrics.csv")
