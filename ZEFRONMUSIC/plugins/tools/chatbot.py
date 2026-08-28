"""Optional Persian/English chat companion.

The plugin is intentionally independent from the music handlers. It only
answers private messages, replies to the bot, or messages mentioning the bot.
Set GROQ_API_KEY in Replit Secrets to enable it.
"""

import asyncio
import os
import tempfile
from collections import defaultdict, deque
from urllib.parse import quote

import aiohttp
from pyrogram import filters
from pyrogram.enums import ChatAction, ChatType
from pyrogram.types import Message

from ZEFRONMUSIC import app
from ZEFRONMUSIC.core.mongo import mongodb
from ZEFRONMUSIC.logging import LOGGER


GROQ_API_URL = os.getenv(
    "GROQ_API_URL",
    "https://api.groq.com/openai/v1/chat/completions",
).strip()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b").strip()

# Keep moderation credentials separate from the chatbot API credentials.
SIGHTENGINE_URL = os.getenv(
    "SIGHTENGINE_API_URL",
    "https://api.sightengine.com/1.0/check.json",
).strip()
SIGHTENGINE_API_USER = os.getenv("SIGHTENGINE_API_USER", "").strip()
SIGHTENGINE_API_SECRET = os.getenv("SIGHTENGINE_API_SECRET", "").strip()
SIGHTENGINE_MAX_FILE_SIZE = int(
    os.getenv("SIGHTENGINE_MAX_FILE_SIZE", str(20 * 1024 * 1024))
)
MAX_HISTORY = 8
history = defaultdict(lambda: deque(maxlen=MAX_HISTORY))
chatbot_memory = mongodb.chatbot_memory
logger = LOGGER(__name__)


def _is_chat_request(message: Message) -> bool:
    text = (message.text or "").strip().lower()
    if not text or text.startswith("/"):
        return False
    if message.chat.type == ChatType.PRIVATE:
        return True
    if message.reply_to_message and message.reply_to_message.from_user:
        if message.reply_to_message.from_user.id == getattr(app, "id", None):
            return True
    username = getattr(app, "username", None)
    return bool(
        "قیماقی" in text
        or text == "riruru"
        or (username and f"@{username.lower()}" in text)
    )


def _clean_mention(text: str) -> str:
    username = getattr(app, "username", None)
    if username:
        text = text.replace(f"@{username}", "").replace(f"@{username.lower()}", "")
    return " ".join(text.split()).strip()


def _extract_text(data):
    if isinstance(data, dict):
        if isinstance(data.get("candidates"), list) and data["candidates"]:
            return _extract_text(data["candidates"][0])
        if isinstance(data.get("content"), dict):
            return _extract_text(data["content"])
        if isinstance(data.get("parts"), list) and data["parts"]:
            return _extract_text(data["parts"][0])
        if isinstance(data.get("message"), dict):
            return _extract_text(data["message"])
        for key in ("text", "response", "message", "content", "output"):
            if isinstance(data.get(key), str):
                return data[key]
        if isinstance(data.get("choices"), list) and data["choices"]:
            return _extract_text(data["choices"][0])
    return None


async def _load_history(user_id: int):
    """Load the user's recent conversation from MongoDB."""
    try:
        record = await chatbot_memory.find_one({"user_id": user_id})
        items = record.get("messages", []) if record else []
        history[user_id].extend(
            item for item in items
            if isinstance(item, dict) and item.get("role") in {"user", "assistant"}
        )
    except Exception:
        # A database hiccup must not stop a live chat response.
        return


async def _save_history(user_id: int):
    try:
        await chatbot_memory.update_one(
            {"user_id": user_id},
            {"$set": {"messages": list(history[user_id])}},
            upsert=True,
        )
    except Exception:
        return


async def _translate_to_persian(text: str) -> str:
    """Use Google Translate to keep every chatbot response Persian."""
    if not text:
        return text
    url = (
        "https://translate.googleapis.com/translate_a/single"
        f"?client=gtx&sl=auto&tl=fa&dt=t&q={quote(text)}"
    )
    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                if response.status != 200:
                    return text
                data = await response.json()
        translated = "".join(
            part[0] for part in data[0] if isinstance(part, list) and part and part[0]
        )
        return translated.strip() or text
    except (aiohttp.ClientError, asyncio.TimeoutError, ValueError, IndexError, TypeError):
        return text


async def _ask_model(user_text: str, user_id: int):
    if not GROQ_API_KEY:
        return None
    if not history[user_id]:
        await _load_history(user_id)
    messages = list(history[user_id])
    messages.append({"role": "user", "content": user_text})
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Your name is قیماقی. You are a friendly Telegram chatbot. "
                    "Reply naturally and briefly in under 40 words. "
                    "The final response will be translated to Persian."
                ),
            },
            *[
                {"role": item["role"], "content": item["content"]}
                for item in messages
            ],
        ],
        "temperature": 1,
        "max_completion_tokens": 2048,
        "top_p": 1,
        "reasoning_effort": "medium",
        "stream": False,
    }
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    reply = None
    try:
        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                GROQ_API_URL,
                json=payload,
                headers=headers,
            ) as response:
                if response.status == 200:
                    reply = _extract_text(await response.json())
                else:
                    error_body = (await response.text())[:300]
                    logger.warning(
                        "Groq API returned HTTP %s: %s",
                        response.status,
                        error_body,
                    )
    except (aiohttp.ClientError, asyncio.TimeoutError, ValueError):
        logger.warning("Groq API request failed")
    if not reply:
        return None
    reply = await _translate_to_persian(reply.strip())
    history[user_id].append({"role": "user", "content": user_text})
    history[user_id].append({"role": "assistant", "content": reply.strip()})
    await _save_history(user_id)
    return reply.strip()


def _moderated_media(message: Message):
    """Return supported Telegram media and a filename suffix."""
    if message.photo:
        return message.photo, ".jpg"
    if message.animation:
        return message.animation, ".mp4"
    if message.video:
        return message.video, ".mp4"
    if message.video_note:
        return message.video_note, ".mp4"
    if message.sticker:
        file_name = (message.sticker.file_name or "").lower()
        if file_name.endswith((".tgs", ".webm")):
            return None
        return message.sticker, ".webp"
    return None


def _is_nsfw(result: dict) -> bool:
    """Apply a conservative explicit-content threshold to nudity-2.0 scores."""
    nudity = result.get("nudity", {})
    if not isinstance(nudity, dict):
        return False
    scores = (
        nudity.get("raw", 0),
        nudity.get("sexual_activity", 0),
        nudity.get("sexual_display", 0),
        nudity.get("erotica", 0),
    )
    return any(isinstance(score, (int, float)) and score >= 0.60 for score in scores)


async def _sightengine_nsfw(message: Message) -> bool:
    """Classify media without deleting anything when the service is unavailable."""
    if not SIGHTENGINE_API_USER or not SIGHTENGINE_API_SECRET:
        return False
    media = _moderated_media(message)
    if not media:
        return False
    media_object, suffix = media
    file_size = getattr(media_object, "file_size", None)
    if file_size and file_size > SIGHTENGINE_MAX_FILE_SIZE:
        return False

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
            temp_path = temp_file.name
        downloaded_path = await message.download(file_name=temp_path)
        if not downloaded_path:
            return False
        form = aiohttp.FormData()
        form.add_field("api_user", SIGHTENGINE_API_USER)
        form.add_field("api_secret", SIGHTENGINE_API_SECRET)
        form.add_field("models", "nudity-2.0")
        with open(downloaded_path, "rb") as media_file:
            form.add_field(
                "media",
                media_file,
                filename=os.path.basename(downloaded_path),
                content_type="application/octet-stream",
            )
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(SIGHTENGINE_URL, data=form) as response:
                    if response.status != 200:
                        logger.warning(
                            "Sightengine returned HTTP %s while moderating media",
                            response.status,
                        )
                        return False
                    result = await response.json()
        return result.get("status") == "success" and _is_nsfw(result)
    except (aiohttp.ClientError, asyncio.TimeoutError, OSError, ValueError, TypeError):
        logger.warning("Sightengine media moderation failed")
        return False
    finally:
        if temp_path:
            try:
                os.unlink(temp_path)
            except OSError:
                pass


@app.on_message(
    filters.group
    & ~filters.bot
    & ~filters.service
    & (
        filters.photo
        | filters.sticker
        | filters.animation
        | filters.video
        | filters.video_note
    ),
    group=-60,
)
async def nsfw_media_handler(client, message: Message):
    """Delete explicit human media from groups when Sightengine identifies it."""
    if not message.from_user or message.from_user.is_bot:
        return
    if await _sightengine_nsfw(message):
        try:
            await message.delete()
            logger.info("Deleted NSFW media in chat %s", message.chat.id)
        except Exception:
            logger.warning("Could not delete NSFW media in chat %s", message.chat.id)


@app.on_message(filters.text & ~filters.bot, group=3)
async def chatbot_handler(client, message: Message):
    if not _is_chat_request(message):
        return
    text = _clean_mention(message.text or "")
    if not text:
        return
    try:
        await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    except Exception:
        pass
    reply = await _ask_model(text, message.from_user.id)
    if reply:
        await message.reply_text(reply)
    else:
        await message.reply_text(
            "متأسفانه الان نمی‌توانم پاسخ بدهم؛ لطفاً اتصال API قیماقی را بررسی کنید."
        )