from fastapi import APIRouter, Request, HTTPException
from app.v1 import core, pionex_core
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
            binance_data = core.get_asset()
            reply += "=== Binance ===\n"
            reply += format_assets(binance_data)
            reply += f"\n總值: {binance_data['total_usdt_estimate']:.2f} USDT"
        except Exception as e:
            reply = f"取得 Binance 資產失敗: {e}"

    elif msg == "派網總額":
        try:
            pionex_data = pionex_core.get_pionex_asset()
            reply += "=== Pionex ===\n"
            reply += format_assets(pionex_data)
            reply += f"\n總值: {pionex_data['total_usdt_estimate']:.2f} USDT"
        except Exception as e:
            reply = f"取得 Pionex 資產失敗: {e}"

    elif msg == "全部總額":
        # 全部才一次 call 兩個
        try:
            binance_data = core.get_asset()
        except Exception as e:
            binance_data = {"total_usdt_estimate": 0, "assets": []}

        try:
            pionex_data = pionex_core.get_pionex_asset()
        except Exception as e:
            pionex_data = {"total_usdt_estimate": 0, "assets": []}

        reply += "=== Binance ===\n"
        reply += format_assets(binance_data)
        reply += f"\n總值: {binance_data['total_usdt_estimate']:.2f} USDT\n\n"

        reply += "=== Pionex ===\n"
        reply += format_assets(pionex_data)
        reply += f"\n總值: {pionex_data['total_usdt_estimate']:.2f} USDT\n\n"

        total = binance_data['total_usdt_estimate'] + pionex_data['total_usdt_estimate']
        reply += f"=== 全部總值: {total:.2f} USDT ==="

    elif msg == "活著嗎":
        try:
            data = core.get_status()
            reply = data.get("status", "狀態未知")
        except Exception as e:
            reply = f"取得狀態失敗: {e}"

    else:
        reply = "請輸入以下指令:\n- 幣安總額\n- 派網總額\n- 全部總額"

    #print(reply)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )


def format_assets(data):
    """
    將資產資料格式化成易讀字串
    """
    lines = []
    for asset in data["assets"]:
        lines.append(
            f"幣種: {asset['asset']}\n"
            f"持幣: {asset['free'] + asset['locked']:.4f}\n"
            f"價值約: {asset['usdt_value']:.2f} USDT\n"
        )
    return "\n".join(lines)