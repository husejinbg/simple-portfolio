from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import sqlite3
import algolab
import secretconfig

app = FastAPI()
templates = Jinja2Templates(directory="templates")

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

    return templates.TemplateResponse("home.html", {"request": request, "assets": assets, "total": total})


@app.get("/asset/{symbol}")
async def asset_detail(request: Request, symbol: str):
    asset = {"symbol": symbol}
    return templates.TemplateResponse("asset_detail.html", {"request": request, "asset": asset})