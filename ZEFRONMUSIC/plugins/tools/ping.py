# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (suraj08832) 🚀
# 
# This source code is under MIT License 📜
# ❌ Unauthorized forking, importing, or using this code
#    without giving proper credit will result in legal action ⚠️
# 
# 📩 DM for permission : @zefron
# ===========================================================

import os, shutil
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message
from config import BANNED_USERS
from ZEFRONMUSIC import app
from ZEFRONMUSIC.core.call import PURVI
from ZEFRONMUSIC.utils import bot_sys_stats
from ZEFRONMUSIC.utils.decorators.language import language
from pyrogram.enums import ButtonStyle
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from ZEFRONMUSIC.utils.inline import supp_markup
from ZEFRONMUSIC.misc import SUDOERS


def ping_markup(_):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                text=_["S_B_9"],
                url="https://t.me/JAN_AMP",
                style=ButtonStyle.SUCCESS,
            ),
            InlineKeyboardButton(
                text="• به‌روزرسانی‌ها •",
                url="https://t.me/AMP_mah",
                style=ButtonStyle.PRIMARY,
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data="close",
                style=ButtonStyle.DANGER,
            ),
        ],
    ])


@app.on_message(filters.command("ping", prefixes=["/", "!"]) & ~BANNED_USERS)
@language
async def ping_com(client, message: Message, _):
    start = datetime.now()
    response = await message.reply_photo(
        photo="https://files.catbox.moe/leaexg.jpg",
        caption=_["ping_1"].format(app.mention),
    )
    pytgping = await PURVI.ping()
    UP, CPU, RAM, DISK = await bot_sys_stats()
    resp = (datetime.now() - start).microseconds / 1000
    await response.edit_text(
        _["ping_2"].format(resp, app.mention, UP, RAM, CPU, DISK, pytgping),
        reply_markup=ping_markup(_),
    )


@app.on_message(filters.command(["eco", "co"], prefixes=["/", "e", "E"]) & filters.reply & filters.user(list(SUDOERS)))
async def eco_reply(client: Client, message):

    if not message.reply_to_message:
        await message.reply("**» ᴘʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴜsᴇʀ's ᴍᴇssᴀɢᴇ ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.**")
        return
      
    command_parts = message.text.split(" ", 1)
    if len(command_parts) < 2:
        await message.reply("**» ᴘʀᴏᴠɪᴅᴇ ᴀ ᴍᴇssᴀɢᴇ ᴀғᴛᴇʀ** `/eco` **ᴄᴏᴍᴍᴀɴᴅ.**")
        return

    reply_text = command_parts[1]

    await message.delete()
    await message.reply_to_message.reply(reply_text)



@app.on_message(filters.command("clean") & SUDOERS)
async def clean(_, message):
    A = await message.reply_text("**» ᴄʟᴇᴀɴɪɴɢ ᴛᴇᴍᴘ ᴅɪʀᴇᴄᴛᴏʀɪᴇs...**")
    dir = "downloads"
    dir1 = "cache"
    shutil.rmtree(dir)
    shutil.rmtree(dir1)
    os.mkdir(dir)
    os.mkdir(dir1)
    await A.edit("**» ᴛᴇᴍᴘ ᴅɪʀᴇᴄᴛᴏʀɪᴇs ᴀʀᴇ ᴄʟᴇᴀɴᴇᴅ ✅**")

# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (suraj08832) 😎
# 🧑‍💻 Developer : https://t.me/AMP_mah
# 🔗 Source link : GitHub.com/suraj08832/Purvi-V2
# 📢 Telegram channel : t.me/JAN_AMP
# ===========================================================
