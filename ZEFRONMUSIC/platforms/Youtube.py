import os
import re
import asyncio
import aiohttp
import yt_dlp
import glob
import logging
from typing import Union

from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from py_yt import VideosSearch, Playlist

from ZEFRONMUSIC.utils.formatters import time_to_seconds

# ── Download API config ────────────────────────────────────────────────────────
# Keep the old names for existing deployments, while also supporting the names
# used by the imported Replit project.
API_URL = (
    os.environ.get("MusicSp_API_URL")
    or os.environ.get("SPARROW_API_URL")
    or os.environ.get("ApiUrl")
    or os.environ.get("SHRUTI_API_URL")
    or "https://apisparrow.site"
).rstrip("/")
API_KEY = (
    os.environ.get("MusicSp_API_KEY")
    or os.environ.get("SPARROW_API_KEY")
    or os.environ.get("APIKey")
    or os.environ.get("SHRUTI_API_KEY")
    or ""
).strip()
FAST_MEDIA_API_URL = os.environ.get(
    "FAST_MEDIA_API_URL",
    "https://zefronapi-62506ec361ff.herokuapp.com/api/media",
).strip()
DOWNLOAD_DIR = "downloads"
LOGGER = logging.getLogger(__name__)
DOWNLOAD_TIMEOUT = aiohttp.ClientTimeout(
    total=180,
    connect=30,
    sock_connect=30,
    sock_read=60,
)


def _video_id_from_link(link: str) -> Union[str, None]:
    link = str(link or "").strip()
    if "v=" in link:
        video_id = link.split("v=", 1)[1].split("&", 1)[0]
    elif "youtu.be/" in link:
        video_id = link.split("youtu.be/", 1)[1].split("?", 1)[0].split("&", 1)[0]
    else:
        video_id = link.rsplit("/", 1)[-1].split("?", 1)[0]
    if not video_id or len(video_id) < 3:
        return None
    return video_id


def _download_endpoint() -> str:
    return API_URL if API_URL.endswith("/download") else f"{API_URL}/download"


async def _download_from_fast_api(
    video_id: str, media_type: str, file_path: str
) -> bool:
    """Use the no-cookie media endpoint before YouTube direct extraction."""
    temp_path = f"{file_path}.fast.part"
    try:
        async with aiohttp.ClientSession() as session:
            params = {
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "type": media_type,
                "quality": "360",
            }
            async with session.get(
                FAST_MEDIA_API_URL,
                params=params,
                timeout=DOWNLOAD_TIMEOUT,
            ) as resp:
                if resp.status != 200:
                    LOGGER.warning("Fast media API returned HTTP %s", resp.status)
                    return False

                content_type = resp.headers.get("Content-Type", "").lower()
                if "json" in content_type:
                    payload = await resp.json(content_type=None)
                    media_url = (
                        payload.get("url")
                        or payload.get("download_url")
                        or payload.get("link")
                    )
                    if not media_url:
                        return False
                    async with session.get(
                        media_url,
                        timeout=DOWNLOAD_TIMEOUT,
                    ) as media_resp:
                        if media_resp.status != 200:
                            return False
                        with open(temp_path, "wb") as output:
                            async for chunk in media_resp.content.iter_chunked(131072):
                                output.write(chunk)
                else:
                    with open(temp_path, "wb") as output:
                        async for chunk in resp.content.iter_chunked(131072):
                            output.write(chunk)

        if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
            os.replace(temp_path, file_path)
            return True
        return False
    except Exception as exc:
        LOGGER.warning("Fast media API failed: %s", type(exc).__name__)
        return False
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass


async def _download_from_api(video_id: str, media_type: str, file_path: str) -> bool:
    """Download from the configured API, rejecting JSON error responses."""
    if not API_KEY:
        return False

    temp_path = f"{file_path}.part"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                _download_endpoint(),
                params={
                    "url": video_id,
                    "type": media_type,
                    "api_key": API_KEY,
                },
                timeout=DOWNLOAD_TIMEOUT,
            ) as resp:
                if resp.status != 200:
                    LOGGER.warning("YouTube API returned HTTP %s", resp.status)
                    return False

                content_type = resp.headers.get("Content-Type", "").lower()
                if "json" in content_type:
                    LOGGER.warning("YouTube API returned a JSON error response")
                    return False

                with open(temp_path, "wb") as output:
                    async for chunk in resp.content.iter_chunked(131072):
                        output.write(chunk)

        if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
            os.replace(temp_path, file_path)
            return True
        return False
    except Exception as exc:
        LOGGER.warning("YouTube API download failed: %s", type(exc).__name__)
        return False
    finally:
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass


def _download_with_ytdlp(video_id: str, media_type: str) -> Union[str, None]:
    """Fallback downloader with a second YouTube client for intermittent 403s."""
    source = f"https://www.youtube.com/watch?v={video_id}"
    output_template = os.path.join(DOWNLOAD_DIR, f"{video_id}.%(ext)s")
    clients = (None, "android")

    for client in clients:
        options = {
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "retries": 2,
            "socket_timeout": 60,
            "force_ipv4": True,
            "geo_bypass": True,
            "outtmpl": output_template,
            "http_headers": {
                "User-Agent": (
                    "Mozilla/5.0 (X11; Linux x86_64) "
                    "AppleWebKit/537.36 Chrome/131.0 Safari/537.36"
                ),
                "Referer": "https://www.youtube.com/",
            },
        }
        if client:
            options["extractor_args"] = {
                "youtube": {"player_client": [client]}
            }

        if media_type == "audio":
            options.update(
                {
                    "format": "bestaudio/best",
                    "postprocessors": [
                        {
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "mp3",
                            "preferredquality": "192",
                        }
                    ],
                }
            )
        else:
            options["format"] = (
                "bestvideo[ext=mp4]+bestaudio[ext=m4a]/"
                "best[ext=mp4]/best"
            )

        try:
            with yt_dlp.YoutubeDL(options) as ydl:
                result = ydl.download([source])
            if result:
                continue

            candidates = [
                path
                for path in glob.glob(os.path.join(DOWNLOAD_DIR, f"{video_id}.*"))
                if not path.endswith((".part", ".ytdl"))
                and os.path.isfile(path)
                and os.path.getsize(path) > 0
            ]
            if media_type == "audio":
                candidates = [
                    path for path in candidates if path.lower().endswith(".mp3")
                ] or candidates
            if candidates:
                return max(candidates, key=os.path.getmtime)
        except Exception as exc:
            LOGGER.warning(
                "yt-dlp %s client failed: %s",
                client or "default",
                type(exc).__name__,
            )

    LOGGER.warning("All yt-dlp download clients failed")
    return None


async def _download_media(link: str, media_type: str, extension: str) -> Union[str, None]:
    video_id = _video_id_from_link(link)
    if not video_id:
        return None

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.{extension}")

    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        return file_path

    if await _download_from_fast_api(video_id, media_type, file_path):
        return file_path

    if await _download_from_api(video_id, media_type, file_path):
        return file_path

    fallback_path = await asyncio.to_thread(_download_with_ytdlp, video_id, media_type)
    if fallback_path:
        return fallback_path
    return None


async def download_song(link: str) -> Union[str, None]:
    return await _download_media(link, "audio", "mp3")


async def download_video(link: str) -> Union[str, None]:
    return await _download_media(link, "video", "mp4")


class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        return bool(re.search(self.regex, link))

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)

        for message in messages:
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        return text[entity.offset : entity.offset + entity.length]

            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        return None

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]

        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            vidid = result["id"]
            duration_sec = int(time_to_seconds(duration_min)) if duration_min else 0

        return title, duration_min, duration_sec, thumbnail, vidid

    async def title(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]

        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            return result["title"]

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]

        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            return result["duration"]

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]

        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            return result["thumbnails"][0]["url"].split("?")[0]

    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]

        try:
            downloaded_file = await download_video(link)
            if downloaded_file:
                return 1, downloaded_file
            return 0, "Video download failed"
        except Exception as e:
            return 0, f"Video download error: {e}"

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid:
            link = self.listbase + link
        if "&" in link:
            link = link.split("&")[0]

        try:
            plist = await Playlist.get(link)
        except Exception:
            return []

        videos = plist.get("videos") or []
        ids = []
        for data in videos[:limit]:
            if not data:
                continue
            vid = data.get("id")
            if not vid:
                continue
            ids.append(vid)
        return ids

    async def track(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]

        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            vidid = result["id"]
            yturl = result["link"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]

        track_details = {
            "title": title,
            "link": yturl,
            "vidid": vidid,
            "duration_min": duration_min,
            "thumb": thumbnail,
            "artist": result.get("channel", {}).get("name", "") if result else "",
        }
        return track_details, vidid

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]

        ytdl_opts = {"quiet": True}
        ydl = yt_dlp.YoutubeDL(ytdl_opts)
        with ydl:
            formats_available = []
            r = ydl.extract_info(link, download=False)
            for fmt in r["formats"]:
                try:
                    if "dash" not in str(fmt["format"]).lower():
                        formats_available.append(
                            {
                                "format": fmt["format"],
                                "filesize": fmt.get("filesize"),
                                "format_id": fmt["format_id"],
                                "ext": fmt["ext"],
                                "format_note": fmt["format_note"],
                                "yturl": link,
                            }
                        )
                except Exception:
                    continue
        return formats_available, link

    async def slider(self, link: str, query_type: int, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]

        a = VideosSearch(link, limit=10)
        result = (await a.next()).get("result")
        title = result[query_type]["title"]
        duration_min = result[query_type]["duration"]
        vidid = result[query_type]["id"]
        thumbnail = result[query_type]["thumbnails"][0]["url"].split("?")[0]
        return title, duration_min, thumbnail, vidid

    async def download(
        self,
        link: str,
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ) -> str:
        if videoid:
            link = self.base + link

        try:
            if video:
                downloaded_file = await download_video(link)
            else:
                downloaded_file = await download_song(link)

            if downloaded_file:
                return downloaded_file, True
            return None, False

        except Exception:
            return None, False


YouTube = YouTubeAPI()
