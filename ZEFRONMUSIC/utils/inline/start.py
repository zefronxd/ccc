# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (suraj08832) 🚀
# 
# This source code is under MIT License 📜
# ❌ Unauthorized forking, importing, or using this code
#    without giving proper credit will result in legal action ⚠️
# 
# 📩 DM for permission : @zefron
# ===========================================================

from pyrogram.types import InlineKeyboardButton
from pyrogram.enums import ButtonStyle

import config
from ZEFRONMUSIC import app


def start_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_1"],
                url=f"https://t.me/{app.username}?startgroup=true",
                style=ButtonStyle.SUCCESS,
            ),
            InlineKeyboardButton(
                text=_["S_B_2"],
                url=config.SUPPORT_CHAT,
                style=ButtonStyle.PRIMARY,
            ),
        ],
    ]
    return buttons


def private_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_3"],
                url=f"https://t.me/{app.username}?startgroup=true",
                style=ButtonStyle.SUCCESS,
            ),
            InlineKeyboardButton(
                text=_["S_B_4"],
                callback_data="settings_back_helper",
                style=ButtonStyle.DANGER,
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["S_B_9"],
                url=config.SUPPORT_CHAT,
                style=ButtonStyle.PRIMARY,
            ),
            InlineKeyboardButton(
                text=_["S_B_6"],
                url=config.SUPPORT_CHANNEL,
                style=ButtonStyle.PRIMARY,
            ),
        ],
    ]
    return buttons

# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (suraj08832) 😎
# 
# 🧑‍💻 Developer : https://t.me/AMP_mah
# 🔗 Source link : GitHub.com/suraj08832/Purvi-V2
# 📢 Telegram channel : t.me/JAN_AMP
# ===========================================================
