import asyncio
import logging
import random
import string
import pytz
from datetime import datetime
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import enums
from info import (
    VERIFIED_LOG, TIMEZONE, VERIFY_IMG, VERIFY_EXPIRE,
    TUTORIAL_LINK_1, TUTORIAL_LINK_2,
    IS_VERIFY, IS_SECOND_VERIFY
)
from database.users_db import db
from utils import temp, get_shortlink_av, auto_delete_message, get_readable_time
from Script import script

logger = logging.getLogger(__name__)

# --- FOOTER LOGIC ---
VERIFY_FOOTER = "1/2" if IS_SECOND_VERIFY else "1/1"

# --- MAIN VERIFICATION CHECKER ---
async def av_x_verification(client, message):
    user_id = message.from_user.id
    if IS_VERIFY:
        user_verified = await db.is_user_verified(user_id)
    else:
        user_verified = True 
    if IS_SECOND_VERIFY and user_verified:
        is_second_shortener = await db.use_second_shortener(user_id)
    else:
        is_second_shortener = False 
    if user_verified and not is_second_shortener:
        return True
    how_to_download_link = TUTORIAL_LINK_2 if is_second_shortener else TUTORIAL_LINK_1
    file_id = None
    if len(message.command) > 1:
        file_id = message.command[1]
    verify_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))
    await db.create_verify_id(user_id, verify_id, file_id)
    verify_url = await get_shortlink_av(
        f"https://telegram.me/{temp.U_NAME}?start=avbotz_{user_id}_{verify_id}", 
        is_second_shortener
    )
    buttons = [[
        InlineKeyboardButton(text="⚠️ ᴠᴇʀɪғʏ ⚠️", url=verify_url), 
        InlineKeyboardButton(text="❗ ʜᴏᴡ ᴛᴏ ᴠᴇʀɪғʏ ❗", url=how_to_download_link)
    ]]
    user_name = message.from_user.first_name
    if is_second_shortener:
        try:
            bin_text = script.SECOND_VERIFICATION_TEXT.format(user_name, "2/2")
        except:
            bin_text = script.SECOND_VERIFICATION_TEXT.format(user_name)
    else:
        verify_time = "1/2" if IS_SECOND_VERIFY else "1/1"
        try:
            bin_text = script.VERIFICATION_TEXT.format(user_name, verify_time, VERIFY_FOOTER)
        except:
            bin_text = script.VERIFICATION_TEXT.format(user_name, verify_time)
    dlt = await message.reply_text(
        text=bin_text,
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    )
    asyncio.create_task(auto_delete_message(message, dlt))
    return False

# --- VERIFICATION SUCCESS HANDLER (Run on /start) ---
async def verify_user_on_start(client, message):
    try:
        data = message.command[1].split("_")       
        if len(data) < 3:
            return False           
        user_id = int(data[1])
        verify_id = data[2]
        if message.from_user.id != user_id:
            await message.reply("<b>This link is not for you!</b>")
            return True
        verify_id_info = await db.get_verify_id_info(user_id, verify_id)
        if not verify_id_info or verify_id_info["verified"]:
            await message.reply("<b>Lɪɴᴋ Exᴘɪʀᴇᴅ ᴏʀ Aʟʀᴇᴀᴅʏ Usᴇᴅ... Tʀʏ Aɢᴀɪɴ.</b>")
            return True
        is_first_done = await db.is_user_verified(user_id)
        if IS_VERIFY and not is_first_done:
            key = "last_verified"
        else:
            key = "second_time_verified"
        ist_timezone = pytz.timezone(TIMEZONE)     
        current_time = datetime.now(tz=ist_timezone)
        await db.update_notcopy_user(user_id, {key: current_time})
        await db.update_verify_id_info(user_id, verify_id, {"verified": True})
        stored_file_id = verify_id_info.get("file_id")
        if stored_file_id:
            file_link = f"https://t.me/{temp.U_NAME}?start={stored_file_id}"
        else:
            file_link = f"https://t.me/{temp.U_NAME}?start=help"
        btn = InlineKeyboardMarkup([[
            InlineKeyboardButton("📂 ɢᴇᴛ ʀᴇǫᴜᴇsᴛᴇᴅ ғɪʟᴇ 📂", url=file_link)
        ]])
        txt = script.SECOND_VERIFY_COMPLETE_TEXT if key == "second_time_verified" else script.VERIFY_COMPLETE_TEXT
        vrfy_num = 2 if key == "second_time_verified" else 1
        if VERIFIED_LOG:
            try:
                await client.send_message(
                    VERIFIED_LOG, 
                    script.VERIFIED_TXT.format(
                        message.from_user.mention, 
                        user_id, 
                        datetime.now(ist_timezone).strftime('%d_%B_%Y'), 
                        vrfy_num
                    )
                )
            except Exception as e:
                logger.warning(f"Failed to send log: {e}")
        await message.reply_photo(
            photo=VERIFY_IMG, 
            caption=txt.format(message.from_user.mention), 
            reply_markup=btn, 
            parse_mode=enums.ParseMode.HTML
        )
        return True
        
    except Exception as e:
        logger.error(f"Verify Error: {e}")
        return False
            
