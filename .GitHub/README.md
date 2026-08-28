<p align="center">
  <img src="https://user-images.githubusercontent.com/73097560/115834477-dbab4500-a447-11eb-908a-139a6edaec5c.gif"/>
</p>

<h2 align="center">
    ───「zefron ᴍᴜsɪᴄ 」───
</h2>

<p align="center">
  <img src="https://user-images.githubusercontent.com/73097560/115834477-dbab4500-a447-11eb-908a-139a6edaec5c.gif"/>
</p>

<p align="center">
  <img src="https://files.catbox.moe/971v6c.jpg">
</p>

<p align="center">
<b>𝗗𝗘𝗣𝗟𝗢𝗬𝗠𝗘𝗡𝗧 𝗠𝗘𝗧𝗛𝗢𝗗𝗦</b>
</p>

<h2 align="center"> ─「 ᴅᴇᴘʟᴏʏ ᴏɴ ʜᴇʀᴏᴋᴜ 」─ </h2>

<p align="center">
  <img src="https://user-images.githubusercontent.com/73097560/115834477-dbab4500-a447-11eb-908a-139a6edaec5c.gif"/>
</p>

<p align="center">
  <a href="https://dashboard.heroku.com/new?template=https://github.com/zefronxd/ZEFRONMUSIC">
    <img src="https://img.shields.io/badge/Deploy%20On%20Heroku-8A2BE2?style=for-the-badge&logo=heroku" width="230" height="40"/>
  </a>
</p>

<p align="center">
  <img src="https://user-images.githubusercontent.com/73097560/115834477-dbab4500-a447-11eb-908a-139a6edaec5c.gif"/>
</p>

<h1 align="center">─「 ǫᴜɪᴄᴋ sᴇᴛᴜᴘ 」─</h1>

## VPS deployment (recommended)

This bot runs as a background Telegram service on a VPS. It does not need
`webserver.py`, an exposed HTTP port, or a Render keep-alive URL.

1. Install Ubuntu/Debian packages and clone the project:

   ```bash
   sudo apt-get update
   sudo apt-get install -y git
   git clone https://github.com/zefronxd/ZEFRONMUSIC /opt/zefronmusic
   cd /opt/zefronmusic
   ```

2. Create the environment file and fill in the required values:

   ```bash
   cp .env.example .env
   nano .env
   ```

3. Install dependencies and register the systemd service:

   ```bash
   sudo bash deploy/install-vps.sh
   ```

   The installer adds FFmpeg, creates an isolated Python environment, and
   starts the bot with automatic restart enabled.

4. Manage and inspect the bot:

   ```bash
   sudo systemctl restart zefronmusic
   sudo systemctl stop zefronmusic
   sudo journalctl -u zefronmusic -f
   ```

 1. **🔧 ᴜᴘᴅᴀᴛᴇ & ᴜᴘɢʀᴀᴅᴇ**
   ```bash
   sudo apt-get update && sudo apt-get upgrade -y
   ```

 2. **📦 ɪɴsᴛᴀʟʟ ʀᴇǫᴜɪʀᴇᴅ ᴘᴀᴄᴋᴀɢᴇs**
   ```bash
   sudo apt-get install python3-pip ffmpeg -y
   ```
 4. **📌 sᴇᴛᴛɪɴɢ ᴜᴘ ᴘɪᴘ**
   ```bash
   sudo pip3 install -U pip
   ```
 5. **⚡ ɪɴsᴛᴀʟʟɪɴɢ ɴᴏᴅᴇ**
   ```bash
   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.38.0/install.sh | bash && source ~/.bashrc && nvm install v18
   ```
 6. **📥 ᴄʟᴏɴᴇ ᴛʜᴇ ʀᴇᴘᴏsɪᴛᴏʀʏ**
   ```bash
   git clone https://github.com/zefronxd/ZEFRONMUSIC && cd New-Purvi
   ```
 7. **📂 ɪɴsᴛᴀʟʟ ʀᴇǫᴜɪʀᴇᴍᴇɴᴛs**
   ```bash
   pip3 install -U -r requirements.txt
   ```
 8. **📝 ᴄʀᴇᴀᴛᴇ .env ᴡɪᴛʜ sᴀᴍᴘʟᴇ.env**
   ```bash
   cp sample.env .env
   ```
   - Edit .env with your vars
 9. **✏️ ᴇᴅɪᴛɪɴɢ ᴠᴀʀs**
   ```bash
   vi .env
   ```
   - Edit .env with your values.
   - Press `I` button on keyboard to start editing.
   - Press `Ctrl + C`  once you are done with editing vars and type `:wq` to save .env or `:qa` to exit editing.
10. **🔗 ɪɴsᴛᴀʟʟɪɴɢ ᴛᴍᴜx**
    ```bash
    sudo apt install tmux -y && tmux
    ```
11. **🚀 ʀᴜɴ ᴛʜᴇ ʙᴏᴛ**
    ```bash
    bash start
    ```

<p align="center">
  <img src="https://user-images.githubusercontent.com/73097560/115834477-dbab4500-a447-11eb-908a-139a6edaec5c.gif"/>
</p>

<h1 align="center">─「 ©️ ʟɪᴄᴇɴsᴇ ɴᴏᴛᴇ 」─</h1>

<p>©️ 2025-26 ᴀʟʟ ʀɪɢʜᴛs ʀᴇsᴇʀᴠᴇᴅ ʙʏ <strong>ᴘᴜʀᴠɪ ʙᴏᴛs (<a href="https://github.com/suraj08832">suraj08832</a>)</strong> 🚀</p>

<p>• ᴛʜɪs <a href="https://github.com/zefronxd/ZEFRONMUSIC">sᴏᴜʀᴄᴇ ᴄᴏᴅᴇ</a> ɪs ʀᴇʟᴇᴀsᴇᴅ ᴜɴᴅᴇʀ ᴛʜᴇ <strong><a href="https://github.com/zefronxd/ZEFRONMUSIC/blob/main/LICENSE">MIT LICENSE</a></strong> 📜</p>

<p>• ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ ғᴏʀᴋɪɴɢ, ɪᴍᴘᴏʀᴛɪɴɢ, ᴏʀ ᴜsɪɴɢ ᴛʜɪs ᴄᴏᴅᴇ ᴡɪᴛʜᴏᴜᴛ ᴘʀᴏᴘᴇʀ ᴄʀᴇᴅɪᴛ ᴡɪʟʟ ʀᴇsᴜʟᴛ ɪɴ ʟᴇɢᴀʟ ᴀᴄᴛɪᴏɴ ⚠️.</p>

<p align="center">  
  <img src="https://user-images.githubusercontent.com/73097560/115834477-dbab4500-a447-11eb-908a-139a6edaec5c.gif"/>  
</p>  

<h1 align="center">─「 ᴄᴏɴᴛᴀᴄᴛ ᴍᴇ 」─</h1>  

<p align="center">  
  <img src="https://user-images.githubusercontent.com/73097560/115834477-dbab4500-a447-11eb-908a-139a6edaec5c.gif"/>  
</p>  

<p align="center">  
  <!-- Dev -->  
  <a href="https://https://t.me/AMP_mah">  
    <img src="https://img.shields.io/badge/ᴅᴇᴠ-ᴀʟᴘʜᴀ-ff9800?style=for-the-badge&logo=telegram&logoColor=white"/> 
  </a>  

  <!-- Purvi Bots -->    
  <a href="https://t.me/JAN_AMP">  
    <img src="https://img.shields.io/badge/ᴘᴜʀᴠ𝙸-%20ʙᴏᴛs-2196f3?style=for-the-badge&logo=telegram&logoColor=white"/> 
  </a>  

  <!-- Instagram -->    
  <a href="https://instagram.com/careless__02">  
    <img src="https://img.shields.io/badge/𝙸ɴѕᴛᴀɢʀᴀᴍ-d62976?style=for-the-badge&logo=instagram&logoColor=white"/>  
  </a>  
</p>  

<p align="center">  
  <img src="https://user-images.githubusercontent.com/73097560/115834477-dbab4500-a447-11eb-908a-139a6edaec5c.gif"/>  
</p>
