import pandas as pd
import os
import zipfile
import io
import requests

def closing_prices(stocks, start_date="2020-01-01"):
    
    all_prices={}
    
        #get ticker, date in correct format, set date as index and sort
    for stock in stocks:
        ticker = os.path.splitext(stock)[0].upper()
        data = pd.read_csv(stock)
        data["Date"] = pd.to_datetime(data["Date"])
        data = data.set_index("Date").sort_index()

        #get price in correct format
        price = data["Close/Last"].replace({r'\$': ''}, regex=True).astype(float)
        price = price[price.index >= pd.to_datetime(start_date)]
        all_prices[ticker] = price
    
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






