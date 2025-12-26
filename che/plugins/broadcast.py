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
    chats, groups, users = [], [], []
    
    status_msg = await message.reply_text("🔍 Veriler toplanıyor ve yayın hazırlanıyor...")

    # 3. Veritabanından hedefleri çekme
    try:
        if "-nochat" not in message.command:
            groups.extend(await db.get_chats())
        if "-user" in message.command:
            users.extend(await db.get_users())
    except Exception as e:
        return await status_msg.edit_text(f"❌ Veritabanı hatası: {e}")

    all_targets = groups + users
    if not all_targets:
        return await status_msg.edit_text("❌ Yayın yapılacak hedef bulunamadı.")

    broadcasting = True
    await status_msg.edit_text(f"🚀 Yayın başladı!\nToplam Hedef: {len(all_targets)}")

    # 4. Logger Bildirimi
    try:
        await msg.forward(app.logger)
        log_notif = await app.send_message(
            chat_id=app.logger,
            text=f"📢 **Yayın Başlatıldı**\n**Admin:** {message.from_user.mention}\n**ID:** `{message.from_user.id}`"
        )
        await log_notif.pin()
    except:
        pass

    failed_reasons = {}

    # 5. Ana Yayın Döngüsü
    for chat_id in all_targets:
        if not broadcasting:
            break

        # ID'nin sayısal olup olmadığını doğrula (Loglardaki bozuk verileri eler)
        try:
            target = int(chat_id)
        except (ValueError, TypeError):
            continue

        try:
            # Mesajı Gönder (Kopyala veya İlet)
            if "-copy" in message.text:
                await msg.copy(target, reply_markup=msg.reply_markup)
            else:
                await msg.forward(target)
            
            if target in groups:
                count += 1
            else:
                ucount += 1
            
            # Spam koruması için kısa mola
            await asyncio.sleep(0.3)

        except errors.FloodWait as fw:
            # Telegram sınırı: fw.value saniye bekle
            await asyncio.sleep(fw.value + 5)
        
        except (errors.UserIsBlocked, errors.InputUserDeactivated, errors.PeerIdInvalid):
            # Kullanıcı hesabı silmiş veya botu engellemiş -> DB'den kaldır
            await db.remove_user(target) if target in users else await db.remove_chat(target)
            
        except (errors.ChatWriteForbidden, errors.ChatAdminRequired, errors.ChannelPrivate, errors.ChannelInvalid):
            # Bot gruptan atılmış veya yetkisi alınmış -> DB'den kaldır
            await db.remove_chat(target)
            
        except Exception as ex:
            # Diğer bilinmeyen hataları kaydet
            err_name = type(ex).__name__
            failed_reasons[err_name] = failed_reasons.get(err_name, 0) + 1
            continue

    # 6. Sonuç Bildirimi
    broadcasting = False
    final_report = message.lang["gcast_end"].format(count, ucount)
    
    if failed_reasons:
        report_path = "broadcast_report.txt"
        with open(report_path, "w") as f:
            f.write("--- Yayın Hata Raporu ---\n")
            for err, c in failed_reasons.items():
                f.write(f"Hata: {err} | Adet: {c}\n")
        
        await message.reply_document(
            document=report_path,
            caption=f"✅ **Yayın Tamamlandı**\n{final_report}\n\n⚠️ Bazı hatalar nedeniyle temizlik yapıldı (Rapor ekte)."
        )
        os.remove(report_path)
    else:
        await status_msg.edit_text(f"✅ **Yayın Başarıyla Tamamlandı!**\n{final_report}")

@app.on_message(filters.command(["stop_broadcast"]) & app.sudoers)
async def _stop_broadcast(_, message: types.Message):
    global broadcasting
    if not broadcasting:
        return await message.reply_text("❌ Şu an aktif bir yayın yok.")
    
    broadcasting = False
    await message.reply_text("🛑 Yayın durdurma sinyali gönderildi. Mevcut işlem bitince duracak.")