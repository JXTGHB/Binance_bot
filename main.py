from fastapi import FastAPI, Request
from app import routers

app = FastAPI()
app.include_router(routers.binance, prefix="/binance", tags=["Binance API"])
app.include_router(routers.linebot, prefix="/linebot", tags=["LINE Bot"])
app.include_router(routers.pionex_core, prefix="/pionex", tags=["Pionex API"])


@app.get("/")
def root():
    return {"message": "Binance x LINE Bot running on FastAPI"}
