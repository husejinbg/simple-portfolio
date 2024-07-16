import yfinance
import datetime

def get_usdtry(start: str = "2024-01-01"):
    today = datetime.date.today()

    symbol = "USDTRY=X"

    df = yfinance.download(symbol, start=start)
    temp = yfinance.download(symbol, start=today, interval="1m")
    if len(temp) > 0:
        df.loc[f"{today} 00:00:00"] = temp.iloc[-1]

    df = df.reset_index()
    df["Date"] = df["Date"].astype(str)

    usdtry = {}

    for i in range(len(df)):
        usdtry[df.iloc[i]["Date"][:10]] = df.iloc[i]["Close"]

    return usdtry

print(get_usdtry())

