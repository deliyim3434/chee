import pyrogram
from pyrogram.enums import ChatMemberStatus, ParseMode
from pyrogram.types import BotCommand, BotCommandScopeAllPrivateChats, BotCommandScopeAllGroupChats, LinkPreviewOptions
import logging

# Config ve Logger'ı kendi yapınıza göre import edin
# Eğer hata alırsanız config.py dosyanızın olduğundan emin olun.
try:
    from che import config, logger
except ImportError:
    import config
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("che")

# ─────────────────────────────────────────────
# 📜 BOT KOMUT TANIMLARI
# ─────────────────────────────────────────────

PRIVATE_COMMANDS = [
    BotCommand("start", "🌟 Botu başlat ve müzik keyfine başla"),
    BotCommand("yardim", "🧠 Yardım menüsünü göster"),
]

GROUP_COMMANDS = [
    BotCommand("oynat", "🎶 Seçilen şarkıyı çalmaya başlar"),
    BotCommand("voynat", "🎬 Video oynatımını başlatır"),
    BotCommand("atla", "⏭️ Sonraki şarkıya geç"),
    BotCommand("duraklat", "⏸️ Şarkıyı duraklat"),
    BotCommand("devam", "▶️ Şarkıyı devam ettir"),
    BotCommand("son", "⛔ Oynatmayı durdur"),
    BotCommand("karistir", "🔀 Çalma listesini karıştır"),
    BotCommand("dongu", "🔁 Tekrar modunu etkinleştir"),
    BotCommand("sira", "📋 Kuyruğu göster"),
    BotCommand("ilerisar", "⏩ Şarkıyı ileri sar"),
    BotCommand("gerisar", "⏪ Şarkıyı geri sar"),
    BotCommand("playlist", "🎼 Kendi çalma listen"),
    BotCommand("bul", "🔍 Müzik ara ve indir"),
    BotCommand("ayarlar", "⚙️ Grup ayarlarını göster"),
    BotCommand("restart", "♻️ Botu yeniden başlat"),
    BotCommand("reload", "🔄 Admin önbelleğini yenile"),
]

# ─────────────────────────────────────────────
# 🤖 BOT SINIFI
# ─────────────────────────────────────────────

class Bot(pyrogram.Client):
    def __init__(self):
        super().__init__(
            name="che",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            parse_mode=ParseMode.HTML,
            max_concurrent_transmissions=7,
            link_preview_options=LinkPreviewOptions(is_disabled=True),
        )
        self.owner = config.OWNER_ID
        self.logger_id = config.LOGGER_ID
        self.bl_users = pyrogram.filters.user()
        self.sudoers = pyrogram.filters.user(self.owner)

    async def boot(self):
        """
        Botu başlatır, log grubunu kontrol eder ve komutları yükler.
        """
        await super().start()
        self.id = self.me.id
        self.name = self.me.first_name
        self.username = self.me.username
        self.mention = self.me.mention

        # Log Grubu Kontrolü
        try:
            await self.send_message(self.logger_id, f"🚀 **{self.name} Başlatıldı!**\n\n**Kullanıcı Adı:** @{self.username}")
            get = await self.get_chat_member(self.logger_id, self.id)
            if get.status != ChatMemberStatus.ADMINISTRATOR:
                logger.error("Bot log grubunda yönetici değil!")
                raise SystemExit("Hata: Lütfen botu log grubunda yönetici yapın.")
        except Exception as ex:
            logger.error(f"Log grubuna erişim hatası: {ex}")
            raise SystemExit(f"Bot log grubuna erişemedi. ID: {self.logger_id}")

        # Komutları Telegram'a Kaydetme
        try:
            await self.set_bot_commands(PRIVATE_COMMANDS, scope=BotCommandScopeAllPrivateChats())
            await self.set_bot_commands(GROUP_COMMANDS, scope=BotCommandScopeAllGroupChats())
            logger.info("Bot komutları başarıyla yüklendi.")
        except Exception as e:
            logger.warning(f"Komutlar yüklenirken bir hata oluştu: {e}")

        logger.info(f"Bot @{self.username} olarak başarıyla aktif edildi.")

    async def stop(self):
        """
        Botu güvenli bir şekilde kapatır.
        """
        await super().stop()
        logger.info("Bot durduruldu.")

# Çalıştırma Bloğu
if __name__ == "__main__":
    app = Bot()
    app.run(app.boot())
