import pandas as pd
import numpy as np

def calculate_returns(prices_data):
    return prices_data.pct_change().dropna()

def calculate_volatility(returns_data, window=5):
    return returns_data.rolling(window=window).std()

def calculate_cumulative_return(returns_data):
    return (returns_data + 1).cumprod()
