# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (suraj08832) 🚀
# 
# This source code is under MIT License 📜
# ❌ Unauthorized forking, importing, or using this code
#    without giving proper credit will result in legal action ⚠️
# 
# 📩 DM for permission : @zefron
# ===========================================================

import asyncio
import os
import shlex
from typing import Tuple

# Set GIT_PYTHON_REFRESH to quiet to suppress warnings
os.environ.setdefault("GIT_PYTHON_REFRESH", "quiet")
# Prevent git from prompting for credentials (hangs in non-interactive environments)
os.environ["GIT_TERMINAL_PROMPT"] = "0"
os.environ["GIT_ASKPASS"] = "echo"

try:
    from git import Repo
    from git.exc import GitCommandError, InvalidGitRepositoryError
    GIT_AVAILABLE = True
except (ImportError, Exception) as e:
    GIT_AVAILABLE = False
    Repo = None
    GitCommandError = Exception
    InvalidGitRepositoryError = Exception

import config

from ..logging import LOGGER


def install_req(cmd: str) -> Tuple[str, str, int, int]:
    async def install_requirements():
        args = shlex.split(cmd)
        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        return (
            stdout.decode("utf-8", "replace").strip(),
            stderr.decode("utf-8", "replace").strip(),
            process.returncode,
            process.pid,
        )

    return asyncio.get_event_loop().run_until_complete(install_requirements())


def git():
    if not GIT_AVAILABLE or Repo is None:
        LOGGER(__name__).warning(f"» ɢɪᴛ ɪs ɴᴏᴛ ᴀᴠᴀɪʟᴀʙʟᴇ. sᴋɪᴘᴘɪɴɢ ɢɪᴛ ᴏᴘᴇʀᴀᴛɪᴏɴs.")
        return
    
    REPO_LINK = config.UPSTREAM_REPO
    if config.GIT_TOKEN:
        GIT_USERNAME = REPO_LINK.split("com/")[1].split("/")[0]
        TEMP_REPO = REPO_LINK.split("https://")[1]
        UPSTREAM_REPO = f"https://{GIT_USERNAME}:{config.GIT_TOKEN}@{TEMP_REPO}"
    else:
        UPSTREAM_REPO = config.UPSTREAM_REPO
    try:
        repo = Repo()
        LOGGER(__name__).info(f"» ɢɪᴛ ᴄʟɪᴇɴᴛ ғᴏᴜɴᴅ [ᴠᴘs ᴅᴇᴘʟᴏʏᴇʀ]")
        try:
            origin = repo.remote("origin")
            origin.fetch()
            try:
                origin.pull(config.UPSTREAM_BRANCH)
            except GitCommandError:
                repo.git.reset("--hard", "FETCH_HEAD")
            install_req("pip3 install --no-cache-dir -r requirements.txt")
            LOGGER(__name__).info(f"» ꜰᴇᴛᴄʜɪɴɢ ᴜᴘᴅᴀᴛᴇs ꜰʀᴏᴍ ᴜᴘsᴛʀᴇᴀᴍ ʀᴇᴘᴏsɪᴛᴏʀʏ...")
        except Exception:
            pass
    except (GitCommandError, InvalidGitRepositoryError):
        LOGGER(__name__).info(
            f"» ɴᴏᴛ ᴀ ɢɪᴛ ʀᴇᴘᴏ (ᴅᴇᴘʟᴏʏᴇᴅ ᴠɪᴀ ʀᴇɴᴅᴇʀ/ʜᴇʀᴏᴋᴜ). sᴋɪᴘᴘɪɴɢ ɢɪᴛ ᴏᴘᴇʀᴀᴛɪᴏɴs."
        )
    except Exception as e:
        LOGGER(__name__).warning(f"» ɢɪᴛ ᴏᴘᴇʀᴀᴛɪᴏɴ ғᴀɪʟᴇᴅ: {e}. sᴋɪᴘᴘɪɴɢ ɢɪᴛ ᴏᴘᴇʀᴀᴛɪᴏɴs.")

# ===========================================================
# ©️ 2025-26 All Rights Reserved by Purvi Bots (suraj08832) 😎
# 
# 🧑‍💻 Developer : https://t.me/+BsvMgJITJvM5YWE1
# 🔗 Source link : GitHub.com/suraj08832/Purvi-V2
# 📢 Telegram channel : t.me/wife_girlfriend_group
# ===========================================================
