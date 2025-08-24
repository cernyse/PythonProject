# portfolios.py
import pandas as pd

def calculate_equal_weighted_portfolio(returns_data: pd.DataFrame, tickers):
    tickers = [t.upper() for t in tickers]
    available = [t for t in tickers if t in returns_data.columns]
    if not available:
        raise ValueError(f"No selected tickers found. Requested: {tickers}")
    weights = pd.Series(1 / len(available), index=available)
    return returns_data[available].dot(weights)
