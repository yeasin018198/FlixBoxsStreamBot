import os
import sys
import shutil
import psutil
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from database.users_db import db
from info import ADMINS
from Script import script

# -----------------------------------------------------------
#  BOT STATISTICS COMMAND
# -----------------------------------------------------------
@Client.on_message(filters.command("stats") & filters.private & filters.user(ADMINS))
async def bot_stats(client: Client, message: Message):
    status_msg = await message.reply_text("🔄 **Fetching Stats...**", quote=True)
    try:
        total_users = await db.total_users_count()
        blocked_users = await db.total_blocked_count()
        blocked_channels = await db.total_blocked_channels_count()
        try:
            premium_users = await db.all_premium_users_count()
        except AttributeError:
            premium_users = "N/A"
        try:
            level1, level2 = await db.get_verification_stats()
        except Exception:
            level1, level2 = 0, 0
        total_files = await db.files.count_documents({})
        total_links = await db.protected_links.count_documents({})
        total, used, free = shutil.disk_usage(".")
        total = get_size(total)
        used = get_size(used)
        free = get_size(free)
        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory().percent
        await status_msg.edit(script.BOT_STATS_TEXT.format(total_users=total_users, premium_users=premium_users, blocked_users=blocked_users, level1=level1, level2=level2, total_files=total_files, total_links=total_links, blocked_channels=blocked_channels, cpu_usage=cpu_usage, ram_usage=ram_usage, total=total, used=used, free=free), disable_web_page_preview=True)
    except Exception as e:
        await status_msg.edit(f"❌ **Error Fetching Stats:**\n`{e}`")

@Client.on_message(filters.command("restart") & filters.private & filters.user(ADMINS))
async def restart_bot(client: Client, message: Message):
    try:
        msg = await message.reply_text("<i>♻️ Restarting the bot, please wait...</i>")
        await asyncio.sleep(2)
        await msg.edit("<i>✅ System Restart Initiated...\nI will be back in few seconds!</i>")
        os.execl(sys.executable, sys.executable, *sys.argv)
    except Exception as e:
        print(f"Restart Error: {e}")
        await message.reply_text(f"❌ Error while restarting: `{e}`")
        
# --- Helper Function for Size Conversion ---
def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor
        
