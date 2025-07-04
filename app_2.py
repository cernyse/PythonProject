import pandas as pd
import os
import streamlit as st
import statsmodels.api as sm
from utils import closing_prices, ff3_factors
from analysis import calculate_returns, calculate_volatility, calculate_cumulative_return
from portfolios import calculate_equal_weighted_portfolio
from visuals import plot_profit, plot_volatility, plot_returns

st.title("Portfolio/Stock Analysis with Fama-French Factors")


risk_score = st.sidebar.slider("Select your risk score (1 = lowest risk, 10 = highest risk):", 1, 10, 5)


csv_files = [
    "AAPL.csv", "MSFT.csv", "TSLA.csv", "GOOG.csv", "AMZN.csv", "META.csv", "NVDA.csv", "SP500.csv",
    "JNJ.csv", "PG.csv", "KO.csv", "WMT.csv", "PEP.csv", "VZ.csv", "XOM.csv", "CVX.csv", "SO.csv", "NEE.csv",
    "MRK.csv", "ABT.csv", "D.csv", "DUK.csv", "LLY.csv", "UNH.csv", "HD.csv", "MA.csv", "V.csv", "LOW.csv",
    "JPM.csv", "BA.csv", "CAT.csv", "AXP.csv", "IBM.csv", "QCOM.csv", "INTC.csv", "ORCL.csv", "UPS.csv", "CSCO.csv",
    "SHOP.csv", "RBLX.csv", "ARKK.csv", "PLTR.csv", "CRWD.csv", "DOCU.csv", "AFRM.csv", "COIN.csv", "AMC.csv",
    "GME.csv", "FUBO.csv", "T.csv", "PFE.csv", "MDT.csv", "CL.csv", "GS.csv", "MS.csv",
    "BAC.csv", "C.csv", "USB.csv", "ASML.csv", "TEAM.csv", "OKTA.csv", "MDB.csv", "BILL.csv", "FSLY.csv", "U.csv",
    "NIO.csv", "XPEV.csv", "LI.csv", "TME.csv", "JD.csv", "BIDU.csv", "PDD.csv", "SE.csv", "MELI.csv", "TCEHY.csv",
    "BABA.csv", "MTCH.csv", "BB.csv", "VNQ.csv", "XLK.csv", "XLE.csv", "XLV.csv", "XLF.csv", "IWM.csv",
    "VOO.csv", "VTI.csv", "ARKW.csv", "ARKG.csv", "XLU.csv", "XLI.csv", "XLY.csv", "XLRE.csv", "SPYG.csv", "DIA.csv",
    "IJR.csv", "IVV.csv", "MTUM.csv", "VUG.csv"
]

prices = closing_prices(csv_files)
tickers = prices.columns.tolist()


returns = calculate_returns(prices)
profit = calculate_cumulative_return(returns)
volatility = calculate_volatility(returns)


risk_portfolios = {
    1: ["JNJ", "PG", "KO", "WMT", "PEP"],
    2: ["VZ", "XOM", "CVX", "SO", "NEE"],
    3: ["MRK", "ABT", "D", "DUK", "LLY"],
    4: ["UNH", "HD", "MA", "V", "LOW"],
    5: ["AAPL", "MSFT", "GOOG", "AMZN", "META"],
    6: ["JPM", "BA", "CAT", "AXP", "IBM"],
    7: ["QCOM", "INTC", "ORCL", "UPS", "CSCO"],
    8: ["TSLA", "NVDA", "SHOP", "RBLX", "SQ"],
    9: ["ARKK", "PLTR", "CRWD", "DOCU", "AFRM"],
    10: ["COIN", "AMC", "GME", "FUBO", "BBBY"]
}


selected_tickers = risk_portfolios[risk_score]
returns["RiskPortfolio"] = calculate_equal_weighted_portfolio(returns, selected_tickers)
volatility["RiskPortfolio"] = calculate_volatility(returns[["RiskPortfolio"]])
profit["RiskPortfolio"] = calculate_cumulative_return(returns["RiskPortfolio"])


st.markdown(f"### Portfolio for Risk Score {risk_score}")
st.write("Stocks in your portfolio:", ", ".join(selected_tickers))


selectable = tickers + ["RiskPortfolio"]
selected = st.sidebar.multiselect("Choose portfolios/stocks to display:", selectable, default=["RiskPortfolio"])


st.subheader("Cumulative Return")
plot_profit(profit, selected, title="Cumulative Return")

st.subheader("Rolling Volatility")
plot_volatility(volatility, selected, title="Weekly Rolling Volatility")

st.subheader("Daily Returns")
plot_returns(returns, selected, title="Daily Returns")


st.subheader("Fama-French 3-Factor Regression on RiskPortfolio")
ff3 = ff3_factors()
returns_ff3 = returns[returns.index <= ff3.index.max()].copy()
returns_ff3["RiskPortfolio"] = calculate_equal_weighted_portfolio(returns_ff3, selected_tickers)

combined = pd.concat([returns_ff3["RiskPortfolio"], ff3], axis=1, join="inner").dropna()

if combined.empty:
    st.warning("⚠️ Not enough data to run Fama-French regression. Please check your selected tickers or try a different risk score.")
else:
    combined = combined.rename(columns={"RiskPortfolio": "Portfolio"})
    combined["Excess"] = combined["Portfolio"] - combined["RF"]

    X = sm.add_constant(combined[["Mkt-RF", "SMB", "HML"]])
    y = combined["Excess"]

    model = sm.OLS(y, X).fit()
    st.code(model.summary().as_text(), language="text")

