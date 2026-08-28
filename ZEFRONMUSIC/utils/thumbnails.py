# =======================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (suraj08832) 🚀
# This source code is under MIT License 📜
# 📩 DM for permission : @zefron
# =======================================================

import os, re, random, aiofiles, aiohttp, asyncio
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont
from py_yt import VideosSearch
from config import YOUTUBE_IMG_URL
from ZEFRONMUSIC import app

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

PALETTES = [
    {"neon": (0, 230, 180),  "accent": (0, 120, 255),  "bg": (10, 20, 40)},
    {"neon": (255, 60, 180), "accent": (160, 0, 255),  "bg": (30, 0, 30)},
    {"neon": (255, 200, 0),  "accent": (255, 90, 0),   "bg": (30, 15, 0)},
    {"neon": (60, 255, 100), "accent": (0, 180, 255),  "bg": (0, 25, 15)},
    {"neon": (255, 70, 70),  "accent": (255, 190, 0),  "bg": (30, 5, 5)},
    {"neon": (140, 80, 255), "accent": (255, 80, 160), "bg": (15, 0, 30)},
]

LIVE_BADGE_COLORS = [
    (220, 30,  30),
    (255, 120,  0),
    (140,   0, 255),
    (0,   160, 255),
    (0,   200,  80),
    (255,  50, 180),
]

# ── active live rotator tasks: chat_id → asyncio.Task ──
_live_tasks: dict = {}


def trim_to_width(text, font, max_w):
    try:
        if font.getlength(text) <= max_w:
            return text
        for i in range(len(text) - 1, 0, -1):
            if font.getlength(text[:i] + "…") <= max_w:
                return text[:i] + "…"
    except Exception:
        return text[:max_w // 10] + "…" if len(text) > max_w // 10 else text
    return "…"


def add_rounded_corners(img, radius):
    img = img.convert("RGBA")
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, img.width - 1, img.height - 1], radius=radius, fill=255
    )
    out = Image.new("RGBA", img.size, (0, 0, 0, 0))
    out.paste(img, mask=mask)
    return out


def _text_w(font, text):
    try:
        return int(font.getlength(text))
    except Exception:
        return len(text) * 11


def draw_text_shadowed(draw, xy, text, font, fill=(255, 255, 255), shadow=(0, 0, 0)):
    x, y = xy
    for dx, dy in [(-2, -2), (2, -2), (-2, 2), (2, 2), (0, 3), (3, 0)]:
        draw.text((x + dx, y + dy), text, font=font, fill=(*shadow, 180))
    draw.text((x, y), text, font=font, fill=(*fill, 255))


def draw_pill(draw, x, y, text, font, neon, alpha_bg=55, alpha_border=200):
    tw = _text_w(font, text)
    px, py = 14, 7
    rx1, ry1 = x + tw + px * 2, y + font.size + py * 2
    r, g, b = neon
    draw.rounded_rectangle([x, y, rx1, ry1], radius=(ry1 - y) // 2,
                           fill=(r, g, b, alpha_bg),
                           outline=(r, g, b, alpha_border), width=2)
    draw.text((x + px, y + py), text, font=font, fill=(255, 255, 255, 255))
    return rx1 + 12


def draw_filled_badge(draw, x, y, text, font, bg_rgb, text_rgb=(255, 255, 255)):
    tw = _text_w(font, text)
    px, py = 14, 7
    rx1, ry1 = x + tw + px * 2, y + font.size + py * 2
    r, g, b = bg_rgb
    draw.rounded_rectangle([x, y, rx1, ry1], radius=(ry1 - y) // 2,
                           fill=(r, g, b, 210),
                           outline=(255, 255, 255, 70), width=1)
    draw.text((x + px, y + py), text, font=font, fill=(*text_rgb, 255))
    return rx1 + 10


def draw_equalizer(draw, x, y, palette, bars=8, bw=10, gap=6, max_h=50):
    nr, ng, nb = palette["neon"]
    ar, ag, ab = palette["accent"]
    for i in range(bars):
        bh = random.randint(10, max_h)
        t = i / max(bars - 1, 1)
        r = int(nr + (ar - nr) * t)
        g = int(ng + (ag - ng) * t)
        b = int(nb + (ab - nb) * t)
        bx = x + i * (bw + gap)
        draw.rounded_rectangle([bx, y - bh, bx + bw, y], radius=4, fill=(r, g, b, 220))


def draw_progress_bar(draw, x, y, w, palette):
    nr, ng, nb = palette["neon"]
    ar, ag, ab = palette["accent"]
    h = 7
    draw.rounded_rectangle([x, y, x + w, y + h], radius=3, fill=(255, 255, 255, 35))
    pct = random.uniform(0.25, 0.80)
    fw = int(w * pct)
    for px in range(fw):
        t = px / max(fw - 1, 1)
        r2 = int(nr + (ar - nr) * t)
        g2 = int(ng + (ag - ng) * t)
        b2 = int(nb + (ab - nb) * t)
        draw.line([(x + px, y), (x + px, y + h)], fill=(r2, g2, b2, 230))
    cx = x + fw
    draw.ellipse([cx - 8, y - 4, cx + 8, y + h + 4], fill=(255, 255, 255, 255))
    draw.ellipse([cx - 5, y - 1, cx + 5, y + h + 1], fill=(nr, ng, nb, 255))


def _build_image(raw_path: str, title: str, views: str, duration_text: str,
                 player_username: str, is_live: bool, palette: dict) -> Image.Image:
    W, H = 1280, 720
    nr, ng, nb = palette["neon"]
    ar, ag, ab = palette["accent"]
    br, bg_, bb = palette["bg"]

    base = Image.open(raw_path).resize((W, H)).convert("RGBA")
    bg = base.filter(ImageFilter.GaussianBlur(30))
    bg = ImageEnhance.Brightness(bg).enhance(0.22)

    # Solid dark colour wash for better text contrast
    wash = Image.new("RGBA", (W, H), (br, bg_, bb, 160))
    bg = Image.alpha_composite(bg.convert("RGBA"), wash)

    # Vignette gradient
    vign = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vign)
    for y in range(H):
        a = int(200 * (y / H) ** 0.5)
        vd.line([(0, y), (W, y)], fill=(0, 0, 0, a))
    bg = Image.alpha_composite(bg, vign)

    # Noise
    noise = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    nd = ImageDraw.Draw(noise)
    for _ in range(3000):
        px2, py2 = random.randint(0, W - 1), random.randint(0, H - 1)
        nd.point((px2, py2), fill=(255, 255, 255, random.randint(0, 14)))
    bg = Image.alpha_composite(bg, noise)

    # ── CARD ──
    card_w, card_h = 760, 400
    card_x = (W - card_w) // 2
    card_y = 66

    glass = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
    ImageDraw.Draw(glass, "RGBA").rounded_rectangle(
        [0, 0, card_w, card_h], radius=26,
        fill=(255, 255, 255, 12), outline=(nr, ng, nb, 100), width=2
    )
    bg.paste(glass, (card_x, card_y), glass)

    # Multi-layer glow border
    for spread in range(22, 0, -5):
        alpha = int(40 * spread / 22)
        gl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(gl, "RGBA").rounded_rectangle(
            [card_x - spread, card_y - spread,
             card_x + card_w + spread, card_y + card_h + spread],
            radius=26 + spread, outline=(nr, ng, nb, alpha), width=4
        )
        bg = Image.alpha_composite(bg, gl)

    draw = ImageDraw.Draw(bg, "RGBA")

    # Thumbnail inside card
    iw, ih = 690, 320
    ix = card_x + (card_w - iw) // 2
    iy = card_y + 16
    thumb = Image.open(raw_path).resize((iw, ih)).convert("RGBA")
    thumb = add_rounded_corners(thumb, 18)
    # subtle dark rim on thumb
    rim = Image.new("RGBA", (iw, ih), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rim, "RGBA")
    for ri in range(8):
        a2 = int(100 * (1 - ri / 8))
        rd.rounded_rectangle([ri, ri, iw - ri, ih - ri],
                             radius=max(18 - ri, 2), outline=(0, 0, 0, a2), width=2)
    bg.paste(rim, (ix, iy), rim)
    bg.paste(thumb, (ix, iy), thumb)

    # ── Fonts ──
    try:
        f_title  = ImageFont.truetype("ZEFRONMUSIC/assets/f.ttf",     42)
        f_meta   = ImageFont.truetype("ZEFRONMUSIC/assets/font.ttf",  21)
        f_tag    = ImageFont.truetype("ZEFRONMUSIC/assets/font2.ttf", 22)
        f_badge  = ImageFont.truetype("ZEFRONMUSIC/assets/font2.ttf", 20)
        f_small  = ImageFont.truetype("ZEFRONMUSIC/assets/font.ttf",  19)
    except OSError:
        f_title = f_meta = f_tag = f_badge = f_small = ImageFont.load_default()

    draw = ImageDraw.Draw(bg, "RGBA")

    # ── Title with dark pill backdrop for readability ──
    title_text = trim_to_width(title, f_title, W - 140)
    tw2 = _text_w(f_title, title_text)
    tx = (W - tw2) // 2
    ty = card_y + card_h + 18

    # Dark semi-transparent box behind title
    pad = 12
    draw.rounded_rectangle(
        [tx - pad, ty - 6, tx + tw2 + pad, ty + f_title.size + 6],
        radius=10, fill=(0, 0, 0, 160)
    )
    draw_text_shadowed(draw, (tx, ty), title_text, f_title,
                       fill=(255, 255, 255), shadow=(0, 0, 0))

    # ── Progress bar ──
    pb_y = ty + f_title.size + 22
    pb_m = 160
    draw_progress_bar(draw, pb_m, pb_y, W - pb_m * 2, palette)

    # ── Pill metadata row ──
    pill_y = pb_y + 22
    pills = [f"👁  {views}", f"⏱  {duration_text}", f"▶  @{player_username}"]
    total_w = sum(_text_w(f_small, p) + 14 * 2 + 12 for p in pills) - 12
    cx2 = (W - total_w) // 2
    for pill in pills:
        cx2 = draw_pill(draw, cx2, pill_y, pill, f_small, palette["neon"])

    # ── Equalizer bars ──
    draw_equalizer(draw, 38, H - 88, palette)

    # ── Top-left badge ──
    if is_live:
        live_col = random.choice(LIVE_BADGE_COLORS)
        draw_filled_badge(draw, 20, 20, "⬤  LIVE NOW", f_tag, live_col)
    else:
        draw_filled_badge(draw, 20, 20, "🎵  ZEFRONMUSIC", f_tag, (nr, ng, nb))

    # ── Top-right music note ──
    draw_text_shadowed(draw, (W - 68, 16), "♪", f_title, fill=(nr, ng, nb), shadow=(0, 0, 0))

    # ── Bottom bar ──
    bar_y = H - 54
    bar_h2 = 46
    strip = Image.new("RGBA", (W, bar_h2), (0, 0, 0, 130))
    bg.paste(strip, (0, bar_y), strip)
    draw = ImageDraw.Draw(bg, "RGBA")

    # Left: owner
    draw_filled_badge(draw, 16, bar_y + 8, "⭐  @crush_hu_tera", f_badge, (ar, ag, ab))

    # Right: channel
    chan_text = "📢  @JAN_AMP"
    chan_w2 = _text_w(f_badge, chan_text) + 14 * 2
    draw_filled_badge(draw, W - chan_w2 - 16, bar_y + 8, chan_text, f_badge, (nr, ng, nb))

    # Center: subtle dev credit (white, readable on dark bar)
    dev_text = "Dev :-  @JAN_AMP"
    dw = _text_w(f_meta, dev_text)
    draw.text(((W - dw) // 2, bar_y + 14), dev_text, font=f_meta,
              fill=(220, 220, 220, 180))

    return bg


async def get_thumb(videoid: str, player_username: str = None) -> str:
    if player_username is None:
        player_username = app.username

    cache_path = os.path.join(CACHE_DIR, f"{videoid}_v8.png")
    if os.path.exists(cache_path):
        return cache_path

    try:
        results = VideosSearch(f"https://www.youtube.com/watch?v={videoid}", limit=1)
        sr = await results.next()
        data = sr.get("result", [])[0]
        title = re.sub(r"\W+", " ", data.get("title", "Unknown Title")).title()
        thumbnail = data.get("thumbnails", [{}])[0].get("url", YOUTUBE_IMG_URL)
        duration = data.get("duration")
        views = data.get("viewCount", {}).get("short", "Unknown")
    except Exception:
        title, thumbnail, duration, views = "Unknown Title", YOUTUBE_IMG_URL, None, "Unknown"

    is_live = not duration or str(duration).lower() in {"live", "live now", ""}
    duration_text = "🔴 LIVE" if is_live else duration or "Unknown"

    raw_path = os.path.join(CACHE_DIR, f"raw_{videoid}.png")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    async with aiofiles.open(raw_path, "wb") as f:
                        await f.write(await resp.read())
    except Exception:
        return YOUTUBE_IMG_URL

    palette = random.choice(PALETTES)
    img = _build_image(raw_path, title, views, duration_text, player_username, is_live, palette)

    try:
        os.remove(raw_path)
    except OSError:
        pass

    if is_live:
        live_path = os.path.join(CACHE_DIR, f"{videoid}_live_{random.randint(0, 99999)}.png")
        img.convert("RGB").save(live_path, quality=95)
        return live_path

    img.convert("RGB").save(cache_path, quality=95)
    return cache_path


async def get_live_thumb_raw(videoid: str, thumbnail_url: str,
                              title: str, views: str, duration_text: str,
                              player_username: str) -> str:
    """Generate a fresh live thumbnail without caching (for color rotation)."""
    raw_path = os.path.join(CACHE_DIR, f"raw_live_{videoid}_{random.randint(0,999999)}.png")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail_url) as resp:
                if resp.status == 200:
                    async with aiofiles.open(raw_path, "wb") as f:
                        await f.write(await resp.read())
    except Exception:
        return None

    palette = random.choice(PALETTES)
    img = _build_image(raw_path, title, views, duration_text, player_username, True, palette)

    try:
        os.remove(raw_path)
    except OSError:
        pass

    out_path = os.path.join(CACHE_DIR, f"live_rot_{videoid}_{random.randint(0,999999)}.png")
    img.convert("RGB").save(out_path, quality=92)
    return out_path


async def _live_rotate_task(chat_id: int, message, videoid: str,
                             thumbnail_url: str, title: str,
                             player_username: str, markup):
    """Background task: edit the Now Playing message every 5 s with a new colour."""
    from pyrogram.types import InputMediaPhoto
    interval = 5
    max_runs = 120  # stop after 10 minutes
    runs = 0
    while runs < max_runs:
        await asyncio.sleep(interval)
        try:
            new_path = await get_live_thumb_raw(
                videoid, thumbnail_url, title,
                "Unknown", "🔴 LIVE", player_username
            )
            if not new_path:
                break
            await message.edit_media(
                media=InputMediaPhoto(media=new_path, has_spoiler=True),
                reply_markup=markup,
            )
            try:
                os.remove(new_path)
            except OSError:
                pass
        except Exception:
            break
        runs += 1
    _live_tasks.pop(chat_id, None)


def start_live_rotation(chat_id: int, message, videoid: str,
                         thumbnail_url: str, title: str,
                         player_username: str, markup):
    """Start (or restart) the live colour-rotation background task for a chat."""
    stop_live_rotation(chat_id)
    task = asyncio.create_task(
        _live_rotate_task(chat_id, message, videoid, thumbnail_url,
                          title, player_username, markup)
    )
    _live_tasks[chat_id] = task


def stop_live_rotation(chat_id: int):
    """Cancel any running live-rotation task for this chat."""
    task = _live_tasks.pop(chat_id, None)
    if task and not task.done():
        task.cancel()

# ======================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (suraj08832) 😎
# 🧑‍💻 Developer : https://t.me/AMP_mah
# 🔗 Source link : GitHub.com/suraj08832/Purvi-V2
# 📢 Telegram channel : t.me/JAN_AMP
# =======================================================
