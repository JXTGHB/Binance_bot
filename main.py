from fastapi import FastAPI, Request
from app import routers

app = FastAPI()
app.include_router(routers.binance, prefix="/binance", tags=["Binance API"])

@app.get("/")
def root():
    return {"message": "Binance x LINE Bot running on FastAPI"}
