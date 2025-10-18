from fastapi import FastAPI, Request, APIRouter, HTTPException
from binance.spot import Spot
import os 

app = APIRouter()
api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")


@app.get("/status")
def get_status():
    return {"status": "Binance API is working!"}


@app.get("/balance", summary="取得 Binance 現貨資訊(幣本位)")
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


@app.get("/asset", summary="取得 Binance 現貨帳戶資訊(usdt)")
def get_asset():
    if not api_key or not api_secret:
        raise RuntimeError("Can't find Binance API Key or Secret in.env")
    client = Spot(api_key=api_key, api_secret=api_secret)
    try:
        # 取得現貨帳戶資產列表
        assets = client.user_asset()

        total_usdt_estimate = 0
        result_assets = []

        for a in assets:
            asset = a["asset"]
            free = float(a["free"])
            locked = float(a["locked"])
            total_amount = free + locked

            # 嘗試取得該幣種對USDT的匯率
            usdt_value = 0
            if asset == "USDT":
                usdt_value = total_amount
            else:
                symbol = f"{asset}USDT"
                try:
                    ticker = client.ticker_price(symbol=symbol)
                    price = float(ticker["price"])
                    usdt_value = total_amount * price
                except Exception:
                    # 若無法取得 (例如沒有該交易對)，usdt_value維持0
                    usdt_value = 0

            total_usdt_estimate += usdt_value

            result_assets.append({
                "asset": asset,
                "free": free,
                "locked": locked,
                "usdt_value": round(usdt_value, 4)
            })

        return {
            "total_usdt_estimate": round(total_usdt_estimate, 4),
            "assets": result_assets
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Binance API 呼叫失敗: {str(e)}")

# @app.get("/env")
# def check_env():

#     return {
#         "BINANCE_API_KEY": os.getenv("BINANCE_API_KEY"),
#         "BINANCE_API_SECRET": os.getenv("BINANCE_API_SECRET")
#     }
