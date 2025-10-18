from fastapi import APIRouter
from app.v1 import core , line_bot

binance = core.app
linebot = line_bot.app
