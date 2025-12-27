import os
import asyncio
from pyrogram import errors, filters, types
from che import app, db, lang

# Yayın durumunu kontrol etmek için global değişken
broadcasting = False

@app.on_message(filters.command(["broadcast", "gcast"]) & app.sudoers)
@lang.language()
async def _broadcast(_, message: types.Message):
    global broadcasting
    
    # 1. Yanıtlanan mesaj kontrolü
    if not message.reply_to_message:
        return await message.reply_text(message.lang["gcast_usage"])

    # 2. Çakışma kontrolü
    if broadcasting:
        return await message.reply_text(message.lang["gcast_active"])

    msg = message.reply_to_message
    count, ucount = 0, 0
    groups, users = [], []
    
    status_msg = await message.reply_text("🔍 Veritabanı taranıyor, binlerce hedef hazırlanıyor...")

    # 3. Veritabanından hedefleri çekme
    try:
        if "-nochat" not in message.command:
            groups = await db.get_chats()
        if "-user" in message.command:
            users = await db.get_users()
    except Exception as e:
        return await status_msg.edit_text(f"❌ Veritabanı hatası: {e}")

    # Mükerrer kayıtları temizle (Aynı ID'ye iki kez gitmesin)
    all_targets = list(set(groups + users))
    total_targets = len(all_targets)
    
    if not all_targets:
        return await status_msg.edit_text("❌ Yayın yapılacak hedef bulunamadı.")

    broadcasting = True
    await status_msg.edit_text(f"🚀 Yayın başladı!\n📊 Toplam Hedef: `{total_targets}`\n⏳ İşlem devam ediyor...")

    # 4. Logger Bildirimi
    try:
        await msg.forward(app.logger)
    except:
        pass

    # 5. Ana Yayın Döngüsü
    for chat_id in all_targets:
        if not broadcasting:
            break

        try:
            target = int(chat_id)
            
            # Mesajı Gönder (Kopyala veya İlet)
            if "-copy" in message.text:
                await msg.copy(target, reply_markup=msg.reply_markup)
            else:
                await msg.forward(target)
            
            if target in groups:
                count += 1
            else:
                ucount += 1
            
            # Her 20 mesajda bir admini bilgilendir (Binlerce grupta donma hissini engeller)
            if (count + ucount) % 20 == 0:
                try:
                    await status_msg.edit_text(
                        f"⏳ **Yayın Devam Ediyor...**\n"
                        f"✅ Başarılı: `{count + ucount}` / `{total_targets}`\n"
                        f"👥 Gruplar: `{count}` | 👤 Üyeler: `{ucount}`"
                    )
                except:
                    pass

            # Spam koruması için kısa mola (Binlerce grup için ideal süre)
            await asyncio.sleep(0.3)

        except errors.FloodWait as fw:
            # Telegram sınırı: fw.value saniye bekle
            await asyncio.sleep(fw.value + 5)
        
        except (errors.UserIsBlocked, errors.InputUserDeactivated, errors.PeerIdInvalid, 
                errors.ChatWriteForbidden, errors.ChatAdminRequired, errors.ChannelPrivate, errors.ChannelInvalid):
            # Akıllı Temizlik: Fonksiyon ismi ne olursa olsun bulup siler, hata vermez
            try:
                for func_name in ["remove_user", "delete_user", "remove_chat", "delete_chat", "remove_served_chat"]:
                    if hasattr(db, func_name):
                        func = getattr(db, func_name)
                        await func(target)
                        break
            except:
                pass # Silme fonksiyonu hatalıysa bile yayını bozma
            
        except Exception:
            continue

    # 6. Sonuç Bildirimi
    broadcasting = False
    
    final_report = (
        f"✅ **Yayın Başarıyla Tamamlandı!**\n\n"
        f"👥 **Toplam Grup:** `{count}`\n"
        f"👤 **Toplam Kullanıcı:** `{ucount}`\n"
        f"❌ **Ulaşılamayan:** `{total_targets - (count + ucount)}`"
    )
    
    await status_msg.edit_text(final_report)

@app.on_message(filters.command(["stop_broadcast"]) & app.sudoers)
async def _stop_broadcast(_, message: types.Message):
    global broadcasting
    if not broadcasting:
        return await message.reply_text("❌ Şu an aktif bir yayın yok.")
    
    broadcasting = False
    await message.reply_text("🛑 Yayın durdurma sinyali gönderildi. İşlem birazdan sonlanacak.")
