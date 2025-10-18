from fastapi import FastAPI, Request, APIRouter, HTTPException
import os
import time
import hmac
import hashlib
import requests

app = APIRouter()
API_KEY = os.getenv("PIONEX_API_KEY")
API_SECRET = os.getenv("PIONEX_API_SECRET")
BASE_URL = "https://api.pionex.com"


@app.get("/status")
def get_status():
    return {"status": "Pionex API is working!"}

def pionex_signed_request(method: str, path: str, params=None, body=None):
    """
    通用簽名請求方法，可用於 GET / POST / DELETE。
    """
    if not API_KEY or not API_SECRET:
        raise RuntimeError("Missing Pionex API credentials (PIONEX_API_KEY / PIONEX_API_SECRET).")

    timestamp = str(int(time.time() * 1000))

    if params is None:
        params = {}
    params["timestamp"] = timestamp

    # 依 key 升冪排序
    sorted_items = sorted(params.items(), key=lambda kv: kv[0])
    query_string = "&".join(f"{k}={v}" for k, v in sorted_items)
    path_url = f"{path}?{query_string}"

    # 拼接簽名字串
    message = method.upper() + path_url
    if body is not None and method.upper() in ("POST", "DELETE"):
        import json
        message += json.dumps(body, separators=(",", ":"))

    # 產生 HMAC SHA256 簽名
    signature = hmac.new(API_SECRET.encode(), message.encode(), hashlib.sha256).hexdigest()

    headers = {
        "PIONEX-KEY": API_KEY,
        "PIONEX-SIGNATURE": signature,
        "PIONEX-TIMESTAMP": timestamp,
        "Content-Type": "application/json"
    }

    url = BASE_URL + path
    resp = requests.request(method, url, headers=headers, params=params, json=body, timeout=10)

    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=f"Pionex API error: {resp.text}")

    return resp.json()

@app.get("/asset", summary="取得 Pionex 現貨帳戶資訊(usdt)")
def get_pionex_asset():
    """
    查詢現貨帳戶餘額，並換算成 USDT。
    """
    data = pionex_signed_request("GET", "/api/v1/account/balances")
    print(data)

    total_usdt_estimate = 0
    result_assets = []

    # balances 在 data 裡
    balances = data.get("data", {}).get("balances", [])

    # 先取得所有交易對行情
    tickers_data = requests.get(f"{BASE_URL}/api/v1/market/tickers").json()
    tickers = {t['symbol']: float(t['close']) for t in tickers_data.get("data", {}).get("tickers", [])}

    for item in balances:
        asset = item["coin"]
        free = float(item["free"])
        locked = float(item["frozen"])
        total_amount = free + locked

        usdt_value = 0
        if asset == "USDT":
            usdt_value = total_amount
        else:
            # 嘗試找交易對 <asset>_USDT
            symbol = f"{asset}_USDT"
            price = tickers.get(symbol)
            if price is not None:
                usdt_value = total_amount * price
            else:
                usdt_value = 0  # 如果找不到交易對，USDT價值視為0

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

