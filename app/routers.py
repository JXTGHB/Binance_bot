from fastapi import APIRouter
from app.v1 import core , line_bot, pionex_core

binance = core.app
linebot = line_bot.app
pionex_core = pionex_core.app
