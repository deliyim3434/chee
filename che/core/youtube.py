
import os
import re
import yt_dlp
import random
import asyncio
import aiohttp
from pathlib import Path
from py_yt import Playlist, VideosSearch
from che import logger
from che.helpers import Track, utils

class YouTube:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.cookie_dir = "anony/cookies"
        self.cookies_file = f"{self.cookie_dir}/cookies.txt"
        self.regex = re.compile(
            r"(https?://)?(www\.|m\.|music\.)?"
            r"(youtube\.com/(watch\?v=|shorts/|playlist\?list=)|youtu\.be/)"
            r"([A-Za-z0-9_-]{11}|PL[A-Za-z0-9_-]+)([&?][^\s]*)?"
        )
        # KlasÃ¶r yoksa oluÅŸtur
        if not os.path.exists(self.cookie_dir):
            os.makedirs(self.cookie_dir)

    def get_cookies(self):
        # YÃ–NTEM 1: Ortam DeÄŸiÅŸkeninden (Config Var) Oku ve Yaz
        # Heroku'da GO_COOKIE adÄ±nda bir deÄŸiÅŸken oluÅŸturup iÃ§eriÄŸi oraya yapÄ±ÅŸtÄ±rÄ±n.
        env_cookie = os.getenv("GO_COOKIE")
        if env_cookie:
            if not os.path.exists(self.cookies_file):
                logger.info("Env deÄŸiÅŸkeninden cookie dosyasÄ± oluÅŸturuluyor...")
                with open(self.cookies_file, "w") as f:
                    f.write(env_cookie)
            return self.cookies_file

        # YÃ–NTEM 2: KlasÃ¶rdeki dosyalarÄ± kontrol et
        if os.path.exists(self.cookies_file):
            return self.cookies_file
        
        # KlasÃ¶rdeki diÄŸer .txt dosyalarÄ±na bak
        for file in os.listdir(self.cookie_dir):
            if file.endswith(".txt"):
                return f"{self.cookie_dir}/{file}"

        logger.warning("DÄ°KKAT: Cookie dosyasÄ± bulunamadÄ±! Ä°ndirmeler baÅŸarÄ±sÄ±z olabilir.")
        return None

    def valid(self, url: str) -> bool:
        return bool(re.match(self.regex, url))

    async def search(self, query: str, m_id: int, video: bool = False) -> Track | None:
        _search = VideosSearch(query, limit=1, with_live=False)
        results = await _search.next()
        if results and results["result"]:
            data = results["result"][0]
            return Track(
                id=data.get("id"),
                channel_name=data.get("channel", {}).get("name"),
                duration=data.get("duration"),
                duration_sec=utils.to_seconds(data.get("duration")),
                message_id=m_id,
                title=data.get("title")[:25],
                thumbnail=data.get("thumbnails", [{}])[-1].get("url").split("?")[0],
                url=data.get("link"),
                view_count=data.get("viewCount", {}).get("short"),
                video=video,
            )
        return None

    async def playlist(self, limit: int, user: str, url: str, video: bool) -> list[Track | None]:
        tracks = []
        try:
            plist = await Playlist.get(url)
            for data in plist["videos"][:limit]:
                track = Track(
                    id=data.get("id"),
                    channel_name=data.get("channel", {}).get("name", ""),
                    duration=data.get("duration"),
                    duration_sec=utils.to_seconds(data.get("duration")),
                    title=data.get("title")[:25],
                    thumbnail=data.get("thumbnails")[-1].get("url").split("?")[0],
                    url=data.get("link").split("&list=")[0],
                    user=user,
                    view_count="",
                    video=video,
                )
                tracks.append(track)
        except:
            pass
        return tracks

    async def download(self, video_id: str, video: bool = False) -> str | None:
        url = self.base + video_id
        ext = "mp4" if video else "webm"
        filename = f"downloads/{video_id}.{ext}"

        if Path(filename).exists():
            return filename

        cookie_path = self.get_cookies()
        
        base_opts = {
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "quiet": True,
            "noplaylist": True,
            "geo_bypass": True,
            "no_warnings": True,
            "overwrites": False,
            "nocheckcertificate": True,
            # GeliÅŸmiÅŸ Bot KorumasÄ± AyarlarÄ±
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "referer": "https://www.youtube.com/",
            "extractor_retries": 3,
            "socket_timeout": 15,
        }

        # EÄŸer cookie dosyasÄ± varsa ekle
        if cookie_path:
            base_opts["cookiefile"] = cookie_path
        else:
            # Cookie yoksa tarayÄ±cÄ± taklidi yapmayÄ± dene (Localhost iÃ§in)
            # base_opts["cookiesfrombrowser"] = ("chrome",) 
            pass

        if video:
            ydl_opts = {
                **base_opts,
                "format": "(bestvideo[height<=?720][width<=?1280][ext=mp4])+(bestaudio)",
                "merge_output_format": "mp4",
            }
        else:
            ydl_opts = {
                **base_opts,
                "format": "bestaudio[ext=webm][acodec=opus]",
            }

        def _download():
            # YoutubeDL nesnesini oluÅŸtur
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    ydl.download([url])
                except Exception as e:
                    logger.error(f"Ä°ndirme hatasÄ±: {str(e)}")
                    # EÄŸer Sign in hatasÄ± varsa ve cookie kullanÄ±yorsak, dosyayÄ± silip tekrar denemeyi Ã¶nlemek iÃ§in uyar
                    if "Sign in" in str(e) and cookie_path:
                        logger.error("KullandÄ±ÄŸÄ±nÄ±z Cookie PATLAMIÅ (GeÃ§ersiz). LÃ¼tfen yeni bir cookie alÄ±n.")
                    return None
            return filename

        return await asyncio.to_thread(_download)
