from __future__ import annotations

import pandas as pd
from .sweep import parameter_sweep
from .strategy import TrendRotationStrategy
from .backtest import run_backtest
from .metrics import summarize_equity


def walk_forward_test(
    px: pd.DataFrame,
    universe: list[str],
    defensive_symbol: str,
    train_years: int = 3,
    test_months: int = 6,
    fast_ma_values: list[int] | None = None,
    slow_ma_values: list[int] | None = None,
    momentum_values: list[int] | None = None,
    initial_cash: float = 10_000.0,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    fast_ma_values = fast_ma_values or [20, 50]
    slow_ma_values = slow_ma_values or [100, 150, 200]
    momentum_values = momentum_values or [60, 90, 120]
    px = px.sort_index().ffill().dropna()
    start = px.index.min() + pd.DateOffset(years=train_years)
    end = px.index.max()
    windows = []
    equity_parts = []
    capital = initial_cash
    test_start = start

    while test_start < end:
        train_start = test_start - pd.DateOffset(years=train_years)
        test_end = min(test_start + pd.DateOffset(months=test_months), end)
        train_px = px.loc[(px.index >= train_start) & (px.index < test_start)]
        test_px = px.loc[(px.index >= test_start) & (px.index <= test_end)]
        if len(train_px) < 252 or len(test_px) < 20:
            break
        sweep = parameter_sweep(train_px, universe, defensive_symbol, fast_ma_values, slow_ma_values, momentum_values, initial_cash=initial_cash)
        best = sweep.iloc[0]
        strategy = TrendRotationStrategy(universe, defensive_symbol, int(best.fast_ma), int(best.slow_ma), int(best.momentum_lookback))
        result = run_backtest(test_px, strategy, initial_cash=capital)
        capital = float(result.equity["equity"].iloc[-1])
        part = result.equity[["equity", "holding"]].copy()
        equity_parts.append(part)
        windows.append({
            "train_start": train_start.date(),
            "test_start": test_start.date(),
            "test_end": test_end.date(),
            "chosen_fast_ma": int(best.fast_ma),
            "chosen_slow_ma": int(best.slow_ma),
            "chosen_momentum": int(best.momentum_lookback),
            "test_cagr": result.metrics["cagr"],
            "test_max_drawdown": result.metrics["max_drawdown"],
            "test_sharpe": result.metrics["sharpe"],
        })
        test_start = test_end + pd.Timedelta(days=1)

    if not equity_parts:
        return pd.DataFrame(windows), pd.DataFrame()
    equity = pd.concat(equity_parts).sort_index()
    equity = equity[~equity.index.duplicated(keep="last")]
    metrics = summarize_equity(equity["equity"])
    windows_df = pd.DataFrame(windows)
    for k, v in metrics.items():
        windows_df.attrs[k] = v
    return windows_df, equity
