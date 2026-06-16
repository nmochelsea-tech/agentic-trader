import pandas as pd
from agentic_trader.strategy import TrendRotationStrategy
from agentic_trader.backtest import run_backtest


def test_backtest_runs_on_simple_prices():
    idx = pd.bdate_range("2020-01-01", periods=260)
    px = pd.DataFrame({
        "SPY": [100 + i * 0.1 for i in range(len(idx))],
        "QQQ": [100 + i * 0.2 for i in range(len(idx))],
        "TLT": [100 for _ in idx],
        "BIL": [100 + i * 0.01 for i in range(len(idx))],
    }, index=idx)
    s = TrendRotationStrategy(["SPY", "QQQ", "TLT", "BIL"], "BIL", 20, 100, 60)
    result = run_backtest(px, s)
    assert len(result.equity) == len(px)
    assert result.metrics["end_value"] > 0
    assert "benchmark" in result.equity.columns
