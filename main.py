from fastapi import FastAPI, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import sqlite3
import algolab
import secretconfig
import pandas as pd
import db

app = FastAPI()

app.mount("/data", StaticFiles(directory="data"), name="data")

templates = Jinja2Templates(directory="templates")

@app.get("/test")
async def test(request: Request):
    dates = ["2021-01-01", "2021-01-02", "2021-01-03", "2021-01-04", "2021-01-05"]
    try_values = [10, 11, 12, 13, 14]
    usd_values = [7, 8, 9, 10, 11]
    dates += ["2021-01-06", "2021-01-07", "2021-01-08", "2021-01-09", "2021-01-10", "2021-01-11", "2021-01-12", "2021-01-13", "2021-01-14", "2021-01-15", "2021-01-16", "2021-01-17", "2021-01-18", "2021-01-19", "2021-01-20", "2021-01-21", "2021-01-22", "2021-01-23", "2021-01-24", "2021-01-25", "2021-01-26", "2021-01-27", "2021-01-28", "2021-01-29", "2021-01-30", "2021-01-31", "2021-02-01", "2021-02-02", "2021-02-03", "2021-02-04", "2021-02-05", "2021-02-06", "2021-02-07", "2021-02-08", "2021-02-09", "2021-02-10", "2021-02-11", "2021-02-12", "2021-02-13", "2021-02-14", "2021-02-15", "2021-02-16", "2021-02-17", "2021-02-18", "2021-02-19", "2021-02-20", "2021-02-21", "2021-02-22", "2021-02-23", "2021-02-24", "2021-02-25", "2021-02-26", "2021-02-27", "2021-02-28", "2021-03-01", "2021-03-02", "2021-03-03", "2021-03-04", "2021-03-05", "2021-03-06", "2021-03-07", "2021-03-08", "2021-03-09", "2021-03-10", "2021-03-11", "2021-03-12", "2021-03-13", "2021-03-14", "2021-03-15", "2021-03-16", "2021-03-17", "2021-03-18", "2021-03-19", "2021-03-20", "2021-03-21", "2021-03-22", "2021-03-23", "2021-03-24", "2021-03-25", "2021-03-26", "2021-03-27", "2021-03-28", "2021-03-29", "2021-03-30", "2021-03-31", "2021-04-01", "2021-04-02", "2021-04-03", "2021-04-04", "2021-04-05", "2021-04-06", "2021-04-07", "2021-04-08", "2021-04-09", "2021-04-10"]
    try_values += [15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100]
    usd_values += [12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100]

    return templates.TemplateResponse("test.html", {"request": request, "dates": dates, "try_values": try_values, "usd_values": usd_values})

@app.get("/")
async def home(request: Request):
    connection = sqlite3.connect("./app.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    assets = cursor.execute("SELECT * FROM assets").fetchall()
    return templates.TemplateResponse("home.html", {"request": request, "assets": assets})

@app.get("/portfolio")
async def portfolio(request: Request):
    connection = sqlite3.connect("./app.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    data = cursor.execute("""
        SELECT
            timestamp,
            SUM(position * last_price) AS market_value
        FROM snapshots
        GROUP BY timestamp
    """).fetchall()

    dates = [x["timestamp"][:10] for x in data]
    try_values = [x["market_value"] for x in data]
    usdtry = db.get_usdtry()
    usd_values = [x / usdtry[dates[i]] for i, x in enumerate(try_values)]
    positions = db.get_positions()[1:]

    return templates.TemplateResponse("test.html", {"request": request, "dates": dates, "try_values": try_values, "usd_values": usd_values, "positions": positions})

@app.get("/portfolio/{symbol}")
async def portfolio_asset(request: Request, symbol: str):
    connection = sqlite3.connect("./app.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    data = cursor.execute("""
        SELECT
            timestamp,
            SUM(position * last_price) AS market_value
        FROM snapshots
        WHERE asset_id = ?
        GROUP BY timestamp
    """, (db.get_asset_id(symbol),)).fetchall()

    dates = [x["timestamp"][:10] for x in data]
    try_values = [x["market_value"] for x in data]
    usdtry = db.get_usdtry()
    usd_values = [x / usdtry[dates[i]] for i, x in enumerate(try_values)]

    return templates.TemplateResponse("portfolio_asset.html", {"request": request, "dates": dates, "try_values": try_values, "usd_values": usd_values})


@app.get("/asset/{symbol}")
async def asset_detail(request: Request, symbol: str):
    orders = db.get_orders()
    positions = db.get_positions()
    last_price = db.get_last_price(symbol)
    return templates.TemplateResponse("asset.html", {"request": request, "asset_symbol": symbol, "current_price": last_price, "exchange": "BIST", "positions": positions, "orders": orders})

@app.post("/take_snapshot")
async def take_snapshot():
    db.take_snapshot()
    return {"result": "snapshot taken successfully"}

@app.post("/update_assets")
async def update_assets():
    db.update_assets()
    return {"result": "assets updated successfully"}

@app.get("/order/{symbol}")
async def order(request: Request, symbol: str):
    current_price = db.get_last_price(symbol)
    return templates.TemplateResponse("order.html", {"request": request, "asset_symbol": symbol, "current_price": current_price})

@app.post("/order")
async def send_order(data: dict):
    for key, value in data.items():
        if not value:
            data[key] = -1
    print(data)

    orderType = data["orderType"]
    symbol = data["symbol"]
    quantity = int(data["quantity"])
    totalPrice = float(data["totalPrice"])
    price = float(data["price"])
    offset = float(data["offset"])
    currentPrice = float(data["currentPrice"])
    action = data["action"]

    if orderType == "market":
        if quantity == -1:
            quantity = int(totalPrice / currentPrice)
        db.send_market_order(symbol, quantity, action == "buy")
    
    elif orderType == "limit":
        if quantity == -1:
            quantity = int(totalPrice / price)
        db.send_limit_order(symbol, quantity, price, action == "buy")
    
    elif orderType == "limit-market":
        if quantity == -1:
            quantity = int(totalPrice / currentPrice)
        db.send_limit_from_market_order(symbol, quantity, currentPrice, offset, action == "buy")

@app.post("/cancel_order")
async def cancel_order(data: dict):
    db.cancel_order(data["order_id"])
    return {"result": "order cancelled successfully"}
