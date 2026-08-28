# Running and configuring the Telegram music bot

Run the bot with:

```bash
bash start
```

The default interface language is Persian (`DEFAULT_LANGUAGE=fa`). Music can
be searched with the normal Telegram command and a Persian query, for example:
`/play سیدهو موس والا`.

## Telegram Stars downloads

Song result cards include a Persian download button. Set
`DOWNLOAD_PRICE_STARS` to the integer price in Telegram Stars (default: `10`).
The bot uses Telegram's native `XTR` digital-goods invoice flow. `SESSION_SECRET`
must be set so download callback data and invoice payloads can be signed.

Purchases are stored in the MongoDB `purchases` collection. A successful
payment is persisted before delivery, so a delivery failure does not charge the
user again; pressing the download button later retries delivery.

## Group protection

The protection layer is implemented in `ZEFRONMUSIC/plugins/tools/security.py`.
It uses the existing MongoDB connection and stores group settings in the
`group_security` collection and violation records in `security_violations`.
There is no migration or new environment variable.

Protection is enabled by default for every group. Add the bot as an administrator
with permission to delete messages and restrict members. Only a group
administrator or owner can change settings; `/security off` is the explicit way
to disable the core protection families.

- `/security on` or `/security off` — enable/disable the core protections; plain
  `/security` opens the inline settings panel.
- `/setsecurity warning_limit|mute_duration|spam_limit|spam_window|flood_limit|flood_window|new_member_duration|raid_join_limit|raid_window value`
- `/warn`, `/warnings`, `/resetwarn` — reply to a member's message.
- `/mute 1m|5m|10m|1h|1d` — temporarily restrict a replied-to member.
- `/lock <links|media|stickers|gifs|videos|photos|voice|forwards>` and
  `/unlock <same value>`.
- `/addword`, `/delword`, `/listwords` — manage this group's blacklist.
- `/whitelist`, `/unwhitelist`, `/whitelistusers` — reply to a member or pass
  their numeric ID.
- `/raidmode` and `/normalmode` — manually control emergency mode.

All group settings and warnings are isolated by chat ID. Administrators,
owners, and whitelisted users bypass automated moderation, and moderation
actions re-check live Telegram permissions before muting or banning. Raid
detection watches joins in memory and activates the group's saved raid mode
when its configured join threshold is reached. Temporary restrictions use
Telegram's expiry timestamp, so they recover safely across bot restarts.

Photos sent by human users and any edited human group message are always
deleted, including when the sender is an administrator. Each deletion produces
a Persian HTML notice tagging the sender; the notice is removed automatically
after one minute.

Security events are sent to the existing `LOGGER_ID` chat when configured;
the bot's existing `LOGGER_ID` environment variable is the log destination.

## NSFW media moderation

The chatbot plugin can use Sightengine to classify human-sent group photos,
stickers, GIFs, videos, and video notes. Media classified as explicit is
deleted automatically. The moderation request fails open if Sightengine is
unavailable, the file is unsupported, or it exceeds the 20 MB default limit.

Set these Replit Secrets to enable it:

- `SIGHTENGINE_API_USER`
- `SIGHTENGINE_API_SECRET`
- `SIGHTENGINE_API_URL` (optional; defaults to Sightengine's `check.json` endpoint)
- `SIGHTENGINE_MAX_FILE_SIZE` (optional, in bytes)

These settings are separate from the chatbot's Groq configuration. The
chatbot uses Groq's OpenAI-compatible chat completions endpoint by default.
Set `GROQ_API_KEY` in Replit Secrets to enable it. You can optionally set
`GROQ_API_URL` and `GROQ_MODEL` for a compatible endpoint or another Groq
model. The default model is `openai/gpt-oss-120b`.
