# analysis.py
import pandas as pd
import numpy as np

def calculate_returns(prices_data: pd.DataFrame) -> pd.DataFrame:
    return prices_data.pct_change().dropna()

def calculate_volatility(returns_data: pd.DataFrame, window: int = 5) -> pd.DataFrame:
    return returns_data.rolling(window=window).std()

def calculate_cumulative_return(returns_data: pd.DataFrame):
    return (returns_data + 1).cumprod()
