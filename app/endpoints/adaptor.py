import json
import websockets
import httpx
from fastapi import APIRouter, Request, HTTPException
from openai import OpenAI

from linebot.v3.messaging import Configuration
from app.utils.logger_init import init_logger
from app.utils import env_config as config
from app.core.service_manager import ServiceManager

logger = init_logger(__name__)
router = APIRouter()

configuration = Configuration(access_token=config.CHANNEL_ACCESS_TOKEN)
LINE_CONTENT_URL = "https://api-data.line.me/v2/bot/message/{message_id}/content"

openai_client = OpenAI(api_key=config.OPENAI_API_KEY)
service_manager = ServiceManager()

async def call_chatbot_once(user_message: str) -> str:
    chatbot_ws = 'wss://' + config.CHATBOT_URL + '/ws/live-chat'
    async with websockets.connect(chatbot_ws) as ws:
        await ws.send(config.CHATBOT_API_KEY)
        auth_response = await ws.recv()

        # TODO: Check if the auth response is valid
        logger.debug(f"Auth response: {auth_response}")
        if auth_response != "OK":
            raise Exception("WebSocket auth failed")

        await ws.send(user_message)
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
    """
    Transcribe audio bytes to text using OpenAI's speech-to-text service.
    """
    try:
        transcribed_text = await service_manager.call("speech2text",
                                                      audio_file=audio_bytes,
                                                      client=openai_client)
        return transcribed_text
    except Exception as e:
        logger.error(f"Speech to text conversion failed: {e}")
        raise e


async def handle_audio_message(message_id: str) -> str:
    try:
        audio_bytes = await download_audio(message_id)
        text = await speech_to_text(audio_bytes)
        return text
    except Exception as e:
        logger.error(f"Voice message handling failed: {e}")
        return "ขออภัย ไม่สามารถประมวลผลเสียงได้"


@router.post("/webhook")
async def line_webhook(request: Request):
    body = await request.body()
    data = json.loads(body)

    for event in data.get("events", []):
        message = event.get("message", {})
        reply_token = event.get("replyToken")
        message_type = message.get("type")

        if message_type == "text":
            user_message = message.get("text")

        elif message_type == "audio":
            message_id = message.get("id")
            user_message = await handle_audio_message(message_id)

        else:
            logger.info(f"Message type '{message_type}' not supported.")
            continue

        try:
            bot_response = await call_chatbot_once(user_message)
        except Exception as e:
            logger.error(f"Chatbot error: {e}")
            bot_response = "ขออภัย เซิร์ฟเวอร์ตอบกลับมีปัญหา"

        await reply_message(reply_token, bot_response)

    return {"status": "ok"}
