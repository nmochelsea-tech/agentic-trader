from dataclasses import dataclass
import pandas as pd

@dataclass(frozen=True)
class Signal:
    target_symbol: str
    reason: str
    as_of: str

class TrendRotationStrategy:
    def __init__(self, universe: list[str], defensive_symbol: str, fast_ma: int, slow_ma: int, momentum_lookback: int):
        self.universe = universe
        self.defensive_symbol = defensive_symbol
        self.risk_assets = [s for s in universe if s != defensive_symbol]
        self.fast_ma = fast_ma
        self.slow_ma = slow_ma
        self.momentum_lookback = momentum_lookback

    def generate_signal(self, px: pd.DataFrame) -> Signal:
        if len(px) < max(self.slow_ma, self.momentum_lookback) + 1:
            return Signal(self.defensive_symbol, 'Not enough history; stay defensive.', str(px.index[-1].date()))
        latest = px.iloc[-1]
        slow = px.rolling(self.slow_ma).mean().iloc[-1]
        momentum = px.pct_change(self.momentum_lookback).iloc[-1]
        candidates = []
        for sym in self.risk_assets:
            if latest[sym] > slow[sym]:
                candidates.append((sym, float(momentum[sym])))
        if not candidates:
            return Signal(self.defensive_symbol, 'No risk asset above slow moving average; hold defensive asset.', str(px.index[-1].date()))
        target = sorted(candidates, key=lambda x: x[1], reverse=True)[0][0]
        return Signal(target, f'{target} has strongest {self.momentum_lookback}-day momentum among assets above {self.slow_ma}-day MA.', str(px.index[-1].date()))
