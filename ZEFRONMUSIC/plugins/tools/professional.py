"""Professional product features for the music bot.

This module is deliberately independent from the player.  It provides the
management, identity, analytics and safety layer while existing play plugins
continue to own downloads and voice-chat playback.
"""

import html
import time

from pyrogram import filters
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

import config
from ZEFRONMUSIC import app
from ZEFRONMUSIC.misc import SUDOERS
from ZEFRONMUSIC.utils.admin_check import admin_check
from ZEFRONMUSIC.utils.database import (
    add_favorite, get_feature, get_feature_counts, get_favorites, get_profile,
    get_top_users, set_feature, remove_favorite, upsert_profile,
)

def _mention(user):
    return user.mention if user else "Unknown"


async def _is_owner(message):
    return bool(message.from_user and message.from_user.id == config.OWNER_ID)


async def _is_admin(message):
    return await admin_check(message) if message.chat.type in (
        ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL
    ) else await _is_owner(message)


async def _required_channel(client, message):
    channel = await get_feature(0, "force_join", config.FORCE_JOIN_CHANNEL)
    if not channel or message.chat.type == ChatType.PRIVATE:
        return True
    try:
        member = await client.get_chat_member(channel, message.from_user.id)
        if member.status in (ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR,
                             ChatMemberStatus.MEMBER):
            return True
    except Exception:
        pass
    url = config.FORCE_JOIN_URL or (
        f"https://t.me/{str(channel).lstrip('@')}" if str(channel).startswith("@") else ""
    )
    buttons = [[InlineKeyboardButton("عضویت در کانال الزامی", url=url)]] if url else []
    await message.reply_text(
        "🔒 <b>Force Join</b>\n\nPlease join the required channel, then try again.",
        reply_markup=InlineKeyboardMarkup(buttons) if buttons else None,
    )
    return False


@app.on_message(filters.group & ~filters.service, group=-20)
async def activity(client, message: Message):
    if not message.from_user or message.from_user.is_bot:
        return
    if not await _required_channel(client, message):
        try:
            await message.delete()
        except Exception:
            pass
        return
    await upsert_profile(message.from_user, message.chat.id)


@app.on_message(filters.video_chat_started, group=-19)
async def call_started(client, message: Message):
    await set_feature(message.chat.id, "active_call", True)
    await set_feature(message.chat.id, "last_call_started", time.time())


@app.on_message(filters.video_chat_ended, group=-19)
async def call_ended(client, message: Message):
    await set_feature(message.chat.id, "active_call", False)
    await set_feature(message.chat.id, "last_call_ended", time.time())


@app.on_message(filters.command(["id", "userid"]) & ~filters.service)
async def user_id(client, message: Message):
    target = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    if not target:
        return await message.reply_text("نتوانستم این کاربر را شناسایی کنم.")
    await message.reply_text(
        f"🆔 <b>اطلاعات کاربر</b>\n\n"
        f"نام: {_mention(target)}\n"
        f"شناسه کاربری: <code>{target.id}</code>\n"
        f"نام کاربری: @{html.escape(target.username) if target.username else '—'}"
    )


@app.on_message(filters.command(["profile", "me"]) & ~filters.service)
async def profile(client, message: Message):
    if not await _required_channel(client, message):
        return
    user = message.from_user
    data = await get_profile(user.id) or {}
    vip_until = await get_feature(user.id, "vip_until")
    favorites = await get_favorites(user.id, 100)
    await message.reply_text(
        f"👤 <b>پروفایل کامل</b>\n\nنام: {_mention(user)}\n"
        f"شناسه: <code>{user.id}</code>\nنام کاربری: @{html.escape(user.username) if user.username else '—'}\n"
        f"امتیاز فعالیت: <b>{data.get('messages', 0)}</b>\n"
        f"علاقه‌مندی‌ها: <b>{len(favorites)}</b>\n"
        f"وضعیت ویژه: <b>{'فعال' if vip_until and vip_until > time.time() else 'استاندارد'}</b>"
    )


@app.on_message(filters.command(["commands", "guide", "features"]) & ~filters.service)
async def command_guide(client, message: Message):
    await message.reply_text(
        "🎵 <b>راهنمای حرفه‌ای ربات موسیقی</b>\n\n"
        "🎶 <b>موسیقی:</b> /play، /vplay، /queue، /pause، /resume، /skip، /stop\n"
        "⭐ <b>شخصی:</b> /id، /profile، /fav، /unfav، /favorites\n"
        "📊 <b>آمار:</b> /topusers، /groupstats، /callstats\n"
        "🛡️ <b>امنیت:</b> /security on|off (ویژه مدیران)\n"
        "⚙️ <b>مالک:</b> /professional، /forcejoin، /setad، /vip\n\n"
        "برای راهنمای کامل پخش از /help استفاده کنید."
    )


@app.on_message(filters.command(["fav", "favorite"]) & ~filters.service)
async def favorite(client, message: Message):
    query = message.text.split(None, 1)[1].strip() if len(message.text.split(None, 1)) > 1 else ""
    if not query:
        return await message.reply_text("روش استفاده: <code>/fav نام آهنگ</code>")
    await add_favorite(message.from_user.id, query, query)
    await message.reply_text(f"⭐ <b>{html.escape(query)}</b> به علاقه‌مندی‌ها اضافه شد.")


@app.on_message(filters.command(["unfav", "unfavorite"]) & ~filters.service)
async def unfavorite(client, message: Message):
    query = message.text.split(None, 1)[1].strip() if len(message.text.split(None, 1)) > 1 else ""
    if not query:
        return await message.reply_text("روش استفاده: <code>/unfav نام آهنگ</code>")
    removed = await remove_favorite(message.from_user.id, query)
    await message.reply_text("✅ از علاقه‌مندی‌ها حذف شد." if removed else "این آهنگ در علاقه‌مندی‌های شما نیست.")


@app.on_message(filters.command(["favorites", "favourites"]) & ~filters.service)
async def favorites(client, message: Message):
    rows = await get_favorites(message.from_user.id)
    if not rows:
        return await message.reply_text("⭐ فهرست علاقه‌مندی‌های شما خالی است. از /fav نام آهنگ استفاده کنید.")
    await message.reply_text("⭐ <b>علاقه‌مندی‌های شما</b>\n\n" + "\n".join(
        f"{i}. {html.escape(row['title'])}" for i, row in enumerate(rows, 1)
    ))


@app.on_message(filters.command(["topusers", "ranking"]) & ~filters.service)
async def ranking(client, message: Message):
    rows = await get_top_users()
    if not rows:
        return await message.reply_text("📊 هنوز فعالیتی ثبت نشده است.")
    await message.reply_text("🏆 <b>رتبه‌بندی فعالیت کاربران</b>\n\n" + "\n".join(
        f"{i}. <a href='tg://user?id={row['user_id']}'>{html.escape(row.get('first_name', 'کاربر'))}</a> — {row.get('messages', 0)} پیام"
        for i, row in enumerate(rows, 1)
    ))


@app.on_message(filters.command(["groupstats", "analytics"]) & filters.group)
async def group_stats(client, message: Message):
    if not await _is_admin(message):
        return await message.reply_text("فقط مدیران می‌توانند از این فرمان استفاده کنند.")
    counts = await get_feature_counts()
    enabled = await get_feature(message.chat.id, "anti_spam", False)
    await message.reply_text(
        f"📊 <b>تحلیل {html.escape(message.chat.title or 'گروه')}</b>\n\n"
        f"کاربران ثبت‌شده: {counts['users']}\nگروه‌های موسیقی: {counts['groups']}\n"
        f"رویدادهای ثبت‌شده: {counts['events']}\nضد هرزنامه: {'فعال' if enabled else 'غیرفعال'}"
    )


@app.on_message(filters.command(["callstats"]) & filters.group)
async def call_stats(client, message: Message):
    if not await _is_admin(message):
        return await message.reply_text("فقط مدیران می‌توانند از این فرمان استفاده کنند.")
    active = await get_feature(message.chat.id, "active_call", False)
    await message.reply_text(f"📞 <b>گزارش امنیت تماس</b>\n\nتماس فعال: {'بله' if active else 'خیر'}\n"
                             f"حالت امنیتی: {'فعال' if await get_feature(message.chat.id, 'anti_spam', False) else 'غیرفعال'}")


@app.on_message(filters.command(["professional"]) & filters.private)
async def professional_panel(client, message: Message):
    if not await _is_owner(message):
        return await message.reply_text("فقط مالک ربات می‌تواند از این فرمان استفاده کند.")
    counts = await get_feature_counts()
    await message.reply_text(
        "⚙️ <b>پنل مدیریت حرفه‌ای</b>\n\n"
        f"کاربران: {counts['users']} | گروه‌ها: {counts['groups']}\n"
        f"رویدادها: {counts['events']} | کاربران ویژه: {counts['vip']}\n\n"
        "<code>/forcejoin @channel</code>\n<code>/setad your message</code>\n"
        "<code>/vip user_id days</code>\n<code>/ad</code>"
    )


@app.on_message(filters.command(["forcejoin"]) & filters.private)
async def forcejoin(client, message: Message):
    if not await _is_owner(message):
        return await message.reply_text("فقط مالک ربات می‌تواند از این فرمان استفاده کند.")
    value = message.text.split(None, 1)[1].strip() if len(message.text.split(None, 1)) > 1 else ""
    await set_feature(0, "force_join", value or None)
    await message.reply_text("✅ عضویت اجباری به‌روزرسانی شد." if value else "✅ عضویت اجباری غیرفعال شد.")


@app.on_message(filters.command(["setad"]) & filters.private)
async def set_ad(client, message: Message):
    if not await _is_owner(message):
        return await message.reply_text("فقط مالک ربات می‌تواند از این فرمان استفاده کند.")
    value = message.text.split(None, 1)[1].strip() if len(message.text.split(None, 1)) > 1 else ""
    await set_feature(0, "ad", value or None)
    await message.reply_text("✅ تبلیغ ذخیره شد." if value else "✅ تبلیغات غیرفعال شد.")


@app.on_message(filters.command(["ad"]) & ~filters.service)
async def show_ad(client, message: Message):
    ad = await get_feature(0, "ad")
    if ad:
        await message.reply_text(f"📢 <b>اطلاعیه</b>\n\n{html.escape(ad)}")


@app.on_message(filters.command(["vip"]) & filters.private)
async def vip(client, message: Message):
    if not await _is_owner(message):
        return await message.reply_text("فقط مالک ربات می‌تواند از این فرمان استفاده کند.")
    parts = message.text.split()
    if len(parts) < 3 or not parts[1].lstrip("-").isdigit() or not parts[2].isdigit():
        return await message.reply_text("روش استفاده: <code>/vip شناسه_کاربر تعداد_روز</code>")
    until = time.time() + int(parts[2]) * 86400
    await set_feature(int(parts[1]), "vip_until", until)
    await message.reply_text(f"✅ دسترسی ویژه برای <code>{parts[1]}</code> به‌مدت {parts[2]} روز فعال شد.")