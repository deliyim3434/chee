import os
from os import getenv
from dotenv import load_dotenv
from pyrogram import filters

load_dotenv()

# ==========================================
# 1. BÖLÜM: DEĞİŞKENLER (GLOBAL)
# ==========================================

API_ID = int(getenv("API_ID", "0"))
API_HASH = getenv("API_HASH")
BOT_TOKEN = getenv("BOT_TOKEN")
MONGO_URL = getenv("MONGO_URL")
LOGGER_ID = int(getenv("LOGGER_ID", "-1003450545038"))
OWNER_ID = int(getenv("OWNER_ID", "0"))

DURATION_LIMIT = int(getenv("DURATION_LIMIT", "190")) * 60
QUEUE_LIMIT = int(getenv("QUEUE_LIMIT", "20"))
PLAYLIST_LIMIT = int(getenv("PLAYLIST_LIMIT", "20"))

# Song.py için gerekli olan ek değişkenler
SONG_DOWNLOAD_DURATION = int(getenv("SONG_DOWNLOAD_DURATION", "180"))
SONG_DOWNLOAD_DURATION_LIMIT = SONG_DOWNLOAD_DURATION * 60
BANNED_USERS = filters.user() # Başlangıçta boş filtre

SESSION1 = getenv("SESSION", None)
SESSION2 = getenv("SESSION2", None)
SESSION3 = getenv("SESSION3", None)

SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/paynexmusiccc")
SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/paynexmusiccc")

def is_enabled(value):
    if str(value).lower() in ["true", "yes", "1", "on", "t"]:
        return True
    return False

AUTO_END = is_enabled(getenv("AUTO_END", "False"))
AUTO_LEAVE = is_enabled(getenv("AUTO_LEAVE", "False"))
VIDEO_PLAY = is_enabled(getenv("VIDEO_PLAY", "True"))

COOKIES_URL = [
    url for url in getenv("COOKIES_URL", "").split(" ")
    if url and "batbin.me" in url
]

DEFAULT_THUMB = getenv("DEFAULT_THUMB", "https://te.legra.ph/file/3e40a408286d4eda24191.jpg")
PING_IMG = getenv("PING_IMG", "https://previews.123rf.com/images/nuevoimg/nuevoimg2307/nuevoimg230702438/208122439-beautiful-girl-with-headphones-listening-to-music-3d-rendering.jpg")
START_IMG = getenv("START_IMG", "https://previews.123rf.com/images/nuevoimg/nuevoimg2307/nuevoimg230702438/208122439-beautiful-girl-with-headphones-listening-to-music-3d-rendering.jpg")


# ==========================================
# 2. BÖLÜM: CLASS YAPISI (ESKİ UYUMLULUK)
# ==========================================

class Config:
    def __init__(self):
        self.API_ID = API_ID
        self.API_HASH = API_HASH
        self.BOT_TOKEN = BOT_TOKEN
        self.MONGO_URL = MONGO_URL
        self.LOGGER_ID = LOGGER_ID
        self.OWNER_ID = OWNER_ID
        self.DURATION_LIMIT = DURATION_LIMIT
        self.QUEUE_LIMIT = QUEUE_LIMIT
        self.PLAYLIST_LIMIT = PLAYLIST_LIMIT
        self.BANNED_USERS = BANNED_USERS
        self.SONG_DOWNLOAD_DURATION = SONG_DOWNLOAD_DURATION
        self.SONG_DOWNLOAD_DURATION_LIMIT = SONG_DOWNLOAD_DURATION_LIMIT
        self.SESSION1 = SESSION1
        self.SESSION2 = SESSION2
        self.SESSION3 = SESSION3
        self.SUPPORT_CHANNEL = SUPPORT_CHANNEL
        self.SUPPORT_CHAT = SUPPORT_CHAT
        self.AUTO_END = AUTO_END
        self.AUTO_LEAVE = AUTO_LEAVE
        self.VIDEO_PLAY = VIDEO_PLAY
        self.COOKIES_URL = COOKIES_URL
        self.DEFAULT_THUMB = DEFAULT_THUMB
        self.PING_IMG = PING_IMG
        self.START_IMG = START_IMG

    def check(self):
        missing = []
        if not self.API_ID: missing.append("API_ID")
        if not self.API_HASH: missing.append("API_HASH")
        if not self.BOT_TOKEN: missing.append("BOT_TOKEN")
        if not self.MONGO_URL: missing.append("MONGO_URL")
        if not self.SESSION1: missing.append("SESSION1")
        
        if missing:
            print(f"UYARI: Config sınıfında eksik değişkenler: {', '.join(missing)}")

# ==========================================
# 3. BÖLÜM: GÜVENLİK KONTROLÜ (GLOBAL)
# ==========================================
if not API_ID or not API_HASH or not BOT_TOKEN or not SESSION1:
    print("WARNING: Temel değişkenler eksik! (.env dosyasını kontrol et)")
