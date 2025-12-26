from pyrogram import types
from che import app, config, lang
from che.core.lang import lang_codes

class Inline:
    def __init__(self):
        self.ikm = types.InlineKeyboardMarkup
        self.ikb = types.InlineKeyboardButton

    def cancel_dl(self, text) -> types.InlineKeyboardMarkup:
        """İndirme işlemini iptal etme butonu."""
        return self.ikm([
            [self.ikb(text=f"✕ İptal • {text}", callback_data="cancel_dl")]
        ])

    def controls(
        self,
        chat_id: int,
        status: str = None,
        timer: str = None,
        remove: bool = False,
    ) -> types.InlineKeyboardMarkup:
        """Müzik çalar kontrol butonları."""
        keyboard = []

        # --- 0. SATIR: BİLGİ ÇUBUĞU ---
        if status:
            keyboard.append([
                self.ikb(text=f"• {status} •", callback_data=f"controls status {chat_id}")
            ])
        elif timer:
            keyboard.append([
                self.ikb(text=f"• {timer} •", callback_data=f"controls status {chat_id}")
            ])

        if not remove:
            # --- 1. SATIR: DÖNGÜ ve TEKRAR (BURASI EKLENDİ) ---
            # Loop butonu: 'controls loop' komutunu tetikler
            keyboard.append([
                self.ikb(text="TEKRAR", callback_data=f"controls loop {chat_id}"),
                
            ])

            # --- 2. SATIR: OYNATMA KONTROLLERİ ---
            keyboard.append([
                self.ikb(text="▷", callback_data=f"controls resume {chat_id}"),
                self.ikb(text="II", callback_data=f"controls pause {chat_id}"),
                self.ikb(text="‣‣I", callback_data=f"controls skip {chat_id}"),
                self.ikb(text="▢", callback_data=f"controls stop {chat_id}"),
            ])

            # --- 3. SATIR: SÜRE SARMA ---
            keyboard.append([
                self.ikb(text="≪ 10s", callback_data=f"controls seekback {chat_id} 10"),
                self.ikb(text="10s ≫", callback_data=f"controls seek {chat_id} 10"),
            ])

            # --- 4. SATIR: ALT MENÜ ---
            keyboard.append([
                self.ikb(text="💬 DESTEK", url=config.SUPPORT_CHAT),
                self.ikb(text="🚀 GRUBA EKLE", url=f"https://t.me/{app.username}?startgroup=true"),
            ])

        return self.ikm(keyboard)

    def help_markup(self, _lang: dict, back: bool = False) -> types.InlineKeyboardMarkup:
        """Yardım menüsü butonları."""
        if back:
            return self.ikm([
                [
                    self.ikb(text="« Geri", callback_data="help back"),
                    self.ikb(text="✕ Kapat", callback_data="help close"),
                ]
            ])

        return self.ikm([
            [
                self.ikb(text="Yönetici", callback_data="help admins"),
                self.ikb(text="Sudo", callback_data="help sudo")
            ],
            [
                self.ikb(text="Etiket Sistemi", callback_data="help etiket")
            ],
            [
                self.ikb(text="✕ Menüyü Kapat", callback_data="help close")
            ]
        ])

    def lang_markup(self, _lang: str) -> types.InlineKeyboardMarkup:
        """Dil değiştirme menüsü."""
        langs = lang.get_languages()
        buttons = [
            self.ikb(
                text=f"{'▣' if code == _lang else '▢'} {name}",
                callback_data=f"lang_change {code}",
            )
            for code, name in langs.items()
        ]
        # Butonları 2'li satırlar halinde dizer
        rows = [buttons[i : i + 2] for i in range(0, len(buttons), 2)]
        return self.ikm(rows)

    def settings_markup(self, lang_dict: dict, admin_only: bool, cmd_delete: bool, language: str, chat_id: int) -> types.InlineKeyboardMarkup:
        """Ayarlar menüsü."""
        return self.ikm([
            [
                self.ikb(text="Oynatma Modu", callback_data="settings"),
                self.ikb(text="Yönetici" if admin_only else "Herkes", callback_data="settings play")
            ],
            [
                self.ikb(text="Temizleyici", callback_data="settings"),
                self.ikb(text="☑ Açık" if cmd_delete else "☐ Kapalı", callback_data="settings delete")
            ],
            [
                self.ikb(text="Dil Seçimi", callback_data="settings"),
                self.ikb(text=f"{lang_codes.get(language, 'Unknown')}", callback_data="language")
            ],
        ])

    def start_key(self, lang_dict: dict, private: bool = False) -> types.InlineKeyboardMarkup:
        """Start komutu butonları."""
        oid = config.OWNER_ID
        return self.ikm([
            [
                self.ikb(text="✦ Beni Gruba Ekle ✦", url=f"https://t.me/{app.username}?startgroup=true")
            ],
            [
                self.ikb(text="Komutlar", callback_data="help"),
                self.ikb(text="Destek", url=config.SUPPORT_CHAT)
            ],
            [
                self.ikb(text="Geliştirici", url=f"tg://user?id={oid}")
            ]
        ])

    def yt_key(self, link: str) -> types.InlineKeyboardMarkup:
        """YouTube bağlantı butonları."""
        return self.ikm([
            [
                self.ikb(text="Kopyala", copy_text=link),
                self.ikb(text="YouTube ↗", url=link)
            ]
        ])

    def ping_markup(self, text: str) -> types.InlineKeyboardMarkup:
        """Ping komutu butonu."""
        return self.ikm([
            [self.ikb(text=f"⌁ {text}", url=config.SUPPORT_CHAT)]
        ])

    def play_queued(self, chat_id: int, item_id: str, _text: str) -> types.InlineKeyboardMarkup:
        """Sıradaki parça çalınırken gösterilen butonlar."""
        return self.ikm([
            [
                self.ikb(text="▷", callback_data=f"controls resume {chat_id}"),
                self.ikb(text="II", callback_data=f"controls pause {chat_id}"),
                self.ikb(text="‣‣I", callback_data=f"controls skip {chat_id}"),
                self.ikb(text="▢", callback_data=f"controls stop {chat_id}"),
            ]
        ])

    def queue_markup(self, chat_id: int, status: str, playing: bool) -> types.InlineKeyboardMarkup:
        """Liste/Queue komutu butonları."""
        return self.ikm([
            [
                self.ikb(
                    text=status,
                    callback_data=f"controls resume {chat_id}" if not playing else f"controls pause {chat_id}",
                ),
                self.ikb(text="✕", callback_data="help close")
            ]
        ])
