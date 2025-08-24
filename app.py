# app.py
from __future__ import annotations
import numpy as np
import pandas as pd
import streamlit as st
import statsmodels.api as sm

from utils import closing_prices, ff3_factors
from analysis import calculate_returns, calculate_volatility, calculate_cumulative_return
from portfolios import calculate_equal_weighted_portfolio
from visuals import plot_profit, plot_volatility, plot_returns
from profiles import build_summary_table  # company info removed

# ---------------- UI: title + dropdown width fix ----------------
st.title("Equity Risk & Factor Explorer")
st.markdown(
    """
    <style>
      /* Make selectbox options popup wider and allow wrapping so text isn't cut off */
      div[role="listbox"] { width: 360px !important; max-width: none !important; }
      div[role="option"] > div { white-space: normal !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- Helpers: time-range & rolling-vol presets ----------------
TIME_RANGE_PRESETS = ["YTD", "3M", "6M", "1Y", "3Y", "Max"]
ROLLING_VOL_CHOICES = {
    "Weekly (5 trading days)": 5,
    "Monthly (21 trading days)": 21,
    "Quarterly (63 trading days)": 63,
}  # Yearly removed

def date_mask(index: pd.DatetimeIndex, preset: str) -> pd.Series:
    """Return a boolean mask for the given time range preset."""
    if index.empty:
        return pd.Series([], dtype=bool)
    end = index.max()
    if preset == "Max":
        start = index.min()
    elif preset == "YTD":
        start = pd.Timestamp(end.year, 1, 1)
    elif preset == "3M":
        start = end - pd.DateOffset(months=3)
    elif preset == "6M":
        start = end - pd.DateOffset(months=6)
    elif preset == "1Y":
        start = end - pd.DateOffset(years=1)
    elif preset == "3Y":
        start = end - pd.DateOffset(years=3)
    else:
        start = index.min()
    return (index >= start) & (index <= end)

#STATIC RISKPORTFOLIOS
risk_portfolios_static = {
    1: ["JNJ", "PG", "KO", "WMT", "PEP"],
    2: ["VZ", "XOM", "CVX", "SO", "NEE"],
    3: ["MRK", "ABT", "D", "DUK", "LLY"],
    4: ["UNH", "HD", "MA", "V", "LOW"],
    5: ["AAPL", "MSFT", "GOOG", "AMZN", "META"],
    6: ["JPM", "BA", "CAT", "AXP", "IBM"],
    7: ["QCOM", "INTC", "ORCL", "UPS", "CSCO"],
    8: ["TSLA", "NVDA", "SHOP", "RBLX", "SQ"],
    9: ["ARKK", "PLTR", "CRWD", "DOCU", "AFRM"],
    10: ["COIN", "AMC", "GME", "FUBO", "BBBY"],
}
mag7 = ["AAPL", "MSFT", "TSLA", "GOOG", "AMZN", "META", "NVDA"]
universe = sorted(set(sum(risk_portfolios_static.values(), []) + mag7 + ["SP500"]))

#LOAD DATA
prices_full = closing_prices(universe)
if prices_full.empty:
    st.error("No price data loaded (even after attempting downloads). Check tickers or internet connection.")
    st.stop()

missing_any = prices_full.attrs.get("missing", [])
if missing_any:
    st.info("Some tickers could not be loaded and will be skipped: " + ", ".join(missing_any))

tab_analysis, tab_profiles = st.tabs(["Analysis", "Stock Profiles"])

#ANALYSIS TAB
with tab_analysis:
    st.subheader("Time horizon & risk tolerance")
    col1, col2, col3 = st.columns([1, 1.8, 2])
    with col1:
        time_range = st.selectbox("Time range", TIME_RANGE_PRESETS, index=5)
    with col2:
        vol_label = st.selectbox("Rolling volatility window", list(ROLLING_VOL_CHOICES.keys()), index=0)
        vol_window = ROLLING_VOL_CHOICES[vol_label]
    with col3:
        risk_score = st.slider("Risk score (1 = lowest risk, 10 = highest)", 1, 10, 5)

    mode = st.radio(
        "Portfolio mode",
        ["Predefined (static)", "Data-driven (by volatility)"],
        index=0,
        horizontal=True,
        help="Static = fixed buckets in code; Data-driven = deciles by realized volatility over the selected time range.",
    )

    mask = date_mask(prices_full.index, time_range)
    prices = prices_full.loc[mask]
    if prices.empty or prices.shape[0] < 2:
        st.warning("Not enough data in the selected time range.")
        st.stop()

    tickers_all = prices.columns.tolist()
    returns = calculate_returns(prices)
    profit = calculate_cumulative_return(returns)
    volatility = calculate_volatility(returns, window=vol_window)

    # PORTFOLIO/TICKERS SELECTION
    if mode == "Predefined (static)":
        selected_tickers = list(risk_portfolios_static[risk_score])
        missing = [t for t in selected_tickers if t not in returns.columns]
        if missing:
            st.warning(f"Missing data for: {', '.join(missing)} — they will be skipped.")
        selected_tickers = [t for t in selected_tickers if t in returns.columns]
        if not selected_tickers:
            st.error("None of the tickers in this risk portfolio have data for the selected time range.")
            st.stop()
    else:

        universe_driven = [t for t in returns.columns if t != "SP500"]
        if len(universe_driven) < 2:
            st.error("Need at least 2 tickers (ex-SP500) to form data-driven buckets.")
            st.stop()

        vol_metric = returns[universe_driven].std(skipna=True) * np.sqrt(252)
        vol_metric = vol_metric.dropna().sort_values()

        if vol_metric.empty:
            st.error("No valid volatility data to build data-driven buckets.")
            st.stop()

        groups = np.array_split(vol_metric.index.to_numpy(), 10)
        buckets = {i + 1: list(groups[i]) for i in range(10)}
        selected_tickers = buckets.get(risk_score, [])
        if not selected_tickers:
            st.error("Selected risk bucket is empty. Try a different time range.")
            st.stop()

        st.caption("Portfolio mode: Data-driven deciles by annualized realized volatility over the selected time range.")

    #PORTFOLIO SERIES
    returns["RiskPortfolio"] = calculate_equal_weighted_portfolio(returns, selected_tickers)
    volatility["RiskPortfolio"] = calculate_volatility(returns[["RiskPortfolio"]], window=vol_window)
    profit["RiskPortfolio"] = calculate_cumulative_return(returns["RiskPortfolio"])

    selectable = tickers_all + ["RiskPortfolio"]
    chosen = st.multiselect("Display portfolio/stocks:", selectable, default=["RiskPortfolio"])

    extras = [s for s in chosen if s != "RiskPortfolio"]
    base_str = ", ".join(selected_tickers) if selected_tickers else "(none)"
    title_text = f"{base_str} + {', '.join(extras)}" if extras else base_str
    st.markdown(f"### Portfolio/Stock(s) for Risk Score {risk_score} — {title_text}")

    st.subheader(f"Cumulative Return — {time_range}")
    plot_profit(profit, chosen, title=f"Cumulative Return ({time_range})")

    st.subheader(f"Rolling Volatility — {vol_label}")
    plot_volatility(volatility, chosen, title=f"Rolling Volatility ({vol_label})")

    st.subheader(f"Daily Returns — {time_range}")
    plot_returns(returns, chosen, title=f"Daily Returns ({time_range})")

    #FAMA-FRENCH REGRESSION
    st.subheader(f"Fama-French 3-Factor Regression — {time_range}")
    ff3 = ff3_factors()
    ff3 = ff3.loc[returns.index.min():returns.index.max()]
    if ff3.empty or returns.shape[0] < 30:
        st.warning("Not enough overlapping data for regression in this time range.")
    else:
        returns_ff3 = returns.copy()
        returns_ff3["RiskPortfolio"] = calculate_equal_weighted_portfolio(returns_ff3, selected_tickers)
        combined = pd.concat([returns_ff3["RiskPortfolio"], ff3], axis=1, join="inner").dropna()
        if combined.empty:
            st.warning("Not enough overlapping data for regression.")
        else:
            combined = combined.rename(columns={"RiskPortfolio": "Portfolio"})
            combined["Excess"] = combined["Portfolio"] - combined["RF"]
            X = sm.add_constant(combined[["Mkt-RF", "SMB", "HML"]])
            y = combined["Excess"]
            model = sm.OLS(y, X).fit()
            st.code(model.summary().as_text(), language="text")

#STOCK PROFILES TAB
with tab_profiles:
    st.subheader("Stock Profiles & Key Stats")

    col1, col2 = st.columns([1.2, 2])
    with col1:
        horizon = st.selectbox("Stats time range", TIME_RANGE_PRESETS, index=2)
    with col2:
        st.caption("Table uses the selected time range for Return, Annualized Volatility, and Max Drawdown.")

    mask_h = date_mask(prices_full.index, horizon)
    prices_h = prices_full.loc[mask_h]

    table = build_summary_table(prices_h, horizon=horizon)
    st.dataframe(table, use_container_width=True)
