---
name: Persian localization
description: Locale fallback and transliterated music-search behavior for the Telegram music bot.
---

Incomplete locale files must not be populated with English values during startup. The Persian locale should provide a Persian fallback for any newly added message key.

**Why:** The bot's default language is Persian, so missing translations otherwise make individual command responses unexpectedly switch to English.

**How to apply:** Keep locale loading independent and make `get_string("fa")` fill missing keys with Persian category-safe text. Preserve Telegram's standard Latin command names while accepting Persian/Urdu text as music-search queries.

The preferred Persian song card is thumbnail-first with full-width audio playback, previous/download/next controls, full-width video playback, and a close action; new chats use the selection card before playback.

**Why:** The user wants the first `/play` response to resemble a clean Telegram music-card UI rather than starting playback immediately.

**How to apply:** Keep the actual song thumbnail, title, artist, and duration in the card, and keep the download button connected to the signed Stars flow.