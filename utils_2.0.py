import pandas as pd
import os
import zipfile
import io
import requests


def closing_prices(stocks, start_date="2020-01-01"):
    all_prices = {}

    for stock in stocks:
        ticker = os.path.splitext(stock)[0].upper()
        try:
            data = pd.read_csv(stock)
            data["Date"] = pd.to_datetime(data["Date"])
            data = data.set_index("Date").sort_index()

            # Flexible handling of Close vs Close/Last
            column = "Close/Last" if "Close/Last" in data.columns else "Close"
            if column not in data.columns:
                print(f"⚠️ Skipping {stock} (no 'Close' or 'Close/Last')")
                continue

            price = pd.to_numeric(data[column].replace({r'\$': ''}, regex=True), errors="coerce").dropna()
            price = price[price.index >= pd.to_datetime(start_date)]
            all_prices[ticker] = price
        except Exception as e:
            print(f"❌ Failed to process {stock}: {e}")

    if not all_prices:
        print("❌ No valid prices loaded.")
        return pd.DataFrame()

    prices_data = pd.concat(all_prices.values(), axis=1)
    prices_data.columns = all_prices.keys()
    return prices_data.dropna()


def ff3_factors(start_date="2020-01-01"):
    url = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_daily_CSV.zip"
    response = requests.get(url)

    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        with z.open(z.namelist()[0]) as f:
            data = pd.read_csv(f, skiprows=3)

    data = data.dropna()
    data.columns = ["Date", "Mkt-RF", "SMB", "HML", "RF"]
    data = data[data["Date"].str.strip().str.isnumeric()]
    data["Date"] = pd.to_datetime(data["Date"])
    data = data.set_index("Date").sort_index()
    data[["Mkt-RF", "SMB", "HML", "RF"]] = data[["Mkt-RF", "SMB", "HML", "RF"]].astype(float) / 100
    data = data[data.index >= pd.to_datetime(start_date)]

    return data






