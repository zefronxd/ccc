"""Per-group Telegram protection system.

All state that must survive a restart is stored in MongoDB. High-frequency
message counters intentionally stay in memory and are bounded/expired.
"""

import html
import re
import time
import asyncio
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone

from pyrogram import filters
from pyrogram.enums import ChatMemberStatus, ChatType, ParseMode
from pyrogram.errors import RPCError
from pyrogram.types import ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup, Message

import config
from ZEFRONMUSIC import app
from ZEFRONMUSIC.utils.database import (
    add_security_violation,
    get_security_settings,
    get_security_user,
    set_security_setting,
    update_security_user,
)

URL_RE = re.compile(r"(?:https?://|www\.|t\.me/|telegram\.me/|telegram\.dog/)[^\s]+", re.I)
_activity = defaultdict(deque)
_sticker_activity = defaultdict(deque)
_joins = defaultdict(deque)
_last_notice = {}
_protected_members = {}
STICKER_FLOOD_LIMIT = 8
STICKER_FLOOD_WINDOW = 5

FA = {
    "denied": "❌ شما اجازه استفاده از این دستور را ندارید.",
    "bot_perms": "❌ ربات دسترسی کافی برای انجام این عملیات را ندارد.",
    "spam": "🛡️ پیام شما به دلیل اسپم حذف شد.",
    "link": "🚫 ارسال لینک در این گروه مجاز نیست.",
    "flood": "🌊 پیام شما به دلیل ارسال بیش از حد حذف شد.",
    "badword": "🚫 این پیام به دلیل استفاده از واژه ممنوع حذف شد.",
    "new": "🛡️ شما به‌عنوان عضو جدید، برای مدت کوتاهی تحت محافظت هستید.",
    "warn": "⚠️ شما یک اخطار دریافت کردید.",
    "raid": "🚨 احتمال حمله گروهی شناسایی شد.\nحالت محافظت اضطراری فعال شد.",
    "normal": "🟢 حالت عادی گروه فعال شد.",
}

LOCKS = {"links", "media", "stickers", "gifs", "videos", "photos", "voice", "forwards"}
MUTE_DURATIONS = {"1m": 60, "5m": 300, "10m": 600, "1h": 3600, "1d": 86400}


async def _is_admin(client, message, user_id=None):
    user_id = user_id or (message.from_user.id if message.from_user else 0)
    if user_id == config.OWNER_ID:
        return True
    try:
        member = await client.get_chat_member(message.chat.id, user_id)
        return member.status in (ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR)
    except RPCError:
        return False


async def _trusted(client, message, user_id):
    if user_id == config.OWNER_ID:
        return True
    try:
        member = await client.get_chat_member(message.chat.id, user_id)
        return member.status in (ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR)
    except RPCError:
        settings = await get_security_settings(message.chat.id)
        return user_id in settings["whitelist"]


async def _bot_can(client, chat_id, permission):
    try:
        member = await client.get_chat_member(chat_id, "me")
        return member.status == ChatMemberStatus.OWNER or bool(getattr(member.privileges, permission, False))
    except RPCError:
        return False


async def _safe_restrict(client, message, user_id, seconds):
    if await _trusted(client, message, user_id):
        return False
    if not await _bot_can(client, message.chat.id, "can_restrict_members"):
        return False
    try:
        await client.restrict_chat_member(
            message.chat.id,
            user_id,
            permissions=ChatPermissions(can_send_messages=False),
            until_date=datetime.now(timezone.utc) + timedelta(seconds=max(30, seconds)),
        )
        return True
    except RPCError:
        return False


async def _warn(client, message, reason):
    settings = await get_security_settings(message.chat.id)
    if not settings["warning_system"] or await _trusted(client, message, message.from_user.id):
        return
    current = await get_security_user(message.chat.id, message.from_user.id)
    count = int(current.get("warning_count", 0)) + 1
    await update_security_user(message.chat.id, message.from_user.id, warning_count=count)
    await add_security_violation(message.chat.id, message.from_user.id, reason)
    if count >= int(settings["warning_limit"]):
        if settings["warning_action"] == "ban" and await _bot_can(client, message.chat.id, "can_restrict_members"):
            await client.ban_chat_member(message.chat.id, message.from_user.id)
        else:
            await _safe_restrict(client, message, message.from_user.id, int(settings["mute_duration"]))
        count_text = f"🔇 اخطارها به حد نصاب رسید؛ شما {int(settings['mute_duration']) // 60} دقیقه محدود شدید."
    else:
        count_text = f"{FA['warn']}\n⚠️ تعداد اخطارهای شما: {count} از {settings['warning_limit']}"
    try:
        asyncio.create_task(
            _temporary_notice(
                client,
                message.chat.id,
                count_text,
                user=message.from_user,
            )
        )
    except RPCError:
        pass


async def _log(client, message, event, action):
    """Send a privacy-safe event to the existing bot log chat."""
    if not config.LOGGER_ID:
        return
    try:
        await client.send_message(
            config.LOGGER_ID,
            f"🛡️ <b>رویداد امنیتی</b>\nگروه: <code>{message.chat.id}</code>\n"
            f"کاربر: <code>{message.from_user.id}</code>\n"
            f"دلیل: {html.escape(event)}\nاقدام: {html.escape(action)}",
        )
    except RPCError:
        pass


async def _temporary_notice(client, chat_id, text, user=None, delay=60):
    """Show a tagged Persian HTML notice and remove it after one minute."""
    try:
        if user:
            name = html.escape(user.first_name or "کاربر")
            text = f'👤 <a href="tg://user?id={user.id}">{name}</a>\n{text}'
        notice = await client.send_message(chat_id, text, parse_mode=ParseMode.HTML)
        await asyncio.sleep(delay)
        await notice.delete()
    except RPCError:
        pass


async def _delete_and_warn(client, message, reason, text):
    try:
        await message.delete()
    except RPCError:
        return
    await _warn(client, message, reason)
    key = (message.chat.id, message.from_user.id, reason)
    if time.monotonic() - _last_notice.get(key, 0) > 8:
        _last_notice[key] = time.monotonic()
        asyncio.create_task(
            _temporary_notice(
                client,
                message.chat.id,
                text,
                user=message.from_user,
            )
        )


def _media_kind(message):
    if message.sticker: return "stickers"
    if message.animation: return "gifs"
    if message.video: return "videos"
    if message.photo: return "photos"
    if message.voice: return "voice"
    if message.video_note: return "videos"
    return None


@app.on_message(filters.photo & filters.group & ~filters.service, group=-52)
async def delete_group_photos(client, message: Message):
    """This protection is unconditional: no member may post group photos."""
    if not message.from_user or message.from_user.is_bot:
        return
    try:
        await message.delete()
    except RPCError:
        return
    asyncio.create_task(
        _temporary_notice(
            client,
            message.chat.id,
            "🚫 ارسال تصویر در این گروه مجاز نیست؛ پیام حذف شد.",
            user=message.from_user,
        )
    )


@app.on_message(filters.group & ~filters.service, group=-50)
async def protection_guard(client, message: Message):
    user = message.from_user
    if not user or user.is_bot or not message.chat or message.chat.type not in (ChatType.GROUP, ChatType.SUPERGROUP):
        return
    settings = await get_security_settings(message.chat.id)
    if await _trusted(client, message, user.id):
        return
    now = time.monotonic()
    key = (message.chat.id, user.id)
    bucket = _activity[key]
    while bucket and now - bucket[0][0] > max(settings["spam_window"], settings["flood_window"], 10):
        bucket.popleft()
    text = message.text or message.caption or ""
    bucket.append((now, text.strip().casefold()))
    joined_at = _protected_members.get(key)
    new_member = joined_at and time.time() < joined_at + settings["new_member_duration"]
    if joined_at and not new_member:
        _protected_members.pop(key, None)
    if settings["enabled"] or settings["raid_mode"] or settings["new_member_protection"] or settings["locked"]:
        if (settings["anti_links"] or "links" in settings["locked"] or
                (new_member and settings["new_member_links"]) or
                (settings["raid_mode"] and new_member)) and URL_RE.search(text):
            await _delete_and_warn(client, message, "Link", FA["link"])
            return await _log(client, message, "Link", "Delete")
        kind = _media_kind(message)
        sticker_key = (message.chat.id, user.id)
        sticker_bucket = _sticker_activity[sticker_key]
        while sticker_bucket and now - sticker_bucket[0] > 30:
            sticker_bucket.popleft()
        if kind == "stickers":
            sticker_bucket.append(now)
        sticker_spam = kind == "stickers" and len(sticker_bucket) >= settings["spam_limit"]
        if kind in settings["locked"] or ("media" in settings["locked"] and kind) or (kind and settings["media_lock"]) or (
            new_member and settings["new_member_media"] and kind
        ):
            await _delete_and_warn(client, message, f"Media:{kind}", "🚫 ارسال این نوع رسانه در گروه مجاز نیست.")
            return await _log(client, message, f"Media:{kind}", "Delete")
        if message.forward_date and "forwards" in settings["locked"]:
            await _delete_and_warn(client, message, "Forward", "🚫 ارسال پیام‌های فورواردی در گروه مجاز نیست.")
            return await _log(client, message, "Forward", "Delete")
        words = {str(w).casefold() for w in settings["bad_words"]}
        if settings["bad_words_filter"] and words and any(w in text.casefold().split() for w in words):
            await _delete_and_warn(client, message, "Bad word", FA["badword"])
            return await _log(client, message, "Bad word", "Delete")
        sticker_flood = (
            kind == "stickers"
            and settings["anti_flood"]
            and sum(1 for stamp in sticker_bucket if now - stamp <= STICKER_FLOOD_WINDOW)
            >= STICKER_FLOOD_LIMIT
        )
        if sticker_flood:
            await _delete_and_warn(client, message, "Sticker flood", FA["flood"])
            await _safe_restrict(client, message, user.id, settings["mute_duration"])
            await _log(client, message, "Sticker flood", "Mute")
            return
        spam_window = settings["spam_window"]
        recent = [item for item in bucket if now - item[0] <= spam_window]
        repeated = len(recent) >= settings["spam_limit"] and len({item[1] for item in recent}) == 1
        rapid = len(recent) >= settings["spam_limit"]
        if (settings["anti_spam"] or (new_member and settings["new_member_spam"])) and (
            repeated or rapid or sticker_spam
        ):
            await _delete_and_warn(client, message, "Spam", FA["spam"])
            await _safe_restrict(client, message, user.id, settings["mute_duration"])
            await _log(client, message, "Spam", "Mute")
            return
        flood_window = settings["flood_window"]
        flood = sum(1 for item in bucket if now - item[0] <= flood_window)
        if (settings["anti_flood"] or (new_member and settings["new_member_flood"]) or settings["raid_mode"]) and flood >= settings["flood_limit"]:
            await _delete_and_warn(client, message, "Flood", FA["flood"])
            await _safe_restrict(client, message, user.id, settings["mute_duration"])
            await _log(client, message, "Flood", "Mute")


@app.on_message(filters.new_chat_members, group=-49)
async def new_member_protection(client, message: Message):
    settings = await get_security_settings(message.chat.id)
    join_bucket = _joins[message.chat.id]
    now = time.monotonic()
    while join_bucket and now - join_bucket[0] > settings["raid_window"]:
        join_bucket.popleft()
    join_bucket.extend([now] * len(message.new_chat_members))
    if settings["anti_raid"] and len(join_bucket) >= settings["raid_join_limit"] and not settings["raid_mode"]:
        await set_security_setting(message.chat.id, "raid_mode", True)
        await set_security_setting(message.chat.id, "enabled", True)
        try:
            await message.reply_text(FA["raid"], quote=False)
        except RPCError:
            pass
        settings = await get_security_settings(message.chat.id)
    if not settings["new_member_protection"] and not settings["raid_mode"]:
        return
    for member in message.new_chat_members:
        if member.is_bot or await _trusted(client, message, member.id):
            continue
        _protected_members[(message.chat.id, member.id)] = time.time()
        if settings["new_member_media"] or settings["raid_mode"]:
            try:
                await _safe_restrict(client, message, member.id, settings["new_member_duration"])
            except RPCError:
                pass
    try:
        await message.reply_text(FA["new"], quote=False)
    except RPCError:
        pass


async def _admin_command(client, message):
    if not await _is_admin(client, message):
        await message.reply_text(FA["denied"])
        return False
    if not await _bot_can(client, message.chat.id, "can_delete_messages"):
        await message.reply_text(FA["bot_perms"])
        return False
    return True


def _panel(settings):
    def mark(key): return "✅" if settings.get(key) else "❌"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"ضد اسپم {mark('anti_spam')}", callback_data="sec:toggle:anti_spam"),
         InlineKeyboardButton(f"ضد لینک {mark('anti_links')}", callback_data="sec:toggle:anti_links")],
        [InlineKeyboardButton(f"ضد Flood {mark('anti_flood')}", callback_data="sec:toggle:anti_flood"),
         InlineKeyboardButton(f"ضد Raid {mark('anti_raid')}", callback_data="sec:toggle:anti_raid")],
        [InlineKeyboardButton(f"اعضای جدید {mark('new_member_protection')}", callback_data="sec:toggle:new_member_protection"),
         InlineKeyboardButton(f"فیلتر کلمات {mark('bad_words_filter')}", callback_data="sec:toggle:bad_words_filter")],
        [InlineKeyboardButton("🔄 بروزرسانی", callback_data="sec:panel")],
    ])


@app.on_message(filters.command(["security", "protection"]) & filters.group)
async def security_panel(client, message: Message):
    if not await _is_admin(client, message):
        return await message.reply_text(FA["denied"])
    settings = await get_security_settings(message.chat.id)
    parts = message.text.split()
    if len(parts) > 1 and parts[1].lower() in ("on", "off"):
        enabled = parts[1].lower() == "on"
        await set_security_setting(message.chat.id, "enabled", enabled)
        # The simple switch is useful out of the box; the panel still permits
        # each protection family to be disabled independently.
        for key in ("anti_spam", "anti_links", "anti_flood"):
            await set_security_setting(message.chat.id, key, enabled)
        settings = await get_security_settings(message.chat.id)
    await message.reply_text("🛡️ <b>تنظیمات امنیتی گروه</b>\n\n"
                             f"وضعیت کلی: {'✅ فعال' if settings['enabled'] else '❌ غیرفعال'}",
                             reply_markup=_panel(settings))


@app.on_message(filters.command("setsecurity") & filters.group)
async def set_security(client, message: Message):
    if not await _admin_command(client, message):
        return
    if len(message.command) != 3:
        return await message.reply_text(
            "روش استفاده: <code>/setsecurity نام_تنظیم مقدار</code>\n"
            "تنظیمات: warning_limit, mute_duration, spam_limit, spam_window, "
            "flood_limit, flood_window, new_member_duration, raid_join_limit, raid_window"
        )
    key, raw = message.command[1].lower(), message.command[2]
    limits = {
        "warning_limit": (1, 20), "mute_duration": (60, 86400),
        "spam_limit": (2, 100), "spam_window": (1, 300),
        "flood_limit": (2, 100), "flood_window": (1, 300),
        "new_member_duration": (30, 86400), "raid_join_limit": (2, 1000),
        "raid_window": (5, 3600),
    }
    if key not in limits or not raw.isdigit() or not (limits[key][0] <= int(raw) <= limits[key][1]):
        return await message.reply_text("❌ نام تنظیم یا مقدار آن معتبر نیست.")
    await set_security_setting(message.chat.id, key, int(raw))
    await message.reply_text("✅ تنظیم امنیتی با موفقیت ذخیره شد.")


@app.on_callback_query(filters.regex(r"^sec:(panel|toggle:(anti_spam|anti_links|anti_flood|anti_raid|new_member_protection|bad_words_filter))$"))
async def security_callback(client, query):
    if not query.message or not await _is_admin(client, query.message, query.from_user.id):
        return await query.answer(FA["denied"], show_alert=True)
    if query.data.startswith("sec:toggle:"):
        key = query.data.split(":")[-1]
        settings = await get_security_settings(query.message.chat.id)
        await set_security_setting(query.message.chat.id, key, not settings[key])
    settings = await get_security_settings(query.message.chat.id)
    await query.answer("تنظیمات ذخیره شد.")
    await query.edit_message_reply_markup(_panel(settings))


@app.on_message(filters.command("raidmode") & filters.group)
async def raidmode(client, message: Message):
    if not await _admin_command(client, message): return
    await set_security_setting(message.chat.id, "raid_mode", True)
    await set_security_setting(message.chat.id, "enabled", True)
    await message.reply_text(FA["raid"])


@app.on_message(filters.command("normalmode") & filters.group)
async def normalmode(client, message: Message):
    if not await _admin_command(client, message): return
    await set_security_setting(message.chat.id, "raid_mode", False)
    await message.reply_text(FA["normal"])


@app.on_message(filters.command(["warn", "warnings", "resetwarn", "mute"]) & filters.group)
async def warning_commands(client, message: Message):
    if not await _admin_command(client, message): return
    target = message.reply_to_message.from_user if message.reply_to_message else None
    if not target:
        return await message.reply_text("برای این دستور، پیام کاربر را ریپلای کنید.")
    if await _trusted(client, message, target.id):
        return await message.reply_text("❌ مدیران و مالک گروه قابل اخطار نیستند.")
    if message.command[0] == "resetwarn":
        await update_security_user(message.chat.id, target.id, warning_count=0)
        return await message.reply_text("✅ اخطارهای کاربر پاک شد.")
    current = await get_security_user(message.chat.id, target.id)
    if message.command[0] == "mute":
        duration = MUTE_DURATIONS.get(message.command[1].lower(), 600) if len(message.command) > 1 else 600
        if not await _safe_restrict(client, message, target.id, duration):
            return await message.reply_text(FA["bot_perms"])
        return await message.reply_text(f"🔇 {target.mention} به مدت {duration // 60} دقیقه محدود شد.")
    if message.command[0] == "warnings":
        settings = await get_security_settings(message.chat.id)
        return await message.reply_text(f"⚠️ تعداد اخطارهای {target.mention}: {current.get('warning_count', 0)} از {settings['warning_limit']}")
    warning_count = int(current.get("warning_count", 0)) + 1
    settings = await get_security_settings(message.chat.id)
    await update_security_user(message.chat.id, target.id, warning_count=warning_count)
    if warning_count >= int(settings["warning_limit"]):
        await _safe_restrict(client, message, target.id, int(settings["mute_duration"]))
    await message.reply_text(f"{FA['warn']} {target.mention}")


def _target_id(message):
    target = message.reply_to_message.from_user if message.reply_to_message else None
    if target: return target.id
    if len(message.command) > 1 and message.command[1].lstrip("-").isdigit():
        return int(message.command[1])
    return None


@app.on_message(filters.command(["whitelist", "unwhitelist", "whitelistusers"]) & filters.group)
async def whitelist_commands(client, message: Message):
    if not await _admin_command(client, message): return
    settings = await get_security_settings(message.chat.id)
    if message.command[0] == "whitelistusers":
        ids = settings["whitelist"]
        return await message.reply_text("✅ کاربران مجاز:\n" + ("\n".join(f"• <code>{i}</code>" for i in ids) if ids else "فهرست خالی است."))
    user_id = _target_id(message)
    if not user_id: return await message.reply_text("کاربر را ریپلای کنید یا شناسه او را بنویسید.")
    ids = set(settings["whitelist"])
    ids.discard(user_id) if message.command[0] == "unwhitelist" else ids.add(user_id)
    await set_security_setting(message.chat.id, "whitelist", list(ids))
    await message.reply_text("✅ فهرست کاربران مجاز به‌روزرسانی شد.")


@app.on_message(filters.command(["addword", "delword", "listwords"]) & filters.group)
async def bad_words(client, message: Message):
    if not await _admin_command(client, message): return
    settings = await get_security_settings(message.chat.id)
    if message.command[0] == "listwords":
        return await message.reply_text("🚫 واژه‌های ممنوع:\n" + ("\n".join(f"• {html.escape(w)}" for w in settings["bad_words"]) if settings["bad_words"] else "فهرست خالی است."))
    word = message.text.split(None, 1)[1].strip().casefold() if len(message.text.split(None, 1)) > 1 else ""
    if not word or len(word) > 64: return await message.reply_text("یک واژه معتبر وارد کنید.")
    words = set(settings["bad_words"])
    words.discard(word) if message.command[0] == "delword" else words.add(word)
    await set_security_setting(message.chat.id, "bad_words", list(words))
    await set_security_setting(message.chat.id, "bad_words_filter", True)
    await message.reply_text("✅ فهرست واژه‌های ممنوع به‌روزرسانی شد.")


@app.on_message(filters.command(["lock", "unlock"]) & filters.group)
async def content_lock(client, message: Message):
    if not await _admin_command(client, message): return
    kind = message.command[1].lower() if len(message.command) > 1 else ""
    if kind not in LOCKS: return await message.reply_text("نوع قفل معتبر نیست.")
    settings = await get_security_settings(message.chat.id)
    locked = set(settings["locked"])
    if message.command[0] == "lock": locked.add(kind)
    else: locked.discard(kind)
    await set_security_setting(message.chat.id, "locked", list(locked))
    await message.reply_text(f"✅ قفل {kind} {'فعال' if message.command[0] == 'lock' else 'غیرفعال'} شد.")