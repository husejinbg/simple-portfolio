import algolab
import algolabconfig
import secretconfig
import sqlite3
import config
import datetime
import json
import yfinance

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

def update_assets():
    connection = sqlite3.connect(config.DB_FILE)
    cursor = connection.cursor()

    with open("data/bist_companies.json") as f:
        companies = json.load(f)
    
    for company in companies:
        symbol = company["symbol"]
        name = company["name"]
        exchange = "BIST"

        if cursor.execute("SELECT * FROM assets WHERE symbol = ?", (symbol,)).fetchone() is None:
            cursor.execute("INSERT INTO assets (symbol, name, exchange) VALUES (?, ?, ?)", (symbol, name, exchange))

        # update name if it has changed
        cursor.execute("UPDATE assets SET name = ? WHERE symbol = ?", (name, symbol))
    
    connection.commit()



def get_last_price(symbol) -> float:
    return float(client.GetEquityInfo(symbol)["content"]["lst"])

def insert_order(asset_id: int, type: str, side: str, quantity: float, price: float, timestamp: str, status: str):
    connection = sqlite3.connect(config.DB_FILE)
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO orders (asset_id, type, side, quantity, price, timestamp, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (asset_id, type, side, quantity, price, timestamp, status))
    connection.commit()

def send_market_order(symbol: str, quantity: int, is_buy: bool):
    data = {
        "symbol": symbol,
        "direction": "BUY" if is_buy else "SELL",
        "pricetype": "piyasa",
        "price": "",
        "lot": str(quantity),
        "sms": False,
        "email": False,
        "subAccount": ""
    }
    print(client.SendOrder(**data))

def send_limit_order(symbol: str, quantity: int, price: float, is_buy: bool):
    data = {
        "symbol": symbol,
        "direction": "BUY" if is_buy else "SELL",
        "pricetype": "limit",
        "price": str(price),
        "lot": str(quantity),
        "sms": False,
        "email": False,
        "subAccount": ""
    }
    print(client.SendOrder(**data))

def send_limit_from_market_order(symbol: str, quantity: int, current_price: float, offset: float, is_buy: bool):
    price = get_last_price(symbol)
    if offset == -1 or abs(price - current_price) <= offset:
        send_limit_order(symbol, quantity, price, is_buy)

def get_orders():
    data = client.GetTodaysTransaction()["content"]
    orders = []
    for x in data:
        orders.append({
            "id": x["atpref"],
            "symbol": x["ticker"],
            "type": "-",
            "side": "buy" if x["buysell"][0] == "A" else "sell",
            "order_size": int(float(x["ordersize"])),
            "remaining_size": int(float(x["remainingsize"])),
            "order_price": round(float(x["waitingprice"]), 2),
            "total": round(float(x["ordersize"]) * float(x["waitingprice"]), 2),
            "status": x["description"],
            "timestamp": x["timetransaction"]
        })
    return orders

def get_positions():
    data = client.GetInstantPosition()["content"]
    positions = []
    for x in data:
        if x["explanation"] == "TRY":
            continue            
        positions.append({
            "symbol": x["explanation"],
            "quantity": int(float(x["totalstock"])) if x["totalstock"] != "-" else 0,
            "average_price": round(float(x["cost"]),2),
            "current_price": x["unitprice"],
            "market_value": round(float(x["tlamaount"]), 2),
            "pl": round(float(x["profit"]), 2) if x["profit"] != "-" else 0,
        })
    return positions

def cancel_order(order_id: str):
    print(client.DeleteOrder(order_id, ""))

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