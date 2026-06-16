from pydantic import BaseModel, Field
from pathlib import Path
import yaml

class TraderConfig(BaseModel):
    universe: list[str]
    defensive_symbol: str = 'BIL'
    fast_ma: int = 50
    slow_ma: int = 200
    momentum_lookback: int = 126
    initial_cash: float = 10_000
    max_position_pct: float = Field(default=0.35, ge=0, le=1)
    max_trade_pct: float = Field(default=0.25, ge=0, le=1)
    min_cash_pct: float = Field(default=0.05, ge=0, le=1)
    require_human_approval: bool = True
    price_csv: str
    ledger_path: str = 'ledger.csv'

    @classmethod
    def from_yaml(cls, path: str | Path) -> 'TraderConfig':
        with open(path, 'r', encoding='utf-8') as f:
            return cls(**yaml.safe_load(f))
