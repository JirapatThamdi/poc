import json
import time
import asyncio
import websockets
import httpx

from fastapi import APIRouter, Request, HTTPException
from linebot.v3 import WebhookHandler
from linebot.v3.messaging import (
    Configuration,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    AudioMessageContent
)

from app.utils.logger_init import init_logger
from app.utils import env_config as config

logger = init_logger(__name__)
router = APIRouter()

LINE_CONTENT_URL = "https://api-data.line.me/v2/bot/message/{message_id}/content"
configuration = Configuration(access_token=config.CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(channel_secret=config.CHANNEL_SECRET)

chatbot_session = {
    "ws": None,
    "last_used": 0.0
}

SESSION_TIMEOUT = 60


# --- Chatbot WebSocket session management ---
async def get_or_create_chatbot_ws():
    now = time.time()
    if chatbot_session["ws"] and now - chatbot_session["last_used"] < SESSION_TIMEOUT:
        chatbot_session["last_used"] = now
        return chatbot_session["ws"]

    if chatbot_session["ws"]:
        try:
            await chatbot_session["ws"].close()
        except:
            pass

    ws = await websockets.connect(config.CHATBOT_URL)
    await ws.send(config.CHATBOT_API_KEY)
    auth_response = await ws.recv()
    auth_response_json = json.loads(auth_response)
    if auth_response_json["success"] is not True:
        raise Exception("WebSocket auth failed")

    chatbot_session["ws"] = ws
    chatbot_session["last_used"] = now
    return ws


async def call_chatbot_once(user_message: str) -> str:
    try:
        ws = await get_or_create_chatbot_ws()
        await ws.send(user_message)
        return await ws.recv()
    except Exception as e:
        logger.warning(f"WebSocket error: {e}, reconnecting...")
        chatbot_session["ws"] = None
        ws = await get_or_create_chatbot_ws()
        await ws.send(user_message)
        return await ws.recv()


# --- LINE Messaging API: Reply ---
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


# --- Speech to Text ---
async def download_audio(message_id: str) -> bytes:
    url = LINE_CONTENT_URL.format(message_id=message_id)
    headers = {
        "Authorization": f"Bearer {config.CHANNEL_ACCESS_TOKEN}"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Cannot fetch audio")
        return response.content


async def speech_to_text(audio_bytes: bytes) -> str:
    # TODO: Replace this mock with real speech-to-text service (e.g., Whisper)
    return "คุณพูดอะไรบางอย่างในคลิปเสียง"


async def handle_audio_message(message_id: str) -> str:
    try:
        audio_bytes = await download_audio(message_id)
        return await speech_to_text(audio_bytes)
    except Exception as e:
        logger.error(f"Voice message handling failed: {e}")
        return "ขออภัย ไม่สามารถประมวลผลเสียงได้"


# --- Async message processing ---
async def process_message(user_message: str, reply_token: str):
    try:
        bot_response = await call_chatbot_once(user_message)
    except Exception as e:
        logger.error(f"Chatbot error: {e}")
        bot_response = "ขออภัย เซิร์ฟเวอร์ตอบกลับมีปัญหา"
    await reply_message(reply_token, bot_response)


async def process_audio_message(message_id: str, reply_token: str):
    try:
        user_message = await handle_audio_message(message_id)
        bot_response = await call_chatbot_once(user_message)
    except Exception as e:
        logger.error(f"Voice/audio chatbot error: {e}")
        bot_response = "ขออภัย ไม่สามารถประมวลผลเสียงได้"
    await reply_message(reply_token, bot_response)


# --- Webhook Entry Point ---
@router.post("/webhook")
async def callback(request: Request):
    signature = request.headers.get("X-Line-Signature")
    body = await request.body()
    body_str = body.decode("utf-8")

    try:
        handler.handle(body_str, signature)
    except Exception as e:
        logger.error(f"Invalid signature or handler error: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")

    return {"status": "ok"}


# --- Event Handlers ---
@handler.add(MessageEvent, message=TextMessageContent)
def handle_text(event: MessageEvent):
    user_message = event.message.text
    reply_token = event.reply_token
    asyncio.create_task(process_message(user_message, reply_token))


@handler.add(MessageEvent, message=AudioMessageContent)
def handle_audio(event: MessageEvent):
    message_id = event.message.id
    reply_token = event.reply_token
    asyncio.create_task(process_audio_message(message_id, reply_token))
