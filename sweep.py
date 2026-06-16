from __future__ import annotations

from itertools import product
import pandas as pd
from .strategy import TrendRotationStrategy
from .backtest import run_backtest


def parameter_sweep(
    px: pd.DataFrame,
    universe: list[str],
    defensive_symbol: str,
    fast_ma_values: list[int],
    slow_ma_values: list[int],
    momentum_values: list[int],
    initial_cash: float = 10_000.0,
) -> pd.DataFrame:
    rows = []
    for fast, slow, mom in product(fast_ma_values, slow_ma_values, momentum_values):
        if fast >= slow:
            continue
        strategy = TrendRotationStrategy(universe, defensive_symbol, fast, slow, mom)
        result = run_backtest(px, strategy, initial_cash=initial_cash)
        row = {"fast_ma": fast, "slow_ma": slow, "momentum_lookback": mom}
        row.update(result.metrics)
        rows.append(row)
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values(["sharpe", "cagr", "max_drawdown"], ascending=[False, False, False])
    return df
