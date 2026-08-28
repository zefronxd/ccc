# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (suraj08832) 🚀
# 
# This source code is under MIT License 📜
# ❌ Unauthorized forking, importing, or using this code
#    without giving proper credit will result in legal action ⚠️
# 
# 📩 DM for permission : @zefron
# ===========================================================

from typing import Union

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ButtonStyle

from ZEFRONMUSIC import app


def help_pannel(_, START: Union[bool, int] = None):
    first = [InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data=f"close", style=ButtonStyle.DANGER)]
    second = [
        InlineKeyboardButton(
            text=_["BACK_BUTTON"],
            callback_data=f"settingsback_helper",
            style=ButtonStyle.PRIMARY,
        ),
    ]
    mark = second if START else first
    upl = InlineKeyboardMarkup(
        [
            #[
            #    InlineKeyboardButton(text="ηєᴡ ʀᴛϻᴘ sᴛʀєᴧϻɪηɢ", callback_data="new_cb")],
            
            [
                InlineKeyboardButton(
                    text=_["H_B_25"],
                    callback_data="help_callback hb1",
                    style=ButtonStyle.SUCCESS,
                ),
                InlineKeyboardButton(
                    text=_["H_B_26"],
                    callback_data="help_callback hb2",
                    style=ButtonStyle.PRIMARY,
                ),
                InlineKeyboardButton(
                    text=_["H_B_28"],
                    callback_data="help_callback hb3",
                    style=ButtonStyle.DANGER,
                ),
            ],
            [
                InlineKeyboardButton(
                    text=_["H_B_27"],
                    callback_data="help_callback hb4",
                    style=ButtonStyle.DANGER,
                ),
                InlineKeyboardButton(
                    text=_["H_B_31"],
                    callback_data="help_callback hb5",
                    style=ButtonStyle.SUCCESS,
                ),
                InlineKeyboardButton(
                    text=_["H_B_29"],
                    callback_data="help_callback hb6",
                    style=ButtonStyle.PRIMARY,
                ),
            ],
            [
                InlineKeyboardButton(
                    text=_["H_B_33"],
                    callback_data="help_callback hb7",
                    style=ButtonStyle.PRIMARY,
                ),
                InlineKeyboardButton(
                    text=_["H_B_30"],
                    callback_data="help_callback hb8",
                    style=ButtonStyle.DANGER,
                ),
                InlineKeyboardButton(
                    text=_["H_B_32"],
                    callback_data="help_callback hb9",
                    style=ButtonStyle.SUCCESS,
                ),
            ],
            [
                InlineKeyboardButton(
                    text=_.get("PRO_ADS_BUTTON", "📢 تبلیغات"),
                    callback_data="feature_help ads",
                    style=ButtonStyle.SUCCESS,
                ),
                InlineKeyboardButton(
                    text=_.get("PRO_FORCEJOIN_BUTTON", "🔒 عضویت اجباری"),
                    callback_data="feature_help forcejoin",
                    style=ButtonStyle.PRIMARY,
                ),
            ],
            [
                InlineKeyboardButton(
                    text=_.get("PRO_USERINFO_BUTTON", "👤 اطلاعات کاربر"),
                    callback_data="feature_help userinfo",
                    style=ButtonStyle.PRIMARY,
                ),
                InlineKeyboardButton(
                    text=_.get("PRO_ANALYTICS_BUTTON", "📊 تحلیل و آمار"),
                    callback_data="feature_help analytics",
                    style=ButtonStyle.SUCCESS,
                ),
            ],
            [
                InlineKeyboardButton(
                    text=_.get("PRO_SECURITY_BUTTON", "🛡️ امنیت"),
                    callback_data="feature_help security",
                    style=ButtonStyle.DANGER,
                ),
                InlineKeyboardButton(
                    text=_.get("PRO_VIP_BUTTON", "⭐ علاقه‌مندی و ویژه"),
                    callback_data="feature_help vip",
                    style=ButtonStyle.SUCCESS,
                ),
            ],
            [
                InlineKeyboardButton(
                    text=_.get("PRO_CALLS_BUTTON", "📞 آمار تماس"),
                    callback_data="feature_help calls",
                    style=ButtonStyle.PRIMARY,
                ),
                InlineKeyboardButton(
                    text=_.get("PRO_GUIDE_BUTTON", "📚 راهنمای فرمان‌ها"),
                    callback_data="feature_help guide",
                    style=ButtonStyle.PRIMARY,
                ),
            ],
            mark,
        ]
    )
    return upl


def help_back_markup(_):
    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=_["BACK_BUTTON"],
                    callback_data=f"settings_back_helper",
                    style=ButtonStyle.PRIMARY,
                ),
            ]
        ]
    )
    return upl


def private_help_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_4"],
                url=f"https://t.me/{app.username}?start=help",
                style=ButtonStyle.SUCCESS,
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
