from agentic_trader.risk import RiskManager

def test_risk_caps_order():
    r = RiskManager(max_position_pct=0.35, max_trade_pct=0.25, min_cash_pct=0.05)
    d = r.propose_rebalance('SPY', 'test', {'cash': 10000, 'positions': {}})
    assert d.approved
    assert d.order.notional == 2500
