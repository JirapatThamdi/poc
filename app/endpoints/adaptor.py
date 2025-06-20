import websockets
import json
import httpx

from fastapi import APIRouter, Request, HTTPException
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import Configuration

from app.utils.logger_init import init_logger
from app.utils import env_config as config

logger = init_logger(__name__)

router = APIRouter()

configuration = Configuration(access_token=config.CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(channel_secret=config.CHANNEL_SECRET)

async def call_chatbot_once(user_message: str) -> str:
    async with websockets.connect(config.CHATBOT_WS) as ws:
        # Authen ทุกครั้งที่เชื่อมต่อใหม่
        await ws.send(config.CHATBOT_API_KEY)
        auth_response = await ws.recv()
        if auth_response != "OK":
            raise Exception("WebSocket auth failed")

        # ส่งข้อความผู้ใช้
        await ws.send(user_message)

        # รอรับคำตอบจาก chatbot
        bot_response = await ws.recv()
        return bot_response

async def reply_message(reply_token: str, message: str):
    url = "https://api.line.me/v2/bot/message/reply"
    headers = {
        "Authorization": f"Bearer {config.CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    body = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": message}]
    }
    async with httpx.AsyncClient() as client:
        await client.post(url, headers=headers, json=body)

@router.post("/webhook")
async def line_webhook(request: Request):
    body = await request.body()
    data = json.loads(body)

    for event in data.get("events", []):
        if event["type"] == "message" and event["message"]["type"] == "text":
            user_message = event["message"]["text"]
            reply_token = event["replyToken"]

            try:
                bot_response = await call_chatbot_once(user_message)
            except Exception as e:
                print(f"Error: {e}")
                bot_response = "ขออภัย เซิร์ฟเวอร์ตอบกลับมีปัญหา"

            await reply_message(reply_token, bot_response)

    return {"status": "ok"}