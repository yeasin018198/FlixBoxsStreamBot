import asyncio
import os
import random
from web.utils.file_properties import get_hash
from pyrogram import Client, filters, enums
from info import BIN_CHANNEL, URL, CHANNEL, IS_SHORTLINK, TUTORIAL_LINK_1
from utils import temp, get_size, get_shortlink
from Script import script
from database.users_db import db
from pyrogram.errors import FloodWait
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

@Client.on_message(filters.channel & (filters.document | filters.video) & ~filters.forwarded, group=-1)
async def channel_receive_handler(bot: Client, broadcast: Message):
    try:
        chat_id = broadcast.chat.id
        if str(chat_id).startswith("-100"):
            is_banned = await db.is_channel_blocked(chat_id)
            if is_banned:
                block_data = await db.get_channel_block_data(chat_id)
                try:
                    await bot.send_message(
                        chat_id,
                        f"🚫 **Tʜɪꜱ ᴄʜᴀɴɴᴇʟ ɪꜱ ʙᴀɴɴᴇᴅ ғʀᴏᴍ ᴜꜱɪɴɢ ᴛʜᴇ ʙᴏᴛ.**\n\n"
                        f"🔄 **Cᴏɴᴛᴀᴄᴛ ᴀᴅᴍɪɴ ɪғ ʏᴏᴜ ᴛʜɪɴᴋ ᴛʜɪꜱ ɪꜱ ᴀ ᴍɪꜱᴛᴀᴋᴇ.**\n\n@AV_OWNER_BOT"
                    )
                except:
                    pass  # mute errors
                await bot.leave_chat(chat_id)
                return
        file = broadcast.document or broadcast.video
        file_name = file.file_name if file else "Unknown File"
        msg = await broadcast.forward(chat_id=BIN_CHANNEL)
        raw_stream = f"{URL}watch/{msg.id}/avbotz.mkv?hash={get_hash(msg)}"
        raw_download = f"{URL}{msg.id}?hash={get_hash(msg)}"
        raw_file_link = f"https://t.me/{temp.U_NAME}?start=file_{msg.id}"
        if IS_SHORTLINK:
            stream = await get_shortlink(raw_stream)
            download = await get_shortlink(raw_download)
            file_link = await get_shortlink(raw_file_link)
        else:
            stream = raw_stream
            download = raw_download
            file_link = raw_file_link
        await msg.reply_text(
            text=f"**Channel Name:** `{broadcast.chat.title}`\n**CHANNEL ID:** `{broadcast.chat.id}`\n**Rᴇǫᴜᴇsᴛ ᴜʀʟ:** {stream}",
            quote=True
        )
        new_caption = CHANNEL_FILE_CAPTION.format(CHANNEL, file_name)
        buttons_list = [
            [InlineKeyboardButton("• ꜱᴛʀᴇᴀᴍ •", url=stream),
             InlineKeyboardButton("• ᴅᴏᴡɴʟᴏᴀᴅ •", url=download)],
            [InlineKeyboardButton('• ᴄʜᴇᴄᴋ ʜᴇʀᴇ ᴛᴏ ɢᴇᴛ ғɪʟᴇ •', url=file_link)]
        ]
        if IS_SHORTLINK:
            buttons_list.append([
                InlineKeyboardButton("• ʜᴏᴡ ᴛᴏ ᴏᴘᴇɴ •", url=TUTORIAL_LINK_1)
            ])
        buttons = InlineKeyboardMarkup(buttons_list)
        await bot.edit_message_caption(
            chat_id=broadcast.chat.id,
            message_id=broadcast.id,
            caption=new_caption,
            reply_markup=buttons,
            parse_mode=enums.ParseMode.HTML
        )

    except asyncio.exceptions.TimeoutError:
        print("Request Timed Out! Retrying...")
        await asyncio.sleep(5)
        await channel_receive_handler(bot, broadcast)

    except FloodWait as w:
        print(f"Sleeping for {w.value}s due to FloodWait")
        await asyncio.sleep(w.value)

    except Exception as e:
        await bot.send_message(chat_id=BIN_CHANNEL, text=f"❌ **Error:** `{e}`", disable_web_page_preview=True)
        print(f"❌ Can't edit channel message! Error: {e}")

@Client.on_message(filters.command("link") & filters.group & filters.reply)
async def group_link_handler(bot: Client, message: Message):
    try:
        reply = message.reply_to_message
        if not reply or not (reply.document or reply.video):
            return await message.reply_text("❌ **Is ᴄᴏᴍᴍᴀɴᴅ ᴋᴀ ᴜsᴇ ᴋɪsɪ Vɪᴅᴇᴏ ʏᴀ Fɪʟᴇ ᴘᴀʀ Rᴇᴘʟʏ ᴋᴀʀᴋᴇ ᴋᴀʀᴇɪɴ.**")
        status_msg = await message.reply_text("🔄 **Gᴇɴᴇʀᴀᴛɪɴɢ Lɪɴᴋ... Pʟᴇᴀsᴇ ᴡᴀɪᴛ.**")
        try:
            log_msg = await reply.forward(chat_id=BIN_CHANNEL)
        except Exception as e:
            return await status_msg.edit(f"❌ Error forwarding to Bin Channel: {e}")
        file = reply.document or reply.video
        file_name = file.file_name if hasattr(file, 'file_name') and file.file_name else "Unknown File"
        raw_stream = f"{URL}watch/{log_msg.id}/avbotz.mkv?hash={get_hash(log_msg)}"
        raw_download = f"{URL}{log_msg.id}?hash={get_hash(log_msg)}"
        raw_file_link = f"https://t.me/{temp.U_NAME}?start=file_{log_msg.id}"
        if IS_SHORTLINK:
            stream = await get_shortlink(raw_stream)
            download = await get_shortlink(raw_download)
            file_link = await get_shortlink(raw_file_link)
        else:
            stream = raw_stream
            download = raw_download
            file_link = raw_file_link
        await log_msg.reply_text(
            text=(
                f"👤 **Requested By:** {message.from_user.mention} (`{message.from_user.id}`)\n"
                f"👥 **Group Name:** {message.chat.title}\n"
                f"🆔 **Group ID:** `{message.chat.id}`\n"
                f"🔗 **Stream URL:** {stream}"
            ),
            quote=True,
            disable_web_page_preview=True
        )
        buttons_list = [
            [InlineKeyboardButton("• ꜱᴛʀᴇᴀᴍ •", url=stream),
             InlineKeyboardButton("• ᴅᴏᴡɴʟᴏᴀᴅ •", url=download)],
            [InlineKeyboardButton('• ᴄʜᴇᴄᴋ ʜᴇʀᴇ ᴛᴏ ɢᴇᴛ ғɪʟᴇ •', url=file_link)]
        ]
        
        if IS_SHORTLINK:
            buttons_list.append([
                InlineKeyboardButton("• ʜᴏᴡ ᴛᴏ ᴏᴘᴇɴ •", url=TUTORIAL_LINK_1)
            ])
        buttons = InlineKeyboardMarkup(buttons_list)
        await status_msg.edit_text(
            text=f"📂 **𝘍𝘪𝘭𝘦 𝘕𝘢𝘮𝘦:** {file_name}\n\n🔗 **𝘓𝘪𝘯𝘬𝘴 𝘎𝘦𝘯𝘦𝘳𝘢𝘵𝘦𝘥 𝘚𝘶𝘤𝘤𝘦𝘴𝘴𝘧𝘶𝘭𝘭𝘺!**",
            reply_markup=buttons,
            parse_mode=enums.ParseMode.HTML
        )

    except Exception as e:
        print(f"Group Link Error: {e}")
        await message.reply_text(f"❌ Error: `{e}`")
        
