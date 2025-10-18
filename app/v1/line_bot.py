from fastapi import APIRouter, Request, HTTPException
from app.v1 import core
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os, requests

app = APIRouter()

line_bot_api = LineBotApi(os.getenv("LINE_CHANNEL_ACCESS_TOKEN"))
handler = WebhookHandler(os.getenv("LINE_CHANNEL_SECRET"))

# @app.get("/env")
# def check_env():

#     return {
#         "LINE_CHANNEL_ACCESS_TOKEN": os.getenv("LINE_CHANNEL_ACCESS_TOKEN"),
#         "LINE_CHANNEL_SECRET": os.getenv("LINE_CHANNEL_SECRET")
#     }


@app.post("/webhook")
async def callback(request: Request):
    signature = request.headers["X-Line-Signature"]
    body = await request.body()
    try:
        handler.handle(body.decode("utf-8"), signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text.lower()
    print(f"收到訊息: {msg}")
    reply = ""
    if msg == "幣安總額":
        try:
            data = core.get_asset()
            total_usdt = data["total_usdt_estimate"]
            for asset in data["assets"]:
                reply += f"幣種:{asset['asset']}\n"
                reply += f"持幣:{float(asset['free']) + float(asset['locked'])}\n"
                reply += f"價值約{asset['usdt_value']:.2f} USDT)\n"
            reply += f"資產總值約 {total_usdt:.2f} USDT"
        except Exception as e:
            reply = f"取得資產資訊失敗: {str(e)}"
    elif msg == "活著嗎":
        try:
            data = core.get_status()
            reply += data["status"]
        except Exception as e:
            reply = "取得狀態失敗: {str(e)}"
             
    else:
        reply = "請輸入 '幣安總額' 查看現貨資產" 
    
    print(reply)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )
