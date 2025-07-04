import yfinance as yf
import os

tickers = [
    # Low risk
    "BRK.B", "JNJ", "PG", "KO", "PEP", "WMT", "VZ", "T", "XOM", "CVX",
    "PFE", "MRK", "LLY", "ABT", "MDT", "D", "SO", "DUK", "NEE", "CL",
    # Medium risk
    "V", "MA", "UNH", "HD", "LOW", "UPS", "BA", "CAT", "AXP", "GS",
    "MS", "JPM", "BAC", "C", "USB", "INTC", "CSCO", "ORCL", "IBM", "QCOM",
    # High risk
    "PLTR", "COIN", "ARKK", "ZM", "ROKU", "SHOP", "SQ", "DOCU", "CRWD", "DDOG",
    "NET", "SNOW", "ASML", "TEAM", "OKTA", "MDB", "BILL", "FSLY", "U", "AFRM",
    # Emerging/speculative
    "NIO", "XPEV", "LI", "TME", "JD", "BIDU", "PDD", "SE", "MELI", "TCEHY",
    "BABA", "YNDX", "MTCH", "FUBO", "BB", "GME", "AMC", "RBLX", "SBLK", "BBBY",
    # Diversifying ETFs & REITs
    "VNQ", "XLK", "XLE", "XLV", "XLF", "IWM", "VOO", "VTI", "ARKW", "ARKG",
    "XLU", "XLI", "XLY", "XLRE", "SPYG", "DIA", "IJR", "IVV", "MTUM", "VUG"
]
save_folder = "stock_data_100"
os.makedirs(save_folder, exist_ok=True)

# ✅ Download & save each stock
for ticker in tickers:
    try:
        data = yf.download(ticker, start="2020-01-01", end="2025-01-01")
        if not data.empty:
            data.to_csv(os.path.join(save_folder, f"{ticker}.csv"))
        else:
            print(f"no")
    except Exception as e:
        print(f"fail")

