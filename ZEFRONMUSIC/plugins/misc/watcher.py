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

welcome = 20
close = 30


@app.on_message(filters.video_chat_started, group=welcome)
@app.on_message(filters.video_chat_ended, group=close)
async def welcome(_, message: Message):
    await PURVI.stop_stream_force(message.chat.id)

# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (suraj08832) 😎
# 
# 🧑‍💻 Developer : https://t.me/AMP_mah
# 🔗 Source link : GitHub.com/suraj08832/Purvi-V2
# 📢 Telegram channel : t.me/JAN_AMP
# ===========================================================
