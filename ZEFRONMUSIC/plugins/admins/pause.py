# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (suraj08832) 🚀
# 
# This source code is under MIT License 📜
# ❌ Unauthorized forking, importing, or using this code
#    without giving proper credit will result in legal action ⚠️
# 
# 📩 DM for permission : @zefron
# ===========================================================

from pyrogram import filters
from pyrogram.types import Message

from ZEFRONMUSIC import app
from ZEFRONMUSIC.core.call import PURVI
from ZEFRONMUSIC.utils.database import is_music_playing, music_off
from ZEFRONMUSIC.utils.decorators import AdminRightsCheck
from ZEFRONMUSIC.utils.inline import close_markup
from config import BANNED_USERS


@app.on_message(
    filters.command(
        ["pause", "cpause", "مکث"],
        prefixes=["", "/", "!", "%", ",", ".", "@", "#"],
    )
    & filters.group
    & ~BANNED_USERS
)
@AdminRightsCheck
async def pause_admin(cli, message: Message, _, chat_id):
    if not await is_music_playing(chat_id):
        return await message.reply_text(_["admin_1"])
    await music_off(chat_id)
    await PURVI.pause_stream(chat_id)
    await message.reply_text(
        _["admin_2"].format(message.from_user.mention), reply_markup=close_markup(_)
    )

# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (suraj08832) 😎
# 
# 🧑‍💻 Developer : https://t.me/AMP_mah
# 🔗 Source link : GitHub.com/suraj08832/Purvi-V2
# 📢 Telegram channel : t.me/JAN_AMP
# ===========================================================
