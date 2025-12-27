from pyrogram import filters, types
# KRİTİK DÜZELTME BURADA:
from app.che import app, lang, db
from app.che.helpers import admin_check
from app.che.utils.inline import close_markup

# ... kodun geri kalanı aynı ...
@app.on_message(filters.command(["loop", "döngü", "tekrar"]) & filters.group)
@admin_check
@lang.language()
async def loop_command(client, message: types.Message, _):
    args = message.command
    if len(args) == 1:
        return await message.reply_text(
            _["loop_usage"] if "loop_usage" in _ else "Kullanım:\n/loop [1-10 arası sayı]\n/loop [aç/kapat]"
        )

    state = args[1].lower()

    if state in ["disable", "off", "kapat", "0"]:
        await db.set_loop(message.chat.id, 0)
        return await message.reply_text(
            text=_["loop_disabled"] if "loop_disabled" in _ else "❌ Döngü kapatıldı.",
            reply_markup=close_markup(_)
        )

    elif state in ["enable", "on", "aç", "aktif"]:
        await db.set_loop(message.chat.id, 10)
        return await message.reply_text(
            text=_["loop_enabled"] if "loop_enabled" in _ else "✅ Döngü aktif edildi (10 tekrar).",
            reply_markup=close_markup(_)
        )

    elif state.isdigit():
        count = int(state)
        if 1 <= count <= 10:
            await db.set_loop(message.chat.id, count)
            return await message.reply_text(
                text=_["loop_set"].format(count) if "loop_set" in _ else f"✅ Döngü {count} kez tekrarlanacak.",
                reply_markup=close_markup(_)
            )
        else:
            return await message.reply_text("Lütfen 1 ile 10 arasında bir sayı girin.")
            
    else:
        return await message.reply_text("Hatalı komut. Örnek: `/loop 3` veya `/loop kapat`")
