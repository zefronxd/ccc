# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (suraj08832) 🚀
# 
# This source code is under MIT License 📜
# ❌ Unauthorized forking, importing, or using this code
#    without giving proper credit will result in legal action ⚠️
# 
# 📩 DM for permission : @zefron
# ===========================================================

import random
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from config import LOGGER_ID as LOG_GROUP_ID
from ZEFRONMUSIC import app


photo = [
    "https://telegra.ph/file/1949480f01355b4e87d26.jpg",
    "https://telegra.ph/file/3ef2cc0ad2bc548bafb30.jpg",
    "https://telegra.ph/file/a7d663cd2de689b811729.jpg",
    "https://telegra.ph/file/6f19dc23847f5b005e922.jpg",
    "https://telegra.ph/file/2973150dd62fd27a3a6ba.jpg",
]


@app.on_message(filters.new_chat_members, group=2)
async def join_watcher(_, message: Message):
    chat = message.chat
    link = await app.export_chat_invite_link(chat.id)

    username = f"@{chat.username}" if chat.username else "ᴘʀɪᴠᴀᴛᴇ ɢʀᴏᴜᴘ"

    for member in message.new_chat_members:
        if member.id == app.id:
            count = await app.get_chat_members_count(chat.id)

            msg = (
                "<b>📝 ᴍᴜsɪᴄ ʙᴏᴛ ᴀᴅᴅᴇᴅ ɪɴ ᴀ ɴᴇᴡ ɢʀᴏᴜᴘ</b>\n"
                "<b>____________________________________</b>\n\n"
                f"<b>📌 ᴄʜᴀᴛ ɴᴀᴍᴇ :</b> {chat.title}\n"
                f"<b>🍂 ᴄʜᴀᴛ ɪᴅ :</b> {chat.id}\n"
                f"<b>🔐 ᴄʜᴀᴛ ᴜsᴇʀɴᴀᴍᴇ :</b> {username}\n"
                f"<b>🛰 ᴄʜᴀᴛ ʟɪɴᴋ : <a href='{link}'>ᴄʟɪᴄᴋ ʜᴇʀᴇ</a></b>\n"
                f"<b>📈 ɢʀᴏᴜᴘ ᴍᴇᴍʙᴇʀs :</b> {count}\n"
                f"<b>🤔 ᴀᴅᴅᴇᴅ ʙʏ :</b> {message.from_user.mention}"
            )

            await app.send_photo(
                LOG_GROUP_ID,
                photo=random.choice(photo),
                caption=msg,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("sᴇᴇ ɢʀᴏᴜᴘ 👀", url=link)]]
                )
            )


@app.on_message(filters.left_chat_member)
async def on_left_chat_member(_, message: Message):
    if (await app.get_me()).id == message.left_chat_member.id:
        remove_by = (
            message.from_user.mention if message.from_user else "ᴜɴᴋɴᴏᴡɴ ᴜsᴇʀ"
        )

        chat_id = message.chat.id
        title = message.chat.title

        left_msg = (
            "<b>❖ #𝐋ᴇғᴛ_𝐆ʀᴏᴜᴘ</b>\n\n"
            f"🏷 <b>ᴄʜᴀᴛ ᴛɪᴛʟᴇ :</b> {title}\n"
            f"🆔 <b>ᴄʜᴀᴛ ɪᴅ :</b> {chat_id}\n"
            f"👤 <b>ʀᴇᴍᴏᴠᴇᴅ ʙʏ :</b> {remove_by}\n\n"
            f"🤖 <b>ʙᴏᴛ :</b> @{app.username}"
        )

        add_link = f"https://t.me/{app.username}?startgroup=true"

        await app.send_photo(
            LOG_GROUP_ID,
            photo=random.choice(photo),
            caption=left_msg,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("✙ ʌᴅᴅ ϻє ɪη ʏσυʀ ɢʀσυᴘ ✙", url=add_link)]]
            )
        )

        from ZEFRONMUSIC.core.userbot import assistants
        from ZEFRONMUSIC.utils.database import get_client

        for num in assistants:
            try:
                client = await get_client(num)
                await client.leave_chat(chat_id)
            except:
                pass

# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (suraj08832) 😎
# 
# 🧑‍💻 Developer : https://t.me/AMP_mah
# 🔗 Source link : GitHub.com/suraj08832/Purvi-V2
# 📢 Telegram channel : t.me/JAN_AMP
# ===========================================================
