from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardRemove
)
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid

import time
import asyncio
import logging

from database.users_db import db
from info import ADMINS

lock = asyncio.Lock()

class temp(object):
    USERS_CANCEL = False

def get_readable_time(seconds):
    periods = [('days', 86400), ('hour', 3600), ('min', 60), ('sec', 1)]
    result = ''
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            result += f'{int(period_value)}{period_name}'
    return result

async def users_broadcast(user_id, message, is_pin):
    try:
        m = await message.copy(chat_id=user_id)
        if is_pin:
            await m.pin(both_sides=True)
        return True, "Success"
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await users_broadcast(user_id, message, is_pin)
    except InputUserDeactivated:
        await db.delete_user(int(user_id))
        logging.info(f"{user_id} - Removed from Database, since deleted account.")
        return False, "Deleted"
    except UserIsBlocked:
        logging.info(f"{user_id} - Blocked the bot.")
        await db.delete_user(user_id)
        return False, "Blocked"
    except PeerIdInvalid:
        await db.delete_user(int(user_id))
        logging.info(f"{user_id} - PeerIdInvalid")
        return False, "Error"
    except Exception as e:
        logging.error(f"Error broadcasting to {user_id}: {e}")
        return False, "Error"

@Client.on_callback_query(filters.regex(r'^broadcast_cancel'))
async def broadcast_cancel(bot, query):
    _, ident = query.data.split("#")
    if ident == 'users':
        await query.message.edit("Trying to cancel users broadcasting...")
        temp.USERS_CANCEL = True

async def process_broadcast(bot, message, is_pin: bool):
    if lock.locked():
        return await message.reply('Currently broadcast processing, Wait for complete.')

    # চেক করা হচ্ছে কোনো মেসেজে রিপ্লাই দেওয়া হয়েছে কিনা
    if not message.reply_to_message:
        return await message.reply_text("<b>Error:</b> Please reply to a message (text, photo, video, etc.) to start broadcast!")

    await bot.send_message(chat_id=message.chat.id, text="Broadcast started...", reply_markup=ReplyKeyboardRemove())

    users = await db.get_all_users()
    b_msg = message.reply_to_message
    b_sts = await message.reply_text(text='<b>Broadcasting your messages to users ⌛️</b>')

    start_time = time.time()
    total_users = await db.total_users_count()
    done = 0
    success = 0
    failed = 0

    async with lock:
        async for user in users:
            if temp.USERS_CANCEL:
                temp.USERS_CANCEL = False
                time_taken = get_readable_time(time.time() - start_time)
                await b_sts.edit(
                    f"❌ Users broadcast cancelled!\nCompleted in {time_taken}\n\n"
                    f"Total Users: <code>{total_users}</code>\n"
                    f"Completed: <code>{done}</code>\n"
                    f"Success: <code>{success}</code>"
                )
                return

            success_flag, sts = await users_broadcast(int(user['id']), b_msg, is_pin)
            if sts == 'Success':
                success += 1
            elif sts == 'Error':
                failed += 1
            done += 1

            if done % 20 == 0:
                btn = [[InlineKeyboardButton('CANCEL', callback_data='broadcast_cancel#users')]]
                try:
                    await b_sts.edit(
                        f"📢 Users broadcast in progress...\n\n"
                        f"Total Users: <code>{total_users}</code>\n"
                        f"Completed: <code>{done}</code>\n"
                        f"Success: <code>{success}</code>",
                        reply_markup=InlineKeyboardMarkup(btn)
                    )
                except:
                    pass

        time_taken = get_readable_time(time.time() - start_time)
        await b_sts.edit(
            f"✅ Users broadcast completed!\nCompleted in {time_taken}\n\n"
            f"Total Users: <code>{total_users}</code>\n"
            f"Completed: <code>{done}</code>\n"
            f"Success: <code>{success}</code>\n"
            f"Failed: <code>{failed}</code>"
        )

# Command: /broadcast (fixed logic)
@Client.on_message(filters.command("broadcast") & filters.user(ADMINS))
async def broadcast_only(bot, message):
    # যদি এডমিন রিপ্লাই না দিয়ে কমান্ড দেয়, তবে তাকে তথ্য দেওয়া হবে
    if not message.reply_to_message:
        await message.reply_text("<b>Usage:</b> Reply to any message with /broadcast to send it to all users.")
        return
    await process_broadcast(bot, message, is_pin=False)

# Command: /pin_broadcast (fixed logic)
@Client.on_message(filters.command("pin_broadcast") & filters.user(ADMINS))
async def broadcast_with_pin(bot, message):
    # যদি এডমিন রিপ্লাই না দিয়ে কমান্ড দেয়, তবে তাকে তথ্য দেওয়া হবে
    if not message.reply_to_message:
        await message.reply_text("<b>Usage:</b> Reply to any message with /pin_broadcast to send and pin it for all users.")
        return
    await process_broadcast(bot, message, is_pin=True)

# অতিরিক্ত ফির্চার: নন-এডমিন কেউ ট্রাই করলে ওয়ার্নিং দিবে
@Client.on_message(filters.command(["broadcast", "pin_broadcast"]) & ~filters.user(ADMINS))
async def unauthorized_broadcast(bot, message):
    await message.reply_text("<b>Access Denied!</b>\nOnly authorized admins can use this command.")
