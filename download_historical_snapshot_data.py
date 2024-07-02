import sqlite3
import yfinance
import pandas as pd
import config

symbols = ["HALKB.IS", "KCHOL.IS", "SKBNK.IS", "ZOREN.IS"]
start_date = "2024-06-01"
end_date = "2024-07-02"

def get_asset_id(symbol: str, name: str = None, exchange: str = None):
    if name is None:
        name = symbol
    if exchange is None:
        exchange = "BIST"

    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    row = cursor.execute("SELECT id FROM assets WHERE symbol = ?", (symbol,)).fetchone()
    if row:
        return row[0]
    else:
        cursor.execute("INSERT INTO assets (symbol, name, exchange) VALUES (?, ?, ?)", (symbol, name, exchange))
        connection.commit()
        return cursor.execute("SELECT id FROM assets WHERE symbol = ?", (symbol,)).fetchone()[0]

def insert_snapshot(symbol, position, average_price, currency, last_price, timestamp):
    connection = sqlite3.connect(config.DB_FILE)
    cursor = connection.cursor()
    asset_id = get_asset_id(symbol)

    if position == -1:
        position = cursor.execute("SELECT position FROM portfolio WHERE asset_id = ?", (asset_id,)).fetchone()[0]
    
    if average_price == -1:
        average_price = cursor.execute("SELECT average_price FROM portfolio WHERE asset_id = ?", (asset_id,)).fetchone()[0]

    cursor.execute("""
        INSERT INTO snapshots (asset_id, position, average_price, currency, last_price, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (asset_id, position, average_price, currency, last_price, timestamp))
    connection.commit()

for symbol in symbols:
    
    df = yfinance.download(symbol, start=start_date, end=end_date)
    df.reset_index(inplace=True)
    df["Date"] = df["Date"].astype(str) + "T03:00:00+00:00"

    symbol = symbol.replace(".IS", "")
    for i in range(len(df)):
        date = df.iloc[i]["Date"]
        close = df.iloc[i]["Close"]
        insert_snapshot(symbol, -1, -1, "TRY", close, date)
        print(f"Inserted snapshot for {symbol} on {date}")
    print(f"Inserted all snapshots for {symbol}")

