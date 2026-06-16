from dataclasses import dataclass
from .broker import OrderIntent

@dataclass
class RiskDecision:
    approved: bool
    order: OrderIntent | None
    reason: str

class RiskManager:
    def __init__(self, max_position_pct: float, max_trade_pct: float, min_cash_pct: float):
        self.max_position_pct = max_position_pct
        self.max_trade_pct = max_trade_pct
        self.min_cash_pct = min_cash_pct

    def propose_rebalance(self, target_symbol: str, reason: str, portfolio: dict) -> RiskDecision:
        cash = float(portfolio.get('cash', 0.0))
        positions = dict(portfolio.get('positions', {}))
        equity = cash + sum(float(v) for v in positions.values())
        if equity <= 0:
            return RiskDecision(False, None, 'No account equity available.')
        current = float(positions.get(target_symbol, 0.0))
        max_target = equity * self.max_position_pct
        trade_cap = equity * self.max_trade_pct
        min_cash = equity * self.min_cash_pct
        desired_buy = max(0.0, max_target - current)
        notional = min(desired_buy, trade_cap, max(0.0, cash - min_cash))
        if notional < 25:
            return RiskDecision(False, None, 'Trade below $25 or cash reserve would be breached.')
        return RiskDecision(True, OrderIntent(target_symbol, 'BUY', round(notional, 2), reason), 'Approved by risk limits.')
