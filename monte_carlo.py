from __future__ import annotations

import numpy as np
import pandas as pd
from .metrics import summarize_equity


def bootstrap_returns(equity: pd.Series, simulations: int = 1000, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    returns = equity.pct_change().dropna().to_numpy()
    if len(returns) == 0:
        raise ValueError("not enough equity history for simulation")
    rows = []
    for sim in range(simulations):
        sampled = rng.choice(returns, size=len(returns), replace=True)
        curve = equity.iloc[0] * pd.Series(1 + sampled).cumprod()
        curve.index = equity.index[1:]
        m = summarize_equity(curve)
        m["simulation"] = sim
        rows.append(m)
    return pd.DataFrame(rows)


def summarize_monte_carlo(mc: pd.DataFrame) -> pd.DataFrame:
    fields = ["total_return", "cagr", "max_drawdown", "sharpe", "end_value"]
    rows = []
    for f in fields:
        rows.append({
            "metric": f,
            "p05": mc[f].quantile(0.05),
            "p25": mc[f].quantile(0.25),
            "median": mc[f].quantile(0.50),
            "p75": mc[f].quantile(0.75),
            "p95": mc[f].quantile(0.95),
        })
    return pd.DataFrame(rows)
