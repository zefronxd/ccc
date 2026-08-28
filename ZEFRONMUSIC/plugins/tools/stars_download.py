"""Telegram Stars purchases and protected song delivery."""

import hashlib
import hmac
import re
from pathlib import Path

from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice

import config
from ZEFRONMUSIC import YouTube, app
from ZEFRONMUSIC.utils.database import has_song_purchase, save_song_purchase
from ZEFRONMUSIC.utils.formatters import time_to_seconds

SONG_ID_RE = re.compile(r"^[A-Za-z0-9_-]{3,32}$")
SIGNATURE_LENGTH = 16
FA = {
    "invalid": "این درخواست دانلود معتبر نیست.",
    "other_user": "این دکمه برای کاربر دیگری ساخته شده است.",
    "payment_required": "برای دانلود این آهنگ {0} ⭐ پرداخت کنید.",
    "payment_button": "پرداخت {0} ⭐",
    "paid": "این آهنگ قبلاً خریداری شده است ✅\nدر حال ارسال آهنگ...",
    "success": "پرداخت با موفقیت انجام شد ✅\nدر حال ارسال آهنگ...",
    "payment_failed": "پرداخت تأیید نشد. لطفاً دوباره تلاش کنید.",
    "unavailable": "فایل دانلود این آهنگ در دسترس نیست.",
    "video_unavailable": "ویدیو برای این آهنگ موجود نیست.",
    "error": "در پردازش دانلود مشکلی پیش آمد. لطفاً دوباره تلاش کنید.",
}


def _secret() -> str:
    return config.SESSION_SECRET or config.BOT_TOKEN or ""


def _signature(song_id: str, user_id: int) -> str:
    return hmac.new(
        _secret().encode(), f"{song_id}:{user_id}".encode(), hashlib.sha256
    ).hexdigest()[:SIGNATURE_LENGTH]


def _valid_request(song_id: str, user_id: str, signature: str, actual_user_id: int) -> bool:
    if not _secret() or not SONG_ID_RE.fullmatch(song_id):
        return False
    try:
        requested_user_id = int(user_id)
    except (TypeError, ValueError):
        return False
    return (
        requested_user_id == actual_user_id
        and hmac.compare_digest(signature, _signature(song_id, requested_user_id))
    )


def _payload(song_id: str, user_id: int) -> str:
    return f"song:{song_id}:{user_id}:{_signature(song_id, user_id)}"


def _parse_payload(payload: str):
    parts = (payload or "").split(":")
    if len(parts) != 4 or parts[0] != "song":
        return None
    _, song_id, user_id, signature = parts
    if not _valid_request(song_id, user_id, signature, int(user_id) if user_id.isdigit() else -1):
        return None
    return song_id, int(user_id)


async def _details(song_id: str):
    details, _ = await YouTube.track(song_id, True)
    return details


async def _send_song(message, song_id: str, details: dict, status_message=None):
    try:
        file_path, downloaded = await YouTube.download(
            song_id, status_message or message, videoid=True
        )
        if not downloaded or not file_path or not Path(file_path).is_file():
            if status_message:
                await status_message.edit_text(FA["unavailable"])
            else:
                await message.reply_text(FA["unavailable"])
            return False

        duration = details.get("duration_min") or ""
        duration_seconds = time_to_seconds(duration) if duration else 0
        await message.reply_audio(
            audio=file_path,
            caption=f"<b>{details.get('title', 'آهنگ')}</b>\n"
            f"هنرمند: {details.get('artist') or 'نامشخص'}\n"
            f"مدت: {duration or 'نامشخص'}",
            title=details.get("title"),
            performer=details.get("artist") or "نامشخص",
            duration=duration_seconds,
            thumb=details.get("thumb"),
            parse_mode=ParseMode.HTML,
        )
        if status_message:
            await status_message.delete()
        return True
    except Exception:
        if status_message:
            await status_message.edit_text(FA["error"])
        else:
            await message.reply_text(FA["error"])
        return False


@app.on_callback_query(filters.regex(r"^paidownload:"))
async def paid_download_callback(client, callback_query):
    raw = callback_query.data.split(":", 3)
    if len(raw) != 4:
        return await callback_query.answer(FA["invalid"], show_alert=True)
    _, song_id, requested_user_id, signature = raw
    user_id = callback_query.from_user.id
    if not _valid_request(song_id, requested_user_id, signature, user_id):
        return await callback_query.answer(FA["invalid"], show_alert=True)

    await callback_query.answer()
    try:
        details = await _details(song_id)
    except Exception:
        return await callback_query.message.reply_text(FA["error"])

    if await has_song_purchase(user_id, song_id):
        status = await callback_query.message.reply_text(FA["paid"])
        await _send_song(callback_query.message, song_id, details, status)
        return

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(
            FA["payment_button"].format(config.DOWNLOAD_PRICE_STARS),
            callback_data=f"confirmdownload:{song_id}:{user_id}:{_signature(song_id, user_id)}",
        )]]
    )
    await callback_query.message.reply_text(
        FA["payment_required"].format(config.DOWNLOAD_PRICE_STARS),
        reply_markup=keyboard,
    )


@app.on_callback_query(filters.regex(r"^confirmdownload:"))
async def create_stars_invoice(client, callback_query):
    parts = callback_query.data.split(":")
    if len(parts) != 4:
        return await callback_query.answer(FA["invalid"], show_alert=True)
    _, song_id, user_id, signature = parts
    if not _valid_request(song_id, user_id, signature, callback_query.from_user.id):
        return await callback_query.answer(FA["invalid"], show_alert=True)
    if await has_song_purchase(callback_query.from_user.id, song_id):
        return await callback_query.answer("این آهنگ قبلاً خریداری شده است ✅", show_alert=True)

    try:
        details = await _details(song_id)
        await client.send_invoice(
            chat_id=callback_query.message.chat.id,
            title=(details.get("title") or "دانلود آهنگ")[:32],
            description="دانلود قانونی آهنگ با پرداخت Telegram Stars."[:255],
            payload=_payload(song_id, callback_query.from_user.id),
            provider_token="",
            currency="XTR",
            prices=[LabeledPrice("دانلود آهنگ", config.DOWNLOAD_PRICE_STARS)],
        )
        await callback_query.answer()
    except Exception:
        await callback_query.answer(FA["error"], show_alert=True)


@app.on_pre_checkout_query()
async def verify_stars_checkout(client, query):
    parsed = _parse_payload(query.invoice_payload)
    valid = bool(parsed and query.from_user.id == parsed[1])
    valid = valid and query.currency == "XTR" and query.total_amount == config.DOWNLOAD_PRICE_STARS
    await query.answer(
        ok=valid,
        error_message=None if valid else FA["payment_failed"],
    )


@app.on_message(filters.successful_payment)
async def stars_payment_received(client, message):
    payment = message.successful_payment
    parsed = _parse_payload(payment.invoice_payload)
    if not parsed or parsed[1] != message.from_user.id:
        return await message.reply_text(FA["payment_failed"])
    song_id, user_id = parsed
    try:
        details = await _details(song_id)
        await save_song_purchase(
            user_id,
            song_id,
            payment.telegram_payment_charge_id,
            payment.total_amount,
            payment.currency,
            {
                "title": details.get("title"),
                "artist": details.get("artist"),
                "duration": details.get("duration_min"),
                "thumbnail": details.get("thumb"),
            },
        )
        status = await message.reply_text(FA["success"])
        await _send_song(message, song_id, details, status)
    except Exception:
        await message.reply_text(FA["error"])