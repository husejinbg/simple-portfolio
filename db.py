import algolab
import algolabconfig
import secretconfig
import sqlite3
import config
import datetime

client = algolab.API(secretconfig.MY_API_KEY, secretconfig.MY_USERNAME, secretconfig.MY_PASSWORD)

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

def update_portfolio(asset_id, symbol, position, average_price, currency, last_price):
    connection = sqlite3.connect(config.DB_FILE)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    if cursor.execute("SELECT * FROM portfolio WHERE asset_id = ?", (asset_id,)).fetchone() is None:
        cursor.execute("""
            INSERT INTO portfolio (asset_id, position, average_price, currency, last_price)
            VALUES (?, ?, ?, ?, ?)
        """, (asset_id, position, average_price, currency, last_price))
    else:
        cursor.execute("""
            UPDATE portfolio
            SET position = ?, average_price = ?, currency = ?, last_price = ?
            WHERE asset_id = ?
        """, (position, average_price, currency, last_price, asset_id))
    connection.commit()

def insert_snapshot(symbol, position, average_price, currency, last_price, timestamp):
    connection = sqlite3.connect(config.DB_FILE)
    cursor = connection.cursor()
    asset_id = get_asset_id(symbol)
    cursor.execute("""
        INSERT INTO snapshots (asset_id, position, average_price, currency, last_price, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (asset_id, position, average_price, currency, last_price, timestamp))
    connection.commit()

    update_portfolio(asset_id, symbol, position, average_price, currency, last_price)

def take_snapshot():
    utc_timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    portfolio = client.GetInstantPosition()["content"]
    for asset in portfolio:
        if asset["code"] == "-":
            continue

        symbol = asset["code"]
        position = asset["totalstock"]
        average_price = asset["cost"]
        currency = "TRY"
        last_price = asset["unitprice"]
        insert_snapshot(symbol, position, average_price, currency, last_price, utc_timestamp)
