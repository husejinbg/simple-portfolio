from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import sqlite3
import algolab
import secretconfig
import pandas as pd

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/test")
async def test(request: Request):
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
    # df = pd.read_csv("./AAPL.csv")
    # data = []
    # for i in range(len(df)):
    #     date = df.iloc[i]["Date"]
    #     close = df.iloc[i]["Close"]
    #     data.append({"date": date, "close": close})
    return templates.TemplateResponse("test.html", {"request": request, "data": data})

@app.get("/")
async def home(request: Request):
    connection = sqlite3.connect("./app.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    assets = cursor.execute("""
        SELECT
            a.symbol,
            a.name,
            p.position,
            p.average_price,
            p.last_price,
            p.position * p.last_price AS market_value
        FROM portfolio p
        JOIN assets a ON p.asset_id = a.id;
    """).fetchall()

    total = 0
    for asset in assets:
        total += asset["market_value"]

    data = cursor.execute("""
        SELECT
            timestamp,
            SUM(position * last_price) AS market_value
        FROM snapshots
        GROUP BY timestamp
    """).fetchall()

    return templates.TemplateResponse("home.html", {"request": request, "assets": assets, "total": total, "data": data})


@app.get("/asset/{symbol}")
async def asset_detail(request: Request, symbol: str):
    asset = {"symbol": symbol}
    connection = sqlite3.connect("./app.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    # snapshots = cursor.execute("""
    #     SELECT
    #         position,
    #         average_price,
    #         last_price,
    #         position * last_price AS market_value,
    #         timestamp
    #     FROM snapshots
    #     WHERE asset_id = (
    #         SELECT id FROM assets WHERE symbol = ?
    #     )
    #     ORDER BY id DESC
    # """, (symbol,)).fetchall()

    data = cursor.execute("""
        SELECT
            timestamp,
            position * last_price AS market_value
        FROM snapshots
        WHERE asset_id = (
            SELECT id FROM assets WHERE symbol = ?
        )
    """, (symbol,)).fetchall()

    return templates.TemplateResponse("asset_detail.html", {"request": request, "asset": asset, "data": data})