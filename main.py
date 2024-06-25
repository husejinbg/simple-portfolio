from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import sqlite3
import algolab
import secretconfig
client = algolab.API(secretconfig.MY_API_KEY, secretconfig.MY_USERNAME, secretconfig.MY_PASSWORD)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/asset/{symbol}")
async def asset_detail(request: Request, symbol: str):
    asset = {"symbol": symbol}
    return templates.TemplateResponse("asset_detail.html", {"request": request, "asset": asset})