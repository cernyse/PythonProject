import pandas as pd

def calculate_equal_weighted_portfolio(returns_data, tickers):

    weights = {ticker: 1/len(tickers) for ticker in tickers}
    portfolio_return = returns_data[tickers].dot(pd.Series(weights))
    return portfolio_return