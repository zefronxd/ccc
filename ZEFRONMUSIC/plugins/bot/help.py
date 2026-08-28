# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (suraj08832) 🚀
# 
# This source code is under MIT License 📜
# ❌ Unauthorized forking, importing, or using this code
#    without giving proper credit will result in legal action ⚠️
# 
# 📩 DM for permission : @zefron
# ===========================================================

from typing import Union
import random, config 
from pyrogram import filters, types, Client, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, InputMediaPhoto, Message
from ZEFRONMUSIC import app
from ZEFRONMUSIC.utils import help_pannel
from ZEFRONMUSIC.utils.database import get_lang
from ZEFRONMUSIC.utils.decorators.language import LanguageStart, languageCB
from ZEFRONMUSIC.utils.inline.help import help_back_markup, private_help_panel
from config import BANNED_USERS, START_IMG_URL, SUPPORT_CHAT
from strings import get_string, helpers

FA_HELP_ABOUT = """
**➻ <u>درباره {0}</u>
─────────────────────────
❖ ربات حرفه‌ای موسیقی برای گروه‌ها و کانال‌های تلگرام
● نوشته‌شده با پایتون و پایگاه‌داده MongoDB
● ساخته‌شده با Pyrogram و PyTgCalls
─────────────────────────
✦ سریع، پایدار و همیشه در دسترس
✦ منبع امن و خصوصی، بدون اشتراک‌گذاری داده‌ها
─────────────────────────
➤ [تماس با سازنده](https://t.me/AMP_mah)
➤ [وضعیت ربات و ربات‌های بیشتر](https://t.me/JAN_AMP)
─────────────────────────**
"""

FA_HELP_SUPPORT = """
**❖ <u>پشتیبانی {0}</u>

● پشتیبانی شبانه‌روزی برای ربات
● گفتگوهای پاک، پایدار و بدون خطا
● مشکلی دارید؟ با ما تماس بگیرید.
─────────────────────────
❖ [کانال به‌روزرسانی](https://t.me/JAN_AMP)
❖ [گروه پشتیبانی](https://t.me/AMP_mah)
─────────────────────────**
"""

START_IMG = [
    "https://files.catbox.moe/x5lytj.jpg",
    "https://files.catbox.moe/psya34.jpg",
    "https://files.catbox.moe/leaexg.jpg",
    "https://files.catbox.moe/b0e4vk.jpg",
    "https://files.catbox.moe/1b1wap.jpg",
    "https://files.catbox.moe/ommjjk.jpg",
    "https://files.catbox.moe/onurxm.jpg",
    "https://files.catbox.moe/97v75k.jpg",
    "https://files.catbox.moe/t833zy.jpg",
    "https://files.catbox.moe/472piq.jpg",
    "https://files.catbox.moe/qwjeyk.jpg",
    "https://files.catbox.moe/t0hopv.jpg",
    "https://files.catbox.moe/u5ux0j.jpg",
    "https://files.catbox.moe/h1yk4w.jpg",
    "https://files.catbox.moe/gl5rg8.jpg",
]


class BUTTONS(object):
    ABUTTON = [
    [
        InlineKeyboardButton("˹ پشتیبانی ˼", url="https://t.me/JAN_AMP", style=enums.ButtonStyle.SUCCESS),
        InlineKeyboardButton("˹ به‌روزرسانی‌ها ˼", url="https://t.me/AMP_mah", style=enums.ButtonStyle.PRIMARY),
    ],
    [
        InlineKeyboardButton("˹ مالک ˼", user_id=config.OWNER_ID, style=enums.ButtonStyle.PRIMARY),
        InlineKeyboardButton("• بازگشت •", callback_data="settingsback_helper", style=enums.ButtonStyle.DANGER),
    ]
]

    INFO_BUTTON = [
    [
        InlineKeyboardButton("˹ مخزن کد ˼", callback_data="gib_source", style=enums.ButtonStyle.SUCCESS),
        InlineKeyboardButton("˹ API یوتیوب ˼", callback_data="bot_info_data", style=enums.ButtonStyle.PRIMARY),
        InlineKeyboardButton("˹ زبان ˼", callback_data="LG", style=enums.ButtonStyle.PRIMARY),
    ],
    [
        InlineKeyboardButton("˹ حریم خصوصی ˼", url="https://graph.org/zefron-bot-06-24", style=enums.ButtonStyle.PRIMARY),
        InlineKeyboardButton("• بازگشت •", callback_data="settingsback_helper", style=enums.ButtonStyle.DANGER),
    ]
    ]


@app.on_message(filters.command(["help"]) & filters.private & ~BANNED_USERS)
@app.on_callback_query(filters.regex("settings_back_helper") & ~BANNED_USERS)
async def helper_private(
    client: app, update: Union[types.Message, types.CallbackQuery]
):
    is_callback = isinstance(update, types.CallbackQuery)
    if is_callback:
        try:
            await update.answer()
        except:
            pass
        chat_id = update.message.chat.id
        language = await get_lang(chat_id)
        _ = get_string(language)
        keyboard = help_pannel(_, True)
        await update.edit_message_text(
            _["help_1"].format(SUPPORT_CHAT), reply_markup=keyboard
        )
    else:
        try:
            await update.delete()
        except:
            pass
        language = await get_lang(update.chat.id)
        _ = get_string(language)
        keyboard = help_pannel(_)
        await update.reply_photo(
            photo=START_IMG_URL,
            caption=_["help_1"].format(SUPPORT_CHAT),
            reply_markup=keyboard,
        )


@app.on_message(filters.command(["help"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def help_com_group(client, message: Message, _):
    keyboard = private_help_panel(_)
    await message.reply_text(_["help_2"], reply_markup=InlineKeyboardMarkup(keyboard))


@app.on_callback_query(filters.regex("abot_cb") & ~BANNED_USERS)
async def helper_cb(client, CallbackQuery):
    bot = await client.get_me()
    bot_mention = bot.mention

    await CallbackQuery.edit_message_text(
        FA_HELP_ABOUT.format(bot_mention),
        reply_markup=InlineKeyboardMarkup(BUTTONS.INFO_BUTTON),
    )

@app.on_callback_query(filters.regex("sbot_cb") & ~BANNED_USERS)
async def helper_cb(client, CallbackQuery):
    bot = await client.get_me()
    bot_mention = bot.mention

    await CallbackQuery.edit_message_text(
        FA_HELP_SUPPORT.format(bot_mention),
        reply_markup=InlineKeyboardMarkup(BUTTONS.ABUTTON),
    )


@app.on_callback_query(filters.regex("back_cb") & ~BANNED_USERS)
async def back_cb(client, CallbackQuery):
    photo = random.choice(START_IMG)
    bot = await client.get_me()
    bot_mention = bot.mention

    await CallbackQuery.edit_message_media(
        media=InputMediaPhoto(
            media=photo,
            caption=FA_HELP_ABOUT.format(bot_mention)
        ),
        reply_markup=InlineKeyboardMarkup(BUTTONS.INFO_BUTTON)
    )

@app.on_callback_query(filters.regex("help_callback") & ~BANNED_USERS)
@languageCB
async def helper_cb(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    cb = callback_data.split(None, 1)[1]
    keyboard = help_back_markup(_)
    if _["name"] == "🇮🇷 فارسی":
        fa_pages = {
            "hb1": (
                "🛠️ <b>مدیریت پخش موسیقی</b>\n\n"
                "مدیران گروه می‌توانند پخش جاری و صف آهنگ‌ها را کنترل کنند.\n\n"
                "<code>/pause</code> توقف موقت پخش\n"
                "<code>/resume</code> ادامه پخش متوقف‌شده\n"
                "<code>/skip</code> رفتن به آهنگ بعدی\n"
                "<code>/stop</code> پایان پخش و پاک کردن صف\n"
                "<code>/queue</code> نمایش صف پخش\n"
                "<code>/loop</code> تکرار آهنگ جاری\n"
                "<code>/shuffle</code> جابه‌جایی آهنگ‌های صف\n"
                "<code>/seek زمان</code> رفتن به زمان مشخص\n"
                "<code>/speed</code> تغییر سرعت پخش"
            ),
            "hb2": (
                "👥 <b>مدیریت کاربران مجاز</b>\n\n"
                "کاربران مجاز می‌توانند بعضی از فرمان‌های مدیریتی ربات را بدون "
                "داشتن دسترسی مدیر گروه استفاده کنند.\n\n"
                "➕ <b>افزودن کاربر مجاز</b>\n"
                "با ریپلای به پیام کاربر:\n"
                "<code>/auth</code>\n"
                "یا با شناسه/یوزرنیم:\n"
                "<code>/auth 123456789</code>\n"
                "<code>/auth @username</code>\n\n"
                "➖ <b>حذف کاربر مجاز</b>\n"
                "با ریپلای یا شناسه/یوزرنیم کاربر:\n"
                "<code>/unauth</code>\n"
                "<code>/unauth 123456789</code>\n"
                "<code>/unauth @username</code>\n\n"
                "📋 <b>نمایش فهرست کاربران مجاز</b>\n"
                "<code>/authusers</code>\n\n"
                "⚠️ فقط مدیران گروه می‌توانند کاربر مجاز اضافه یا حذف کنند. "
                "فهرست هر گروه جداگانه است و حداکثر ۲۵ کاربر را پشتیبانی می‌کند."
            ),
            "hb3": (
                "📢 <b>پیام همگانی</b>\n\n"
                "این قابلیت برای ارسال یک پیام به گفتگوهای ثبت‌شده ربات است.\n"
                "<code>/broadcast متن</code> ارسال پیام همگانی\n"
                "همچنین می‌توانید یک پیام را ریپلای کرده و <code>/broadcast</code> بزنید.\n\n"
                "این فرمان فقط برای کاربران ارشد ربات فعال است."
            ),
            "hb4": (
                "🚫 <b>فهرست سیاه و مسدودسازی</b>\n\n"
                "<code>/blacklistchat chat_id</code> جلوگیری از استفاده ربات در گروه\n"
                "<code>/whitelistchat chat_id</code> خارج کردن گروه از فهرست سیاه\n"
                "<code>/blacklistedchat</code> نمایش گروه‌های مسدودشده\n\n"
                "<code>/block</code> مسدود کردن کاربر از ربات\n"
                "<code>/unblock</code> رفع مسدودی کاربر\n"
                "<code>/blockedusers</code> نمایش کاربران مسدودشده\n\n"
                "مدیریت این بخش فقط در اختیار کاربران ارشد ربات است."
            ),
            "hb5": (
                "🎵 <b>فرمان‌های پخش</b>\n\n"
                "<code>/play نام آهنگ</code> پخش صوتی آهنگ\n"
                "<code>/vplay نام آهنگ</code> پخش ویدیویی آهنگ\n"
                "<code>/playforce</code> توقف پخش فعلی و شروع درخواست جدید\n"
                "<code>/channelplay</code> اتصال پخش به کانال\n"
                "<code>/cplay</code> پخش آهنگ در چت صوتی کانال\n\n"
                "برای جست‌وجو می‌توانید نام آهنگ یا لینک آن را ارسال کنید."
            ),
            "hb6": (
                "🌐 <b>مسدودسازی سراسری</b>\n\n"
                "<code>/gban</code> مسدود کردن کاربر در گروه‌های تحت مدیریت ربات\n"
                "<code>/ungban</code> برداشتن مسدودی سراسری\n"
                "<code>/gbannedusers</code> نمایش فهرست کاربران مسدودشده\n\n"
                "این قابلیت فقط برای کاربران ارشد ربات است و روی گروه‌های سرو‌شده اعمال می‌شود."
            ),
            "hb7": (
                "📞 <b>مدیریت تماس‌های صوتی</b>\n\n"
                "<code>/activevoice</code> نمایش تماس‌های صوتی فعال\n"
                "<code>/activevideo</code> نمایش تماس‌های ویدیویی فعال\n"
                "<code>/ac</code> نمایش تماس‌های فعال توسط ربات\n"
                "<code>/autoend enable|disable</code> پایان خودکار پخش در نبود شنونده\n"
                "<code>/autoleave enable|disable</code> خروج خودکار دستیار\n\n"
                "این فرمان‌ها برای مدیریت وضعیت تماس و دستیارهای پخش هستند."
            ),
            "hb8": (
                "🔧 <b>تعمیر و نگهداری ربات</b>\n\n"
                "<code>/logs</code> دریافت گزارش‌های ربات\n"
                "<code>/logger enable|disable</code> فعال یا غیرفعال کردن ثبت رویدادها\n"
                "<code>/maintenance enable|disable</code> فعال کردن حالت تعمیرات\n\n"
                "در حالت تعمیرات، فقط کاربران مجاز می‌توانند از قابلیت‌های مدیریتی استفاده کنند."
            ),
            "hb9": (
                "ℹ️ <b>فرمان‌های پایه</b>\n\n"
                "<code>/start</code> شروع کار با ربات\n"
                "<code>/help</code> باز کردن منوی راهنما\n"
                "<code>/ping</code> بررسی سرعت پاسخ ربات\n"
                "<code>/settings</code> تنظیمات گروه\n"
                "<code>/privacy</code> مشاهده حریم خصوصی\n"
                "<code>/stats</code> آمار کلی ربات\n"
                "<code>/lang</code> تغییر زبان رابط کاربری"
            ),
            "hb10": (
                "🧩 <b>ابزارهای بیشتر</b>\n\n"
                "در این بخش قابلیت‌های تکمیلی ربات برای مدیریت، پروفایل، "
                "آمار، امنیت و امکانات ویژه قرار دارد.\n\n"
                "برای مشاهده توضیح هر قابلیت، یکی از دکمه‌های ویژگی را در منوی "
                "راهنما انتخاب کنید."
            ),
            "hb11": (
                "🔎 <b>جست‌وجو و دانلود</b>\n\n"
                "<code>/play نام آهنگ</code> جست‌وجو و پخش آهنگ\n"
                "می‌توانید لینک یوتیوب یا نام خواننده و آهنگ را ارسال کنید.\n"
                "نتیجه مناسب را انتخاب کنید تا آهنگ در صف پخش قرار بگیرد.\n\n"
                "برای پخش ویدیویی از <code>/vplay</code> استفاده کنید."
            ),
            "hb12": (
                "📋 <b>صف و فهرست پخش</b>\n\n"
                "<code>/queue</code> نمایش آهنگ‌های منتظر در صف\n"
                "<code>/loop</code> تکرار آهنگ یا تنظیم تکرار\n"
                "<code>/shuffle</code> تصادفی کردن ترتیب صف\n"
                "<code>/stop</code> پاک کردن صف و پایان پخش\n\n"
                "مدیران می‌توانند صف پخش گروه را کنترل کنند."
            ),
            "hb13": (
                "🔐 <b>امنیت و کنترل دسترسی</b>\n\n"
                "دسترسی فرمان‌های مدیریتی بر اساس مدیران گروه، مالک گروه و "
                "کاربران مجاز بررسی می‌شود.\n"
                "برای کنترل کامل حفاظت گروه از دکمه «🛡️ امنیت» استفاده کنید.\n\n"
                "تنظیمات هر گروه مستقل است و روی گروه‌های دیگر اثری ندارد."
            ),
            "hb14": (
                "🎶 <b>پخش آهنگ</b>\n\n"
                "نام آهنگ، نام خواننده یا لینک را همراه فرمان زیر ارسال کنید:\n"
                "<code>/play نام آهنگ</code>\n\n"
                "آهنگ پس از آماده‌سازی در تماس صوتی گروه پخش می‌شود. "
                "برای پخش ویدیویی از <code>/vplay</code> استفاده کنید."
            ),
            "hb15": (
                "⚡ <b>کنترل سرعت پخش</b>\n\n"
                "مدیران گروه می‌توانند سرعت پخش آهنگ جاری را تغییر دهند:\n"
                "<code>/speed</code>\n"
                "<code>/playback</code>\n\n"
                "این قابلیت فقط روی پخش جاری اعمال می‌شود و برای آهنگ بعدی "
                "دوباره به حالت عادی برمی‌گردد."
            ),
        }
        return await CallbackQuery.edit_message_text(
            fa_pages.get(cb, "راهنمای این بخش در دسترس نیست."),
            reply_markup=keyboard,
        )
    if cb == "hb1":
        await CallbackQuery.edit_message_text(helpers.HELP_1, reply_markup=keyboard)
    elif cb == "hb2":
        await CallbackQuery.edit_message_text(helpers.HELP_2, reply_markup=keyboard)
    elif cb == "hb3":
        await CallbackQuery.edit_message_text(helpers.HELP_3, reply_markup=keyboard)
    elif cb == "hb4":
        await CallbackQuery.edit_message_text(helpers.HELP_4, reply_markup=keyboard)
    elif cb == "hb5":
        await CallbackQuery.edit_message_text(helpers.HELP_5, reply_markup=keyboard)
    elif cb == "hb6":
        await CallbackQuery.edit_message_text(helpers.HELP_6, reply_markup=keyboard)
    elif cb == "hb7":
        await CallbackQuery.edit_message_text(helpers.HELP_7, reply_markup=keyboard)
    elif cb == "hb8":
        await CallbackQuery.edit_message_text(helpers.HELP_8, reply_markup=keyboard)
    elif cb == "hb9":
        await CallbackQuery.edit_message_text(helpers.HELP_9, reply_markup=keyboard)
    elif cb == "hb10":
        await CallbackQuery.edit_message_text(helpers.HELP_10, reply_markup=keyboard)
    elif cb == "hb11":
        await CallbackQuery.edit_message_text(helpers.HELP_11, reply_markup=keyboard)
    elif cb == "hb12":
        await CallbackQuery.edit_message_text(helpers.HELP_12, reply_markup=keyboard)
    elif cb == "hb13":
        await CallbackQuery.edit_message_text(helpers.HELP_13, reply_markup=keyboard)
    elif cb == "hb14":
        await CallbackQuery.edit_message_text(helpers.HELP_14, reply_markup=keyboard)
    elif cb == "hb15":
        await CallbackQuery.edit_message_text(helpers.HELP_15, reply_markup=keyboard)


@app.on_callback_query(filters.regex("^feature_help ") & ~BANNED_USERS)
async def feature_help_callback(client, callback_query):
    await callback_query.answer()
    feature = callback_query.data.split(maxsplit=1)[1]
    pages = {
        "ads": (
            "📢 <b>مدیریت اطلاعیه‌ها</b>\n\n"
            "<code>/setad متن اطلاعیه</code> — ذخیره یا تغییر اطلاعیه\n"
            "<code>/setad</code> — غیرفعال کردن اطلاعیه\n"
            "<code>/ad</code> — نمایش اطلاعیه فعلی\n\n"
            "این قابلیت فقط در اختیار مالک ربات است."
        ),
        "forcejoin": (
            "🔒 <b>عضویت اجباری</b>\n\n"
            "<code>/forcejoin @channel</code> — الزام عضویت در کانال\n"
            "<code>/forcejoin</code> — غیرفعال کردن عضویت اجباری\n\n"
            "عضویت کاربر پیش از استفاده از ربات در گروه بررسی می‌شود."
        ),
        "userinfo": (
            "👤 <b>اطلاعات کاربر</b>\n\n"
            "<code>/id</code> — نمایش شناسه شما\n"
            "با ریپلای به پیام کاربر و ارسال <code>/id</code> — نمایش شناسه او\n"
            "<code>/profile</code> یا <code>/me</code> — نمایش پروفایل کامل\n\n"
            "فعالیت‌ها و علاقه‌مندی‌ها با شناسه تلگرام شما ذخیره می‌شوند."
        ),
        "analytics": (
            "📊 <b>تحلیل و آمار</b>\n\n"
            "<code>/topusers</code> یا <code>/ranking</code> — رتبه‌بندی فعالیت کاربران\n"
            "<code>/groupstats</code> یا <code>/analytics</code> — گزارش گروه\n\n"
            "گزارش‌های گروه فقط برای مدیران قابل مشاهده است."
        ),
        "security": (
            "🛡️ <b>سیستم حفاظت و امنیت گروه</b>\n\n"
            "<code>/security</code> — باز کردن پنل تنظیمات امنیتی\n"
            "<code>/security on|off</code> — فعال یا غیرفعال کردن حفاظت پایه\n"
            "<code>/raidmode</code> و <code>/normalmode</code> — حالت اضطراری\n"
            "<code>/warn</code>، <code>/warnings</code>، <code>/resetwarn</code> — مدیریت اخطار\n"
            "<code>/mute 1m|5m|10m|1h|1d</code> — محدودیت موقت\n"
            "<code>/lock نوع</code> و <code>/unlock نوع</code> — قفل مستقل محتوا\n"
            "<code>/addword</code>، <code>/delword</code>، <code>/listwords</code> — فیلتر واژه\n"
            "<code>/whitelist</code> و <code>/unwhitelist</code> — کاربران مجاز\n\n"
            "ضد اسپم، ضد لینک، ضد Flood، محافظت عضو جدید و تشخیص Raid "
            "برای هر گروه جداگانه ذخیره می‌شوند."
        ),
        "vip": (
            "⭐ <b>علاقه‌مندی‌ها و دسترسی ویژه</b>\n\n"
            "<code>/fav نام آهنگ</code> — ذخیره آهنگ\n"
            "<code>/unfav نام آهنگ</code> — حذف آهنگ\n"
            "<code>/favorites</code> — نمایش فهرست آهنگ‌ها\n"
            "<code>/vip user_id days</code> — فعال‌سازی ویژه (فقط مالک)"
        ),
        "calls": (
            "📞 <b>آمار و امنیت تماس</b>\n\n"
            "<code>/callstats</code> — نمایش گزارش تماس گروه\n\n"
            "شروع و پایان تماس صوتی برای گزارش گروه ثبت می‌شود."
        ),
        "guide": (
            "📚 <b>راهنمای فرمان‌ها</b>\n\n"
            "<code>/commands</code>, <code>/guide</code>, or <code>/features</code>\n"
            "فهرست کامل فرمان‌های موسیقی، پروفایل، آمار، امنیت و مدیریت را نشان می‌دهد."
        ),
    }
    text = pages.get(feature, "راهنمای این قابلیت در دسترس نیست.")
    await callback_query.edit_message_text(
        text + "\n\nبرای بازگشت به فهرست قابلیت‌ها، دکمه بازگشت را بزنید.",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(
                text="‹ بازگشت به راهنما",
                callback_data="settingsback_helper",
                style=enums.ButtonStyle.PRIMARY,
            )]]
        ),
    )

# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (suraj08832) 😎
# 
# 🧑‍💻 Developer : https://t.me/AMP_mah
# 🔗 Source link : GitHub.com/suraj08832/Purvi-V2
# 📢 Telegram channel : t.me/JAN_AMP
# ===========================================================
