# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (suraj08832) 🚀
# 
# This source code is under MIT License 📜
# ❌ Unauthorized forking, importing, or using this code
#    without giving proper credit will result in legal action ⚠️
# 
# 📩 DM for permission : @zefron
# ===========================================================

import math
from pyrogram.types import InlineKeyboardButton
from pyrogram.enums import ButtonStyle
from ZEFRONMUSIC import app
import config
from ZEFRONMUSIC.utils.formatters import time_to_seconds
import hashlib
import hmac


def _download_signature(videoid, user_id):
    secret = config.SESSION_SECRET or config.BOT_TOKEN or ""
    return hmac.new(
        secret.encode(), f"{videoid}:{user_id}".encode(), hashlib.sha256
    ).hexdigest()[:16]


def track_markup(_, videoid, user_id, channel, fplay):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
                style=ButtonStyle.SUCCESS,
            ),
            InlineKeyboardButton(
                text=f"⬇️ دانلود {config.DOWNLOAD_PRICE_STARS} ⭐",
                callback_data=(
                    f"paidownload:{videoid}:{user_id}:"
                    f"{_download_signature(videoid, user_id)}"
                ),
                style=ButtonStyle.PRIMARY,
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
                style=ButtonStyle.PRIMARY,
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
                style=ButtonStyle.DANGER,
            )
        ],
    ]
    return buttons


def stream_markup_timer(_, chat_id, played, dur):
    played_sec = time_to_seconds(played)
    duration_sec = time_to_seconds(dur)
    percentage = (played_sec / duration_sec) * 100
    umm = math.floor(percentage)
    if 0 < umm <= 10:
        bar = "◉—————————"
    elif 10 < umm < 20:
        bar = "—◉————————"
    elif 20 <= umm < 30:
        bar = "——◉———————"
    elif 30 <= umm < 40:
        bar = "———◉——————"
    elif 40 <= umm < 50:
        bar = "————◉—————"
    elif 50 <= umm < 60:
        bar = "—————◉————"
    elif 60 <= umm < 70:
        bar = "——————◉———"
    elif 70 <= umm < 80:
        bar = "———————◉——"
    elif 80 <= umm < 95:
        bar = "————————◉—"
    else:
        bar = "—————————◉"
        
    buttons = [
        [
            InlineKeyboardButton(
                text=f"{played} {bar} {dur}",
                callback_data="GetTimer",
                style=ButtonStyle.PRIMARY,
            )
        ],
        [
             InlineKeyboardButton(text=_["STREAM_B_1"], callback_data=f"ADMIN Resume|{chat_id}", style=ButtonStyle.SUCCESS),
             InlineKeyboardButton(text=_["STREAM_B_2"], callback_data=f"ADMIN Pause|{chat_id}", style=ButtonStyle.PRIMARY),
             InlineKeyboardButton(text=_["STREAM_B_3"], callback_data=f"ADMIN Replay|{chat_id}", style=ButtonStyle.PRIMARY),
             InlineKeyboardButton(text=_["STREAM_B_4"], callback_data=f"ADMIN Skip|{chat_id}", style=ButtonStyle.PRIMARY),
             InlineKeyboardButton(text=_["STREAM_B_5"], callback_data=f"ADMIN Stop|{chat_id}", style=ButtonStyle.DANGER),
        ],
         [
             InlineKeyboardButton(text=_["STREAM_B_6"], callback_data="seek_backward_20", style=ButtonStyle.PRIMARY),
             InlineKeyboardButton(text=_["STREAM_B_8"], callback_data="seek_forward_20", style=ButtonStyle.PRIMARY)
         ],
        [
             InlineKeyboardButton(text=_["S_B_3"], url=f"https://t.me/{app.username}?startgroup=true", style=ButtonStyle.SUCCESS),
        ]
    ]
    return buttons


def stream_markup(_, chat_id):
    buttons = [
        [
             InlineKeyboardButton(text=_["STREAM_B_1"], callback_data=f"ADMIN Resume|{chat_id}", style=ButtonStyle.SUCCESS),
             InlineKeyboardButton(text=_["STREAM_B_2"], callback_data=f"ADMIN Pause|{chat_id}", style=ButtonStyle.PRIMARY),
             InlineKeyboardButton(text=_["STREAM_B_3"], callback_data=f"ADMIN Replay|{chat_id}", style=ButtonStyle.PRIMARY),
             InlineKeyboardButton(text=_["STREAM_B_4"], callback_data=f"ADMIN Skip|{chat_id}", style=ButtonStyle.PRIMARY),
             InlineKeyboardButton(text=_["STREAM_B_5"], callback_data=f"ADMIN Stop|{chat_id}", style=ButtonStyle.DANGER),
         ],
        [
             InlineKeyboardButton(text=_["STREAM_B_6"], callback_data="seek_backward_20", style=ButtonStyle.PRIMARY),
             InlineKeyboardButton(text=_["STREAM_B_8"], callback_data="seek_forward_20", style=ButtonStyle.PRIMARY)
         ],
        [
             InlineKeyboardButton(text=_["S_B_3"], url=f"https://t.me/{app.username}?startgroup=true", style=ButtonStyle.SUCCESS),
        ]
    ]
    return buttons


def playlist_markup(_, videoid, user_id, ptype, channel, fplay):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"PURVIPlaylists {videoid}|{user_id}|{ptype}|a|{channel}|{fplay}",
                style=ButtonStyle.SUCCESS,
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"PURVIPlaylists {videoid}|{user_id}|{ptype}|v|{channel}|{fplay}",
                style=ButtonStyle.PRIMARY,
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
                style=ButtonStyle.DANGER,
            ),
        ],
    ]
    return buttons


def livestream_markup(_, videoid, user_id, mode, channel, fplay):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_3"],
                callback_data=f"LiveStream {videoid}|{user_id}|{mode}|{channel}|{fplay}",
                style=ButtonStyle.SUCCESS,
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
                style=ButtonStyle.DANGER,
            ),
        ],
    ]
    return buttons


def slider_markup(_, videoid, user_id, query, query_type, channel, fplay):
    query = f"{query[:20]}"
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
                style=ButtonStyle.SUCCESS,
            ),
        ],
        [
            InlineKeyboardButton(
                text="‹",
                callback_data=f"slider B|{query_type}|{query}|{user_id}|{channel}|{fplay}",
                style=ButtonStyle.PRIMARY,
            ),
            InlineKeyboardButton(
                text=f"⬇️ دانلود {config.DOWNLOAD_PRICE_STARS} ⭐",
                callback_data=(
                    f"paidownload:{videoid}:{user_id}:"
                    f"{_download_signature(videoid, user_id)}"
                ),
                style=ButtonStyle.PRIMARY,
            ),
            InlineKeyboardButton(
                text="›",
                callback_data=f"slider F|{query_type}|{query}|{user_id}|{channel}|{fplay}",
                style=ButtonStyle.PRIMARY,
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
                style=ButtonStyle.PRIMARY,
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {query}|{user_id}",
                style=ButtonStyle.DANGER,
            )
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
