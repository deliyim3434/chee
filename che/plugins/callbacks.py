import re
from pyrogram import filters, types
from che import che, app, db, lang, queue, tg, yt
from che.helpers import admin_check, buttons, can_manage_vc

@app.on_callback_query(filters.regex("cancel_dl") & ~app.bl_users)
@lang.language()
async def cancel_dl(_, query: types.CallbackQuery):
    await query.answer()
    await tg.cancel(query)

@app.on_callback_query(filters.regex("controls") & ~app.bl_users)
@lang.language()
@can_manage_vc
async def _controls(_, query: types.CallbackQuery):
    args = query.data.split()
    action = args[1]
    chat_id = int(args[2])
    user = query.from_user.mention

    if not await db.get_call(chat_id):
        return await query.answer(query.lang["not_playing"], show_alert=True)

    if action == "status":
        return await query.answer(query.lang.get("playing_status", "Müzik çalıyor..."), show_alert=False)

    await query.answer(query.lang["processing"], show_alert=False)

    status = None
    reply = None
    should_delete_msg = False 

    # --- EYLEMLER ---

    if action == "pause":
        if not await db.playing(chat_id):
            return await query.answer(query.lang["play_already_paused"], show_alert=True)
        await che.pause(chat_id)
        status = query.lang["paused"]
        reply = query.lang["play_paused"].format(user)

    elif action == "resume":
        if await db.playing(chat_id):
            return await query.answer(query.lang["play_not_paused"], show_alert=True)
        await che.resume(chat_id)
        reply = query.lang["play_resumed"].format(user)

    elif action == "skip":
        await che.play_next(chat_id)
        status = query.lang["skipped"]
        reply = query.lang["play_skipped"].format(user)
        should_delete_msg = True

    elif action == "force":
        if len(args) >= 4:
            pos, media = queue.check_item(chat_id, args[3])
            if media and pos != -1:
                # Mevcut çalınan mesajı al
                current_item = queue.get_current(chat_id)
                m_id = current_item.message_id if current_item else None
                
                queue.force_add(chat_id, media, remove=pos)
                
                # Eski mesajları silmeye çalış
                to_delete = [m_id, media.message_id] if m_id else [media.message_id]
                try:
                    await app.delete_messages(chat_id=chat_id, message_ids=[i for i in to_delete if i], revoke=True)
                    media.message_id = None
                except:
                    pass
                
                msg = await app.send_message(chat_id=chat_id, text=query.lang["play_next"])
                
                if not media.file_path:
                    media.file_path = await yt.download(media.id, video=media.video)
                
                media.message_id = msg.id
                
                # anon yerine che kullanıldı
                return await che.play_media(chat_id, msg, media)
        else:
             return await query.edit_message_text(query.lang["play_expired"])

    elif action == "loop":
        await che.loop(chat_id, 3) 
        status = query.lang["loopped"]
        reply = query.lang["play_loopped"].format(user)
        should_delete_msg = True # İstediğiniz gibi True yapıldı

    elif action == "replay":
        await che.replay(chat_id)
        status = query.lang["replayed"]
        reply = query.lang["play_replayed"].format(user)
        should_delete_msg = True

    elif action == "stop":
        await che.stop(chat_id)
        status = query.lang["stopped"]
        reply = query.lang["play_stopped"].format(user)
        should_delete_msg = True

    elif action == "seek":
        seek_seconds = int(args[3]) if len(args) > 3 else 10
        await che.seek(chat_id, seek_seconds)
        status = query.lang["seeked"]
        reply = query.lang["play_seeked"].format(seek_seconds, user)
        should_delete_msg = True

    elif action == "seekback":
        seek_seconds = int(args[3]) if len(args) > 3 else 10
        await che.seek(chat_id, -seek_seconds)
        status = query.lang["seeked_back"]
        reply = query.lang["play_seeked_back"].format(seek_seconds, user)
        should_delete_msg = True

    
    if not reply and not status:
        return

    try:
        if should_delete_msg:
            # Skip, Loop, Stop, Seek gibi işlemlerde yeni mesaj atılır, eskisi silinir
            await query.message.reply_text(reply, quote=False)
            if action not in ["seek", "seekback"]:
                try:
                    await query.message.delete()
                except:
                    pass
        else:
            # Pause, Resume gibi işlemlerde mevcut mesaj güncellenir
            if query.message.caption:
                original_html = query.message.caption.html
                is_media = True
            else:
                original_html = query.message.text.html
                is_media = False

            clean_text = re.sub(r"\n\n<blockquote>.*?</blockquote>", "", original_html, flags=re.DOTALL)
            
            markup = buttons.controls(chat_id, status=status if action != "resume" else None)
            
            final_text = f"{clean_text}\n\n<blockquote>{reply}</blockquote>"

            if is_media:
                await query.edit_message_caption(caption=final_text, reply_markup=markup)
            else:
                await query.edit_message_text(text=final_text, reply_markup=markup)

    except Exception as e:
        print(f"Controls Error: {e}")
        try:
             await query.answer("İşlem gerçekleştirildi.", show_alert=False)
        except:
            pass

@app.on_callback_query(filters.regex("help") & ~app.bl_users)
@lang.language()
async def _help(_, query: types.CallbackQuery):
    data = query.data.split()
    if len(data) == 1:
        return await query.answer(url=f"https://t.me/{app.username}?start=help")

    if data[1] == "back":
        return await query.edit_message_text(
            text=query.lang["help_menu"], reply_markup=buttons.help_markup(query.lang)
        )
    elif data[1] == "close":
        try:
            await query.message.delete()
            return await query.message.reply_to_message.delete()
        except:
            pass

    await query.edit_message_text(
        text=query.lang[f"help_{data[1]}"],
        reply_markup=buttons.help_markup(query.lang, True),
    )

@app.on_callback_query(filters.regex("settings") & ~app.bl_users)
@lang.language()
@admin_check
async def _settings_cb(_, query: types.CallbackQuery):
    cmd = query.data.split()
    if len(cmd) == 1:
        return await query.answer()
    await query.answer(query.lang["processing"], show_alert=True)

    chat_id = query.message.chat.id
    _admin = await db.get_play_mode(chat_id)
    _delete = await db.get_cmd_delete(chat_id)
    _language = await db.get_lang(chat_id)

    if cmd[1] == "delete":
        _delete = not _delete
        await db.set_cmd_delete(chat_id, _delete)
    elif cmd[1] == "play":
        await db.set_play_mode(chat_id, not _admin)
        _admin = not _admin
        
    await query.edit_message_reply_markup(
        reply_markup=buttons.settings_markup(
            query.lang,
            _admin,
            _delete,
            _language,
            chat_id,
        )
    )
