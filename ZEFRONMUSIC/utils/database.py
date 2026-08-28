# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (suraj08832) 🚀
# 
# This source code is under MIT License 📜
# ❌ Unauthorized forking, importing, or using this code
#    without giving proper credit will result in legal action ⚠️
# 
# 📩 DM for permission : @zefron
# ===========================================================

import asyncio
import random
import config
from typing import Dict, List, Union

from ZEFRONMUSIC import userbot
from ZEFRONMUSIC.core.mongo import mongodb

authdb = mongodb.adminauth
authuserdb = mongodb.authuser
autoenddb = mongodb.autoend
assdb = mongodb.assistants
blacklist_chatdb = mongodb.blacklistChat
blockeddb = mongodb.blockedusers
chatsdb = mongodb.chats
channeldb = mongodb.cplaymode
countdb = mongodb.upcount
gbansdb = mongodb.gban
langdb = mongodb.language
onoffdb = mongodb.onoffper
playmodedb = mongodb.playmode
playtypedb = mongodb.playtypedb
skipdb = mongodb.skipmode
sudoersdb = mongodb.sudoers
usersdb = mongodb.tgusersdb
playlistdb = mongodb.playlist
songlogdb = mongodb.songlog
profilesdb = mongodb.profiles
featuredb = mongodb.professional_features
eventsdb = mongodb.activity_events
favoritesdb = mongodb.favorites
purchasesdb = mongodb.purchases
securitydb = mongodb.group_security
violationsdb = mongodb.security_violations

active = []
activevideo = []
assistantdict = {}
autoend = {}
count = {}
channelconnect = {}
langm = {}
loop = {}
maintenance = []
nonadmin = {}
pause = {}
playmode = {}
playtype = {}
skipmode = {}
playlist = []


async def upsert_profile(user, chat_id: int = None):
    """Record a lightweight profile and activity counter without PII beyond
    Telegram's public identifiers and names supplied by the API."""
    if not user:
        return
    now = __import__("datetime").datetime.utcnow()
    data = {
        "user_id": user.id,
        "first_name": user.first_name or "",
        "last_name": user.last_name or "",
        "username": user.username or "",
        "last_seen": now,
    }
    if chat_id is not None:
        data["last_chat_id"] = chat_id
    await profilesdb.update_one(
        {"user_id": user.id},
        {"$set": data, "$inc": {"messages": 1}},
        upsert=True,
    )
    await eventsdb.insert_one(
        {"kind": "message", "user_id": user.id, "chat_id": chat_id, "at": now}
    )


async def get_profile(user_id: int):
    return await profilesdb.find_one({"user_id": user_id})


async def get_top_users(limit: int = 10):
    return await profilesdb.find({"messages": {"$gt": 0}}).sort("messages", -1).to_list(length=limit)


async def get_feature(chat_id: int, key: str, default=None):
    doc = await featuredb.find_one({"chat_id": chat_id})
    return doc.get(key, default) if doc else default


async def set_feature(chat_id: int, key: str, value):
    await featuredb.update_one({"chat_id": chat_id}, {"$set": {key: value}}, upsert=True)


async def get_security_settings(chat_id: int) -> dict:
    """Return isolated, persistent protection settings for one group."""
    defaults = {
        "enabled": True,
        "anti_spam": True,
        "anti_links": True,
        "anti_flood": True,
        "anti_raid": True,
        "new_member_protection": True,
        "new_member_links": True,
        "new_member_spam": True,
        "new_member_media": False,
        "new_member_flood": True,
        "bad_words_filter": True,
        "warning_system": True,
        "raid_mode": False,
        "media_lock": False,
        "locked": [],
        "bad_words": [],
        "whitelist": [],
        "warning_limit": 3,
        "warning_action": "mute",
        "mute_duration": 600,
        "spam_limit": 5,
        "spam_window": 3,
        "flood_limit": 8,
        "flood_window": 5,
        "new_member_duration": 300,
        "raid_join_limit": 20,
        "raid_window": 30,
        "raid_media": True,
    }
    doc = await securitydb.find_one({"chat_id": int(chat_id)})
    if doc:
        defaults.update({k: v for k, v in doc.items() if k != "_id"})
        # Older records were created before protection was made opt-out. They
        # have no marker showing that an admin explicitly chose a setting, so
        # keep those groups protected instead of preserving the old disabled
        # defaults. Explicit /security off writes the marker below.
        if not doc.get("settings_initialized"):
            for key in (
                "enabled", "anti_spam", "anti_links", "anti_flood",
                "anti_raid", "new_member_protection", "bad_words_filter",
            ):
                defaults[key] = True
    return defaults


async def set_security_setting(chat_id: int, key: str, value):
    await securitydb.update_one(
        {"chat_id": int(chat_id)},
        {"$set": {key: value, "settings_initialized": True},
         "$setOnInsert": {"chat_id": int(chat_id)}},
        upsert=True,
    )


async def add_security_violation(chat_id: int, user_id: int, violation: str):
    await violationsdb.insert_one(
        {"chat_id": int(chat_id), "user_id": int(user_id), "violation": violation,
         "timestamp": __import__("datetime").datetime.utcnow()}
    )


async def get_security_user(chat_id: int, user_id: int) -> dict:
    doc = await securitydb.find_one(
        {"chat_id": int(chat_id), "users.user_id": int(user_id)},
        {"users": {"$elemMatch": {"user_id": int(user_id)}}},
    )
    return (doc or {}).get("users", [{}])[0]


async def update_security_user(chat_id: int, user_id: int, **values):
    values["user_id"] = int(user_id)
    for key, value in values.items():
        await securitydb.update_one(
            {"chat_id": int(chat_id), "users.user_id": int(user_id)},
            {"$set": {f"users.$.{key}": value}},
        )
    if not await securitydb.find_one({"chat_id": int(chat_id), "users.user_id": int(user_id)}):
        await securitydb.update_one(
            {"chat_id": int(chat_id)},
            {"$push": {"users": values}, "$setOnInsert": {"chat_id": int(chat_id)}},
            upsert=True,
        )


async def add_favorite(user_id: int, title: str, query: str):
    await favoritesdb.update_one(
        {"user_id": user_id, "query": query},
        {"$set": {"user_id": user_id, "title": title, "query": query},
         "$setOnInsert": {"added_at": __import__("datetime").datetime.utcnow()}},
        upsert=True,
    )


async def remove_favorite(user_id: int, query: str):
    return (await favoritesdb.delete_one({"user_id": user_id, "query": query})).deleted_count > 0


async def get_favorites(user_id: int, limit: int = 25):
    return await favoritesdb.find({"user_id": user_id}).sort("added_at", -1).to_list(length=limit)


async def has_song_purchase(user_id: int, song_id: str) -> bool:
    return bool(await purchasesdb.find_one({"telegram_user_id": user_id, "song_id": song_id}))


async def save_song_purchase(
    user_id: int,
    song_id: str,
    payment_id: str,
    amount: int,
    currency: str,
    metadata: dict | None = None,
):
    purchase = {
        "telegram_user_id": user_id,
        "song_id": song_id,
        "payment_id": payment_id,
        "telegram_payment_charge_id": payment_id,
        "amount": amount,
        "currency": currency,
        "purchased_at": __import__("datetime").datetime.utcnow(),
    }
    if metadata:
        purchase["song"] = metadata
    await purchasesdb.update_one(
        {"telegram_user_id": user_id, "song_id": song_id},
        {"$setOnInsert": purchase},
        upsert=True,
    )


async def get_feature_counts():
    return {
        "users": await profilesdb.count_documents({}),
        "groups": await chatsdb.count_documents({"chat_id": {"$lt": 0}}),
        "events": await eventsdb.count_documents({}),
        "vip": await featuredb.count_documents({"vip": {"$exists": True, "$ne": []}}),
    }



async def is_vc_logger(chat_id: int) -> bool:
    chat = await get_chat(chat_id)
    return chat.get("vc_logger", False)

async def set_vc_logger(chat_id: int, mode: bool):
    await chatsdb.update_one(
        {"chat_id": chat_id}, 
        {"$set": {"vc_logger": mode}}, 
        upsert=True
    )


async def _get_playlists(chat_id: int) -> Dict[str, int]:
    _notes = await playlistdb.find_one({"chat_id": chat_id})
    if not _notes:
        return {}
    return _notes["notes"]


async def get_playlist_names(chat_id: int) -> List[str]:
    _notes = []
    for note in await _get_playlists(chat_id):
        _notes.append(note)
    return _notes


async def get_playlist(chat_id: int, name: str) -> Union[bool, dict]:
    name = name
    _notes = await _get_playlists(chat_id)
    if name in _notes:
        return _notes[name]
    else:
        return False


async def save_playlist(chat_id: int, name: str, note: dict):
    name = name
    _notes = await _get_playlists(chat_id)
    _notes[name] = note
    await playlistdb.update_one(
        {"chat_id": chat_id}, {"$set": {"notes": _notes}}, upsert=True
    )


async def delete_playlist(chat_id: int, name: str) -> bool:
    notesd = await _get_playlists(chat_id)
    name = name
    if name in notesd:
        del notesd[name]
        await playlistdb.update_one(
            {"chat_id": chat_id},
            {"$set": {"notes": notesd}},
            upsert=True,
        )
        return True
    return False


async def get_song_logger(vidid: str) -> Union[bool, dict]:
    """Return cached logger info for a given YouTube video id, or False if not found."""
    data = await songlogdb.find_one({"vidid": vidid})
    if not data:
        return False
    return data


async def save_song_logger(
    vidid: str,
    message_id: int,
    file_id: str,
    is_video: bool,
) -> None:
    """Save or update logger cache entry for a YouTube video id."""
    await songlogdb.update_one(
        {"vidid": vidid},
        {
            "$set": {
                "vidid": vidid,
                "message_id": message_id,
                "file_id": file_id,
                "is_video": is_video,
            }
        },
        upsert=True,
    )


async def get_assistant_number(chat_id: int) -> str:
    assistant = assistantdict.get(chat_id)
    return assistant


async def get_client(assistant: int):
    if int(assistant) == 1:
        return userbot.one
    elif int(assistant) == 2:
        return userbot.two
    elif int(assistant) == 3:
        return userbot.three
    elif int(assistant) == 4:
        return userbot.four
    elif int(assistant) == 5:
        return userbot.five


async def set_assistant_new(chat_id, number):
    number = int(number)
    await assdb.update_one(
        {"chat_id": chat_id},
        {"$set": {"assistant": number}},
        upsert=True,
    )


async def set_assistant(chat_id):
    from ZEFRONMUSIC.core.userbot import assistants

    if not any((config.STRING1, config.STRING2, config.STRING3, config.STRING4, config.STRING5)):
        raise RuntimeError("No assistant session is configured")
    for _ in range(40):
        if assistants:
            break
        await asyncio.sleep(0.5)
    if not assistants:
        raise RuntimeError("No assistant account is available")
    ran_assistant = random.choice(assistants)
    assistantdict[chat_id] = ran_assistant
    await assdb.update_one(
        {"chat_id": chat_id},
        {"$set": {"assistant": ran_assistant}},
        upsert=True,
    )
    userbot = await get_client(ran_assistant)
    return userbot


async def get_assistant(chat_id: int) -> str:
    from ZEFRONMUSIC.core.userbot import assistants

    if not any((config.STRING1, config.STRING2, config.STRING3, config.STRING4, config.STRING5)):
        raise RuntimeError("No assistant session is configured")
    for _ in range(40):
        if assistants:
            break
        await asyncio.sleep(0.5)
    if not assistants:
        raise RuntimeError("No assistant account is available")
    assistant = assistantdict.get(chat_id)
    if not assistant:
        dbassistant = await assdb.find_one({"chat_id": chat_id})
        if not dbassistant:
            userbot = await set_assistant(chat_id)
            return userbot
        else:
            got_assis = dbassistant["assistant"]
            if got_assis in assistants:
                assistantdict[chat_id] = got_assis
                userbot = await get_client(got_assis)
                return userbot
            else:
                userbot = await set_assistant(chat_id)
                return userbot
    else:
        if assistant in assistants:
            userbot = await get_client(assistant)
            return userbot
        else:
            userbot = await set_assistant(chat_id)
            return userbot


async def set_calls_assistant(chat_id):
    from ZEFRONMUSIC.core.userbot import assistants

    ran_assistant = random.choice(assistants)
    assistantdict[chat_id] = ran_assistant
    await assdb.update_one(
        {"chat_id": chat_id},
        {"$set": {"assistant": ran_assistant}},
        upsert=True,
    )
    return ran_assistant


async def group_assistant(self, chat_id: int) -> int:
    from ZEFRONMUSIC.core.userbot import assistants

    assistant = assistantdict.get(chat_id)
    if not assistant:
        dbassistant = await assdb.find_one({"chat_id": chat_id})
        if not dbassistant:
            assis = await set_calls_assistant(chat_id)
        else:
            assis = dbassistant["assistant"]
            if assis in assistants:
                assistantdict[chat_id] = assis
                assis = assis
            else:
                assis = await set_calls_assistant(chat_id)
    else:
        if assistant in assistants:
            assis = assistant
        else:
            assis = await set_calls_assistant(chat_id)
    if int(assis) == 1:
        return self.one
    elif int(assis) == 2:
        return self.two
    elif int(assis) == 3:
        return self.three
    elif int(assis) == 4:
        return self.four
    elif int(assis) == 5:
        return self.five


async def is_skipmode(chat_id: int) -> bool:
    mode = skipmode.get(chat_id)
    if not mode:
        user = await skipdb.find_one({"chat_id": chat_id})
        if not user:
            skipmode[chat_id] = True
            return True
        skipmode[chat_id] = False
        return False
    return mode


async def skip_on(chat_id: int):
    skipmode[chat_id] = True
    user = await skipdb.find_one({"chat_id": chat_id})
    if user:
        return await skipdb.delete_one({"chat_id": chat_id})


async def skip_off(chat_id: int):
    skipmode[chat_id] = False
    user = await skipdb.find_one({"chat_id": chat_id})
    if not user:
        return await skipdb.insert_one({"chat_id": chat_id})


async def get_upvote_count(chat_id: int) -> int:
    mode = count.get(chat_id)
    if not mode:
        mode = await countdb.find_one({"chat_id": chat_id})
        if not mode:
            return 5
        count[chat_id] = mode["mode"]
        return mode["mode"]
    return mode


async def set_upvotes(chat_id: int, mode: int):
    count[chat_id] = mode
    await countdb.update_one(
        {"chat_id": chat_id}, {"$set": {"mode": mode}}, upsert=True
    )


async def is_autoend() -> bool:
    chat_id = 1234
    user = await autoenddb.find_one({"chat_id": chat_id})
    if not user:
        return False
    return True


async def autoend_on():
    chat_id = 1234
    await autoenddb.insert_one({"chat_id": chat_id})


async def autoend_off():
    chat_id = 1234
    await autoenddb.delete_one({"chat_id": chat_id})


async def get_loop(chat_id: int) -> int:
    lop = loop.get(chat_id)
    if not lop:
        return 0
    return lop


async def set_loop(chat_id: int, mode: int):
    loop[chat_id] = mode


async def get_cmode(chat_id: int) -> int:
    mode = channelconnect.get(chat_id)
    if not mode:
        mode = await channeldb.find_one({"chat_id": chat_id})
        if not mode:
            return None
        channelconnect[chat_id] = mode["mode"]
        return mode["mode"]
    return mode


async def set_cmode(chat_id: int, mode: int):
    channelconnect[chat_id] = mode
    await channeldb.update_one(
        {"chat_id": chat_id}, {"$set": {"mode": mode}}, upsert=True
    )


async def get_playtype(chat_id: int) -> str:
    mode = playtype.get(chat_id)
    if not mode:
        mode = await playtypedb.find_one({"chat_id": chat_id})
        if not mode:
            playtype[chat_id] = "Everyone"
            return "Everyone"
        playtype[chat_id] = mode["mode"]
        return mode["mode"]
    return mode


async def set_playtype(chat_id: int, mode: str):
    playtype[chat_id] = mode
    await playtypedb.update_one(
        {"chat_id": chat_id}, {"$set": {"mode": mode}}, upsert=True
    )


async def get_playmode(chat_id: int) -> str:
    mode = playmode.get(chat_id)
    if not mode:
        mode = await playmodedb.find_one({"chat_id": chat_id})
        if not mode:
            playmode[chat_id] = "Inline"
            return "Inline"
        playmode[chat_id] = mode["mode"]
        return mode["mode"]
    return mode


async def set_playmode(chat_id: int, mode: str):
    playmode[chat_id] = mode
    await playmodedb.update_one(
        {"chat_id": chat_id}, {"$set": {"mode": mode}}, upsert=True
    )


async def get_lang(chat_id: int) -> str:
    mode = langm.get(chat_id)
    if not mode:
        lang = await langdb.find_one({"chat_id": chat_id})
        if not lang:
            langm[chat_id] = config.DEFAULT_LANGUAGE
            return config.DEFAULT_LANGUAGE
        langm[chat_id] = lang["lang"]
        return lang["lang"]
    return mode


async def set_lang(chat_id: int, lang: str):
    langm[chat_id] = lang
    await langdb.update_one({"chat_id": chat_id}, {"$set": {"lang": lang}}, upsert=True)


async def is_music_playing(chat_id: int) -> bool:
    mode = pause.get(chat_id)
    if not mode:
        return False
    return mode


async def music_on(chat_id: int):
    pause[chat_id] = True


async def music_off(chat_id: int):
    pause[chat_id] = False


async def get_active_chats() -> list:
    return active


async def is_active_chat(chat_id: int) -> bool:
    if chat_id not in active:
        return False
    else:
        return True


async def add_active_chat(chat_id: int):
    if chat_id not in active:
        active.append(chat_id)


async def remove_active_chat(chat_id: int):
    if chat_id in active:
        active.remove(chat_id)


async def get_active_video_chats() -> list:
    return activevideo


async def is_active_video_chat(chat_id: int) -> bool:
    if chat_id not in activevideo:
        return False
    else:
        return True


async def add_active_video_chat(chat_id: int):
    if chat_id not in activevideo:
        activevideo.append(chat_id)


async def remove_active_video_chat(chat_id: int):
    if chat_id in activevideo:
        activevideo.remove(chat_id)


async def check_nonadmin_chat(chat_id: int) -> bool:
    user = await authdb.find_one({"chat_id": chat_id})
    if not user:
        return False
    return True


async def is_nonadmin_chat(chat_id: int) -> bool:
    mode = nonadmin.get(chat_id)
    if not mode:
        user = await authdb.find_one({"chat_id": chat_id})
        if not user:
            nonadmin[chat_id] = False
            return False
        nonadmin[chat_id] = True
        return True
    return mode


async def add_nonadmin_chat(chat_id: int):
    nonadmin[chat_id] = True
    is_admin = await check_nonadmin_chat(chat_id)
    if is_admin:
        return
    return await authdb.insert_one({"chat_id": chat_id})


async def remove_nonadmin_chat(chat_id: int):
    nonadmin[chat_id] = False
    is_admin = await check_nonadmin_chat(chat_id)
    if not is_admin:
        return
    return await authdb.delete_one({"chat_id": chat_id})


async def is_on_off(on_off: int) -> bool:
    onoff = await onoffdb.find_one({"on_off": on_off})
    if not onoff:
        return False
    return True


async def add_on(on_off: int):
    is_on = await is_on_off(on_off)
    if is_on:
        return
    return await onoffdb.insert_one({"on_off": on_off})


async def add_off(on_off: int):
    is_off = await is_on_off(on_off)
    if not is_off:
        return
    return await onoffdb.delete_one({"on_off": on_off})


async def is_maintenance():
    if not maintenance:
        get = await onoffdb.find_one({"on_off": 1})
        if not get:
            maintenance.clear()
            maintenance.append(2)
            return True
        else:
            maintenance.clear()
            maintenance.append(1)
            return False
    else:
        if 1 in maintenance:
            return False
        else:
            return True


async def maintenance_off():
    maintenance.clear()
    maintenance.append(2)
    is_off = await is_on_off(1)
    if not is_off:
        return
    return await onoffdb.delete_one({"on_off": 1})


async def maintenance_on():
    maintenance.clear()
    maintenance.append(1)
    is_on = await is_on_off(1)
    if is_on:
        return
    return await onoffdb.insert_one({"on_off": 1})


async def is_served_user(user_id: int) -> bool:
    user = await usersdb.find_one({"user_id": user_id})
    if not user:
        return False
    return True


async def get_served_users() -> list:
    users_list = []
    async for user in usersdb.find({"user_id": {"$gt": 0}}):
        users_list.append(user)
    return users_list


async def add_served_user(user_id: int):
    is_served = await is_served_user(user_id)
    if is_served:
        return
    return await usersdb.insert_one({"user_id": user_id})


async def get_served_chats() -> list:
    chats_list = []
    async for chat in chatsdb.find({"chat_id": {"$lt": 0}}):
        chats_list.append(chat)
    return chats_list


async def is_served_chat(chat_id: int) -> bool:
    chat = await chatsdb.find_one({"chat_id": chat_id})
    if not chat:
        return False
    return True


async def add_served_chat(chat_id: int):
    is_served = await is_served_chat(chat_id)
    if is_served:
        return
    return await chatsdb.insert_one({"chat_id": chat_id})


async def blacklisted_chats() -> list:
    chats_list = []
    async for chat in blacklist_chatdb.find({"chat_id": {"$lt": 0}}):
        chats_list.append(chat["chat_id"])
    return chats_list


async def blacklist_chat(chat_id: int) -> bool:
    if not await blacklist_chatdb.find_one({"chat_id": chat_id}):
        await blacklist_chatdb.insert_one({"chat_id": chat_id})
        return True
    return False


async def whitelist_chat(chat_id: int) -> bool:
    if await blacklist_chatdb.find_one({"chat_id": chat_id}):
        await blacklist_chatdb.delete_one({"chat_id": chat_id})
        return True
    return False


async def _get_authusers(chat_id: int) -> Dict[str, int]:
    _notes = await authuserdb.find_one({"chat_id": chat_id})
    if not _notes:
        return {}
    return _notes["notes"]


async def get_authuser_names(chat_id: int) -> List[str]:
    _notes = []
    for note in await _get_authusers(chat_id):
        _notes.append(note)
    return _notes


async def get_authuser(chat_id: int, name: str) -> Union[bool, dict]:
    name = name
    _notes = await _get_authusers(chat_id)
    if name in _notes:
        return _notes[name]
    else:
        return False


async def save_authuser(chat_id: int, name: str, note: dict):
    name = name
    _notes = await _get_authusers(chat_id)
    _notes[name] = note

    await authuserdb.update_one(
        {"chat_id": chat_id}, {"$set": {"notes": _notes}}, upsert=True
    )


async def delete_authuser(chat_id: int, name: str) -> bool:
    notesd = await _get_authusers(chat_id)
    name = name
    if name in notesd:
        del notesd[name]
        await authuserdb.update_one(
            {"chat_id": chat_id},
            {"$set": {"notes": notesd}},
            upsert=True,
        )
        return True
    return False


async def get_gbanned() -> list:
    results = []
    async for user in gbansdb.find({"user_id": {"$gt": 0}}):
        user_id = user["user_id"]
        results.append(user_id)
    return results


async def is_gbanned_user(user_id: int) -> bool:
    user = await gbansdb.find_one({"user_id": user_id})
    if not user:
        return False
    return True


async def add_gban_user(user_id: int):
    is_gbanned = await is_gbanned_user(user_id)
    if is_gbanned:
        return
    return await gbansdb.insert_one({"user_id": user_id})


async def remove_gban_user(user_id: int):
    is_gbanned = await is_gbanned_user(user_id)
    if not is_gbanned:
        return
    return await gbansdb.delete_one({"user_id": user_id})


async def get_sudoers() -> list:
    sudoers = await sudoersdb.find_one({"sudo": "sudo"})
    if not sudoers:
        return []
    return sudoers["sudoers"]


async def add_sudo(user_id: int) -> bool:
    sudoers = await get_sudoers()
    sudoers.append(user_id)
    await sudoersdb.update_one(
        {"sudo": "sudo"}, {"$set": {"sudoers": sudoers}}, upsert=True
    )
    return True


async def remove_sudo(user_id: int) -> bool:
    sudoers = await get_sudoers()
    sudoers.remove(user_id)
    await sudoersdb.update_one(
        {"sudo": "sudo"}, {"$set": {"sudoers": sudoers}}, upsert=True
    )
    return True


async def get_banned_users() -> list:
    results = []
    async for user in blockeddb.find({"user_id": {"$gt": 0}}):
        user_id = user["user_id"]
        results.append(user_id)
    return results


async def get_banned_count() -> int:
    users = blockeddb.find({"user_id": {"$gt": 0}})
    users = await users.to_list(length=100000)
    return len(users)


async def is_banned_user(user_id: int) -> bool:
    user = await blockeddb.find_one({"user_id": user_id})
    if not user:
        return False
    return True


async def add_banned_user(user_id: int):
    is_gbanned = await is_banned_user(user_id)
    if is_gbanned:
        return
    return await blockeddb.insert_one({"user_id": user_id})


async def remove_banned_user(user_id: int):
    is_gbanned = await is_banned_user(user_id)
    if not is_gbanned:
        return
    return await blockeddb.delete_one({"user_id": user_id})

# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (suraj08832) 😎
# 
# 🧑‍💻 Developer : https://t.me/AMP_mah
# 🔗 Source link : GitHub.com/suraj08832/Purvi-V2
# 📢 Telegram channel : t.me/JAN_AMP
# ===========================================================
