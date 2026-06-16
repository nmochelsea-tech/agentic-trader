import pandas as pd
from pathlib import Path

def load_prices(csv_path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path, parse_dates=['date'])
    required = {'date', 'symbol', 'close'}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f'Missing required columns: {missing}')
    return df.sort_values(['date', 'symbol']).reset_index(drop=True)

def price_matrix(prices: pd.DataFrame) -> pd.DataFrame:
    return prices.pivot(index='date', columns='symbol', values='close').sort_index().ffill()
