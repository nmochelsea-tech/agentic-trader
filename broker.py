from __future__ import annotations
from dataclasses import dataclass, asdict
import csv
from pathlib import Path

@dataclass
class OrderIntent:
    symbol: str
    side: str  # BUY or SELL
    notional: float
    reason: str

@dataclass
class Fill:
    symbol: str
    side: str
    notional: float
    status: str
    reason: str

class Broker:
    def get_portfolio(self) -> dict:
        raise NotImplementedError
    def place_order(self, order: OrderIntent) -> Fill:
        raise NotImplementedError

class PaperBroker(Broker):
    def __init__(self, initial_cash: float, ledger_path: str = 'ledger.csv'):
        self.cash = initial_cash
        self.positions: dict[str, float] = {}
        self.ledger_path = Path(ledger_path)

    def get_portfolio(self) -> dict:
        return {'cash': self.cash, 'positions': self.positions.copy()}

    def place_order(self, order: OrderIntent) -> Fill:
        if order.notional <= 0:
            return Fill(order.symbol, order.side, order.notional, 'REJECTED', 'Order notional must be positive.')
        if order.side == 'BUY':
            if order.notional > self.cash:
                return Fill(order.symbol, order.side, order.notional, 'REJECTED', 'Insufficient paper cash.')
            self.cash -= order.notional
            self.positions[order.symbol] = self.positions.get(order.symbol, 0.0) + order.notional
        elif order.side == 'SELL':
            held = self.positions.get(order.symbol, 0.0)
            sell_amt = min(order.notional, held)
            self.positions[order.symbol] = max(0.0, held - sell_amt)
            self.cash += sell_amt
        else:
            return Fill(order.symbol, order.side, order.notional, 'REJECTED', 'Invalid side.')
        fill = Fill(order.symbol, order.side, order.notional, 'FILLED_PAPER', order.reason)
        self._append_ledger(fill)
        return fill

    def _append_ledger(self, fill: Fill) -> None:
        exists = self.ledger_path.exists()
        with self.ledger_path.open('a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=asdict(fill).keys())
            if not exists:
                writer.writeheader()
            writer.writerow(asdict(fill))

class RobinhoodMCPBroker(Broker):
    """Placeholder adapter.

    Robinhood Agentic Trading is exposed through Robinhood's Trading MCP inside a compatible agent client.
    Keep this class as the boundary where your MCP tool calls would be wired. Do not store credentials here.
    """
    def get_portfolio(self) -> dict:
        raise NotImplementedError('Wire this to Robinhood Trading MCP portfolio/account tools.')
    def place_order(self, order: OrderIntent) -> Fill:
        raise NotImplementedError('Wire this to Robinhood Trading MCP order placement tools.')
