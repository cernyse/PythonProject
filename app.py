import pandas as pd
import streamlit as st
import statsmodels.api as sm
from utils import closing_prices, ff3_factors
from analysis import calculate_returns, calculate_volatility, calculate_cumulative_return
from portfolios import calculate_equal_weighted_portfolio
from visuals import plot_profit, plot_volatility, plot_returns

st.title("Portfolio/Stock Analysis with Fama-French Factors")

# get prices and tickers and calculate metrics
csv_files = ["AAPL.csv", "MSFT.csv", "TSLA.csv", "GOOG.csv", "AMZN.csv", "META.csv", "NVDA.csv", "SP500.csv"]
prices = closing_prices(csv_files)
tickers = prices.columns.tolist()

returns = calculate_returns(prices)
profit = calculate_cumulative_return(returns)
volatility = calculate_volatility(returns)

#MAG 7 portfolio
mag7 = ["AAPL", "MSFT", "TSLA", "GOOG", "AMZN", "META", "NVDA"]
returns["MAG7"] = calculate_equal_weighted_portfolio(returns, mag7)
volatility["MAG7"] = calculate_volatility(returns[["MAG7"]])
profit["MAG7"] = calculate_cumulative_return(returns["MAG7"])

st.sidebar.header("Select assets to display")
selected = st.sidebar.multiselect("Choose portfolios/stocks:", tickers + ["MAG7"], default=["MAG7"])

st.subheader("Cumulative Return")
plot_profit(profit, selected, title="Cumulative Return")

st.subheader("Rolling Volatility")
plot_volatility(volatility, selected, title="Weekly Rolling Volatility")

st.subheader("Daily Returns")
plot_returns(returns, selected, title="Daily Returns")

st.subheader("Fama-French 3-Factor Regression on MAG7")

ff3 = ff3_factors()

returns_ff3 = returns[returns.index <= ff3.index.max()].copy()
returns_ff3.loc[:, "MAG7"] = calculate_equal_weighted_portfolio(returns_ff3, mag7)

combined = pd.concat([returns_ff3["MAG7"], ff3], axis=1, join="inner").dropna()
combined = combined.rename(columns={"MAG7": "Portfolio"})
combined["Excess"] = combined["Portfolio"] - combined["RF"]

X = sm.add_constant(combined[["Mkt-RF", "SMB", "HML"]])
y = combined["Excess"]
model = sm.OLS(y, X).fit()

st.code(model.summary().as_text(), language="text")
