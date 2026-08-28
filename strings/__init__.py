# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (suraj08832) 🚀
# 
# This source code is under MIT License 📜
# ❌ Unauthorized forking, importing, or using this code
#    without giving proper credit will result in legal action ⚠️
# 
# 📩 DM for permission : @zefron
# ===========================================================

import os
from typing import List

import yaml

languages = {}
languages_present = {}

_FA_CATEGORY_TEXT = {
    "general": "در پردازش درخواست شما مشکلی پیش آمد.",
    "tg": "دانلود و پردازش فایل",
    "call": "مدیریت تماس صوتی",
    "auth": "کاربران مجاز",
    "reload": "تنظیمات مدیر با موفقیت به‌روزرسانی شد.",
    "admin": "کنترل پخش موسیقی",
    "start": "به ربات موسیقی خوش آمدید.",
    "lang": "زبان با موفقیت تغییر کرد.",
    "setting": "تنظیمات گروه",
    "set_cb": "در حال دریافت تنظیمات...",
    "gstats": "آمار و اطلاعات ربات",
    "play": "پخش موسیقی",
    "str": "پخش زنده",
    "ping": "وضعیت و آمار سیستم",
    "queue": "صف پخش خالی است.",
    "stream": "پخش موسیقی آغاز شد.",
    "sudo": "مدیریت کاربران ارشد",
    "block": "مدیریت مسدودسازی کاربران",
    "black": "مدیریت فهرست سیاه",
    "maint": "حالت تعمیر و نگهداری",
    "log": "ثبت رویدادها",
    "broad": "پیام همگانی",
    "server": "خطای سرور.",
    "gban": "مدیریت مسدودسازی سراسری",
    "song": "دانلود آهنگ",
}


def _persian_fallback(key, source):
    """Keep older locale files safe: missing Persian keys never expose English."""
    category = key.split("_", 1)[0]
    text = _FA_CATEGORY_TEXT.get(category, "درخواست شما با موفقیت پردازش شد.")
    placeholders = []
    for index in range(10):
        marker = "{" + str(index) + "}"
        if marker in str(source):
            placeholders.append(marker)
    return text + (" " + " ".join(placeholders) if placeholders else "")


def get_string(lang: str):
    if lang == "fa":
        values = dict(languages.get("fa", {}))
        for key, source in languages["en"].items():
            values.setdefault(key, _persian_fallback(key, source))
        return values
    values = dict(languages.get(lang, languages["fa"]))
    # Keep every inline keyboard Persian even when a group selected another
    # language. Message content can still follow the group's chosen language.
    persian = languages["fa"]
    for key, value in persian.items():
        if key in {"CLOSE_BUTTON", "BACK_BUTTON"} or "_B_" in key:
            values[key] = value
    return values


for filename in os.listdir(r"./strings/langs/"):
    if "en" not in languages:
        languages["en"] = yaml.safe_load(
            open(r"./strings/langs/en.yml", encoding="utf8")
        )
        languages_present["en"] = languages["en"]["name"]
    if filename.endswith(".yml"):
        language_name = filename[:-4]
        if language_name == "en":
            continue
        languages[language_name] = yaml.safe_load(
            open(r"./strings/langs/" + filename, encoding="utf8")
        )
        # Keep Persian independent so missing keys use Persian fallbacks.
        # Other legacy locales retain their existing English fallback.
        if language_name != "fa":
            for item in languages["en"]:
                languages[language_name].setdefault(item, languages["en"][item])
    try:
        languages_present[language_name] = languages[language_name]["name"]
    except:
        print("There is some issue with the language file inside bot.")
        exit()

# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (suraj08832) 😎
# 
# 🧑‍💻 Developer : https://t.me/AMP_mah
# 🔗 Source link : GitHub.com/suraj08832/Purvi-V2
# 📢 Telegram channel : t.me/JAN_AMP
# ===========================================================
