# visuals.py
import matplotlib.pyplot as plt
import streamlit as st

def plot_profit(profit_data, tickers, title="Cumulative Return"):
    if not tickers:
        st.warning("No portfolios selected to plot.")
        return
    fig, ax = plt.subplots(figsize=(12, 6))
    profit_data[tickers].plot(ax=ax)
    ax.set_title(title)
    ax.set_xlabel("Date")
    ax.set_ylabel("Growth (Starting = 1.0)")
    ax.grid(True)
    st.pyplot(fig)

def plot_volatility(volatility_data, tickers, title="Rolling Volatility"):
    if not tickers:
        st.warning("No portfolios selected to plot.")
        return
    fig, ax = plt.subplots(figsize=(12, 6))
    volatility_data[tickers].plot(ax=ax)
    ax.set_title(title)
    ax.set_xlabel("Date")
    ax.set_ylabel("Volatility (Std. Dev.)")
    ax.grid(True)
    st.pyplot(fig)

def plot_returns(returns_data, tickers, title="Daily Returns"):
    if not tickers:
        st.warning("No portfolios selected to plot.")
        return
    fig, ax = plt.subplots(figsize=(12, 6))
    returns_data[tickers].plot(ax=ax)
    ax.set_title(title)
    ax.set_xlabel("Date")
    ax.set_ylabel("Daily Return")
    ax.grid(True)
    st.pyplot(fig)
