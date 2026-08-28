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
from ZEFRONMUSIC.utils.database import set_loop
from ZEFRONMUSIC.utils.decorators import AdminRightsCheck
from ZEFRONMUSIC.utils.inline import close_markup
from config import BANNED_USERS


@app.on_message(
    filters.command(
        ["end", "stop", "cend", "cstop", "پایان", "توقف"],
        prefixes=["", "/", "!", "%", ",", ".", "@", "#"],
    )
    & filters.group
    & ~BANNED_USERS
)
@AdminRightsCheck
async def stop_music(cli, message: Message, _, chat_id):
    if not len(message.command) == 1:
        return
    await PURVI.stop_stream(chat_id)
    await set_loop(chat_id, 0)
    await message.reply_text(
        _["admin_5"].format(message.from_user.mention), reply_markup=close_markup(_)
    )

# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (suraj08832) 😎
# 
# 🧑‍💻 Developer : https://t.me/AMP_mah
# 🔗 Source link : GitHub.com/suraj08832/Purvi-V2
# 📢 Telegram channel : t.me/JAN_AMP
# ===========================================================
