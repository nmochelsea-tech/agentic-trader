from __future__ import annotations

import math
import pandas as pd
import numpy as np

TRADING_DAYS = 252


def equity_returns(equity: pd.Series) -> pd.Series:
    return equity.pct_change().fillna(0.0)


def max_drawdown(equity: pd.Series) -> float:
    if equity.empty:
        return 0.0
    peak = equity.cummax()
    dd = equity / peak - 1.0
    return float(dd.min())


def annualized_return(equity: pd.Series) -> float:
    if len(equity) < 2:
        return 0.0
    total = float(equity.iloc[-1] / equity.iloc[0] - 1.0)
    years = max((equity.index[-1] - equity.index[0]).days / 365.25, 1 / 365.25)
    return (1 + total) ** (1 / years) - 1


def annualized_volatility(returns: pd.Series) -> float:
    return float(returns.std(ddof=0) * math.sqrt(TRADING_DAYS))


def sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.0) -> float:
    daily_rf = risk_free_rate / TRADING_DAYS
    excess = returns - daily_rf
    vol = excess.std(ddof=0)
    if vol == 0 or np.isnan(vol):
        return 0.0
    return float(excess.mean() / vol * math.sqrt(TRADING_DAYS))


def sortino_ratio(returns: pd.Series, risk_free_rate: float = 0.0) -> float:
    daily_rf = risk_free_rate / TRADING_DAYS
    excess = returns - daily_rf
    downside = excess[excess < 0]
    downside_vol = downside.std(ddof=0)
    if downside_vol == 0 or np.isnan(downside_vol):
        return 0.0
    return float(excess.mean() / downside_vol * math.sqrt(TRADING_DAYS))


def calmar_ratio(equity: pd.Series) -> float:
    mdd = abs(max_drawdown(equity))
    return 0.0 if mdd == 0 else float(annualized_return(equity) / mdd)


def summarize_equity(equity: pd.Series, risk_free_rate: float = 0.0) -> dict[str, float]:
    returns = equity_returns(equity)
    wins = returns[returns > 0]
    losses = returns[returns < 0]
    return {
        "start_value": float(equity.iloc[0]) if len(equity) else 0.0,
        "end_value": float(equity.iloc[-1]) if len(equity) else 0.0,
        "total_return": float(equity.iloc[-1] / equity.iloc[0] - 1.0) if len(equity) > 1 else 0.0,
        "cagr": annualized_return(equity),
        "annualized_volatility": annualized_volatility(returns),
        "sharpe": sharpe_ratio(returns, risk_free_rate),
        "sortino": sortino_ratio(returns, risk_free_rate),
        "max_drawdown": max_drawdown(equity),
        "calmar": calmar_ratio(equity),
        "win_rate_days": float((returns > 0).mean()),
        "best_day": float(returns.max()),
        "worst_day": float(returns.min()),
        "avg_win_day": float(wins.mean()) if len(wins) else 0.0,
        "avg_loss_day": float(losses.mean()) if len(losses) else 0.0,
    }
