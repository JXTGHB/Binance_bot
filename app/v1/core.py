from fastapi import FastAPI, Request, APIRouter, HTTPException
from binance.spot import Spot
import os 

app = APIRouter()
api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")


@app.get("/status")
def get_status():
    return {"status": "Binance API is working!"}


@app.get("/balance", summary="取得 Binance 現貨帳戶資訊")
def get_balance():
    if not api_key or not api_secret:
        raise RuntimeError("Can't find Binance API Key or Secret in.env")
    client = Spot(api_key=api_key, api_secret=api_secret)
    try:
        account = client.account()
        # 過濾出非零餘額
        nonzero_balances = [
            {
                "asset": b["asset"],
                "free": b["free"],
                "locked": b["locked"]
            }
            for b in account["balances"]
            if float(b["free"]) > 0 or float(b["locked"]) > 0
        ]
        return {
            "makerCommission": account["makerCommission"],
            "takerCommission": account["takerCommission"],
            "canTrade": account["canTrade"],
            "canWithdraw": account["canWithdraw"],
            "canDeposit": account["canDeposit"],
            "balances": nonzero_balances
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Binance API 呼叫失敗: {str(e)}")


@app.get("/env")
def check_env():

    return {
        "BINANCE_API_KEY": os.getenv("BINANCE_API_KEY"),
        "BINANCE_API_SECRET": os.getenv("BINANCE_API_SECRET")
    }
