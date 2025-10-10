from fastapi import FastAPI, Request, APIRouter

app = APIRouter()

@app.get("/status")
def get_status():
    return {"status": "Binance API is working!"}

@app.get("/balance")
def get_balance():
    # 這裡未連幣安API 先放假資料
    return {"BTC": 0.123, "USDT": 520.5}
