from pyrogram import filters, types
from che import app, lang, db
from che.helpers import admin_check

# --- KAPATMA BUTONU FONKSİYONU ---
def close_markup(_):
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    # Eğer dil verisi boşsa veya 'close' anahtarı yoksa "❌ Kapat" yazsın
    btn_text = _["close"] if (_ and "close" in _) else "❌ Kapat"
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(text=btn_text, callback_data="close")]]
    )

@app.on_message(filters.command(["loop", "döngü", "tekrar"]) & filters.group)
@admin_check
@lang.language()
# HATA ÇÖZÜMÜ: "_=None" yaparak bu argümanı isteğe bağlı hale getirdik.
# Böylece sistem bu argümanı gönderemese bile bot çökmez.
async def loop_command(client, message: types.Message, _=None):
    # Eğer sistem dil dosyasını (_) gönderemediyse, hata vermemesi için boş bir sözlük oluşturuyoruz.
    # Bu sayede kod aşağıdaki 'else' kısımlarındaki varsayılan Türkçe metinleri kullanır.
    if not _:
        _ = {}

    # Komutun yanındaki argümanı al (Örn: /loop 3 -> args=["loop", "3"])
    args = message.command
    
    # Eğer sadece /loop yazıldıysa kullanım kılavuzu göster
    if len(args) == 1:
        return await message.reply_text(
            _["loop_usage"] if "loop_usage" in _ else "Kullanım:\n/loop [1-10 arası sayı]\n/loop [aç/kapat]"
        )

    state = args[1].lower()

    # --- DÖNGÜYÜ KAPATMA ---
    if state in ["disable", "off", "kapat", "0"]:
        await db.set_loop(message.chat.id, 0)
        return await message.reply_text(
            text=_["loop_disabled"] if "loop_disabled" in _ else "❌ Döngü kapatıldı.",
            reply_markup=close_markup(_)
        )

    # --- DÖNGÜYÜ AÇMA (Varsayılan: 10) ---
    elif state in ["enable", "on", "aç", "aktif"]:
        await db.set_loop(message.chat.id, 10)
        return await message.reply_text(
            text=_["loop_enabled"] if "loop_enabled" in _ else "✅ Döngü aktif edildi (10 tekrar).",
            reply_markup=close_markup(_)
        )

    # --- SAYI BELİRTEREK AÇMA ---
    elif state.isdigit():
        count = int(state)
        if 1 <= count <= 10:
            await db.set_loop(message.chat.id, count)
            return await message.reply_text(
                text=_["loop_set"].format(count) if "loop_set" in _ else f"✅ Döngü {count} kez tekrarlanacak.",
                reply_markup=close_markup(_)
            )
        else:
            return await message.reply_text(
                "Lütfen 1 ile 10 arasında bir sayı girin."
            )
            
    else:
        return await message.reply_text(
            "Hatalı komut. Örnek: `/loop 3` veya `/loop kapat`"
        )
