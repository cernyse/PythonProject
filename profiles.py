# profiles.py
from __future__ import annotations
import numpy as np
import pandas as pd

YF_ALIAS = {
    "BRK.B": "BRK-B",
    "SP500": "^GSPC",
}

def _mask_by_horizon(index: pd.DatetimeIndex, horizon: str) -> pd.Series:
    if index.empty:
        return pd.Series([], dtype=bool)
    end = index.max()
    if horizon == "Max":
        start = index.min()
    elif horizon == "YTD":
        start = pd.Timestamp(end.year, 1, 1)
    elif horizon == "3M":
        start = end - pd.DateOffset(months=3)
    elif horizon == "6M":
        start = end - pd.DateOffset(months=6)
    elif horizon == "1Y":
        start = end - pd.DateOffset(years=1)
    elif horizon == "3Y":
        start = end - pd.DateOffset(years=3)
    else:
        start = index.min()
    return (index >= start) & (index <= end)

def _horizon_return(series: pd.Series) -> float | float("nan"):
    if series.size < 2:
        return np.nan
    return float(series.iloc[-1] / series.iloc[0] - 1.0)

def _ann_vol(series: pd.Series) -> float | float("nan"):
    r = series.pct_change().dropna()
    if r.empty:
        return np.nan
    # Annualize with sqrt(252)
    return float(r.std(ddof=0) * np.sqrt(252))

def _max_drawdown(series: pd.Series) -> float | float("nan"):
    s = series.dropna()
    if s.empty:
        return np.nan
    roll_max = s.cummax()
    dd = s / roll_max - 1.0
    return float(dd.min())

def _fmt_pct(x):
    return "N/A" if pd.isna(x) else f"{x:.2%}"

def _fmt_num(x):
    return "N/A" if pd.isna(x) else f"{x:,.2f}"

def build_summary_table(prices: pd.DataFrame, horizon: str = "1Y") -> pd.DataFrame:
    """
    Returns a table with one row per ticker for the chosen horizon:
      - Last Price (as of last date in horizon)
      - Return (horizon)
      - Annualized Volatility (horizon)
      - Max Drawdown (horizon)
    """
    rows = []
    for t in prices.columns:
        s_full = prices[t].dropna()
        if s_full.empty:
            rows.append({"Ticker": t, "Last Price": np.nan, "As of": "N/A",
                         "Return": np.nan, "Ann. Vol": np.nan, "Max DD": np.nan})
            continue

        mask = _mask_by_horizon(s_full.index, horizon)
        s = s_full.loc[mask]
        if s.size < 2:
            rows.append({"Ticker": t, "Last Price": float(s_full.iloc[-1]), "As of": s_full.index[-1].date().isoformat(),
                         "Return": np.nan, "Ann. Vol": np.nan, "Max DD": np.nan})
            continue

        last_price = float(s.iloc[-1])
        as_of = s.index[-1].date().isoformat()
        row = {
            "Ticker": t,
            "Last Price": last_price,
            "As of": as_of,
            "Return": _horizon_return(s),
            "Ann. Vol": _ann_vol(s),
            "Max DD": _max_drawdown(s),
        }
        rows.append(row)

    df = pd.DataFrame(rows).set_index("Ticker")
    # Pretty display
    df_fmt = df.copy()
    df_fmt["Last Price"] = df["Last Price"].apply(_fmt_num)
    for col in ["Return", "Ann. Vol", "Max DD"]:
        df_fmt[col] = df[col].apply(_fmt_pct)
    return df_fmt

def fetch_company_info(ticker: str) -> dict | None:
    try:
        import yfinance as yf
    except Exception:
        return None

    symbol = YF_ALIAS.get(ticker, ticker)
    try:
        tk = yf.Ticker(symbol)
        info = None
        if hasattr(tk, "get_info"):
            info = tk.get_info()
        if not info and hasattr(tk, "info"):
            info = tk.info
        if not info:
            return None

        return {
            "name": info.get("longName") or info.get("shortName") or ticker,
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "country": info.get("country"),
            "website": info.get("website"),
            "summary": info.get("longBusinessSummary"),
            "marketCap": info.get("marketCap"),
            "trailingPE": info.get("trailingPE"),
            "forwardPE": info.get("forwardPE"),
            "dividendYield": info.get("dividendYield"),
            "beta": info.get("beta"),
            "currency": info.get("currency"),
        }
    except Exception:
        return None
