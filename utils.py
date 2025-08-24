# utils.py
from __future__ import annotations
import os
from pathlib import Path
import io, zipfile
import pandas as pd
import requests

# Optional: install yfinance once in the teacher's env (see requirements.txt)
try:
    import yfinance as yf
except Exception:  # still let the app run; we'll just skip auto-downloads
    yf = None

# Resolve data dir relative to this file (not CWD), so it works anywhere
ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "fixed_stock_data"
DATA_DIR.mkdir(exist_ok=True)

# Some symbols need remapping on Yahoo
YAHOO_ALIAS = {
    "BRK.B": "BRK-B",
}

def _csv_path(ticker: str) -> Path:
    return DATA_DIR / f"{ticker}.csv"

def _ensure_local_csv(ticker: str, start="2020-01-01") -> bool:
    """
    Ensure we have <DATA_DIR>/<TICKER>.csv. If missing and yfinance is available,
    download it. Return True if file exists after this call.
    """
    path = _csv_path(ticker)
    if path.exists():
        return True
    if yf is None:
        return False

    yahoo_symbol = YAHOO_ALIAS.get(ticker, ticker)
    try:
        df = yf.download(yahoo_symbol, start=start)
        if df is None or df.empty:
            return False
        # Normalize to a simple CSV the app can read
        out = df.reset_index()[["Date", "Close"]]
        out.to_csv(path, index=False)
        return True
    except Exception:
        return False

def _read_close_series(csv_path: Path, start_date="2020-01-01") -> pd.Series:
    df = pd.read_csv(csv_path)

    if "Date" not in df.columns:
        raise ValueError(f"{csv_path.name} has no 'Date' column.")

    df["Date"] = pd.to_datetime(df["Date"])
    df = df.set_index("Date").sort_index()

    # Handle Nasdaq exports ("Close/Last") and Yahoo ("Close")
    col = "Close/Last" if "Close/Last" in df.columns else "Close" if "Close" in df.columns else None
    if col is None:
        raise ValueError(f"{csv_path.name} has neither 'Close' nor 'Close/Last'.")

    s = pd.to_numeric(df[col].replace({r"\$": ""}, regex=True), errors="coerce").dropna()
    return s.loc[s.index >= pd.to_datetime(start_date)]

def closing_prices(stocks: list[str], start_date="2020-01-01") -> pd.DataFrame:
    """
    stocks: list like ["AAPL.csv", "MSFT.csv", "JNJ.csv"] or ["AAPL", "MSFT", ...]
    Returns: DataFrame with tickers as columns and Close prices as values.
    Auto-downloads missing CSVs into fixed_stock_data when possible.
    """
    series = {}
    missing = []

    for item in stocks:
        # Accept 'AAPL.csv' or 'AAPL'
        ticker = Path(item).stem.upper()

        # Ensure the CSV exists (download if needed)
        ok = _ensure_local_csv(ticker, start=start_date)
        csv_path = _csv_path(ticker)

        if not ok and not csv_path.exists():
            missing.append(ticker)
            continue

        try:
            s = _read_close_series(csv_path, start_date=start_date)
            series[ticker] = s
        except Exception:
            missing.append(ticker)

    if not series:
        return pd.DataFrame()

    prices = pd.concat(series, axis=1).dropna()
    prices.columns = list(series.keys())

    # Attach info for UI (callers can check .attrs.get("missing"))
    prices.attrs["missing"] = sorted(set(missing))
    return prices

def ff3_factors(start_date="2020-01-01") -> pd.DataFrame:
    url = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_daily_CSV.zip"
    r = requests.get(url, timeout=60)
    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        with z.open(z.namelist()[0]) as f:
            data = pd.read_csv(f, skiprows=3)

    data = data.dropna()
    data.columns = ["Date", "Mkt-RF", "SMB", "HML", "RF"]
    data = data[data["Date"].astype(str).str.strip().str.isnumeric()]
    data["Date"] = pd.to_datetime(data["Date"])
    data = data.set_index("Date").sort_index()
    for c in ["Mkt-RF", "SMB", "HML", "RF"]:
        data[c] = data[c].astype(float) / 100.0
    return data.loc[data.index >= pd.to_datetime(start_date)]
