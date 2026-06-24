import os
from pyrogram import Client, filters
from pyrogram.types import Message
from database.users_db import db  # DB import verify kar lena
from info import ADMINS

# -----------------------------------------------------------
# 1. DELETE USER FILES COMMAND (Fixed & Safe)
# -----------------------------------------------------------
@Client.on_message(filters.command("delfile") & filters.user(ADMINS))
async def delete_user_files(client: Client, message: Message):
    # Example: /delfile 123456789
    if len(message.command) < 2:
        return await message.reply_text("⚠️ **Usage:** `/delfile [User_ID]`", quote=True)

    try:
        target_id = int(message.command[1])
    except ValueError:
        return await message.reply_text("❌ **Error:** User ID number hona chahiye!", quote=True)

    # Pehle check karein files hain ya nahi
    count = await db.files.count_documents({"user_id": target_id})
    
    if count == 0:
        return await message.reply_text(f"❌ User ID `{target_id}` ki database mein koi files nahi mili.", quote=True)

    # Process start message
    status_msg = await message.reply_text(f"⏳ Deleting **{count}** files...", quote=True)

    # Delete Action
    await db.files.delete_many({"user_id": target_id})
    
    await status_msg.edit(f"✅ **Success!**\n\nUser ID `{target_id}` ki **{count} files** delete kar di gayi hain.")


# -----------------------------------------------------------
# 2. FILE STATS COMMAND (Generates TXT File)
# -----------------------------------------------------------
@Client.on_message(filters.command("file_stats") & filters.user(ADMINS))
async def user_file_stats_txt(client: Client, message: Message):
    
    status_msg = await message.reply_text("🔄 **Generating Statistics File... Wait.**", quote=True)

    try:
        # Database query
        pipeline = [
            {"$group": {"_id": "$user_id", "total_files": {"$sum": 1}}},
            {"$sort": {"total_files": -1}}
        ]
        # Length=None ka matlab saara data lao
        results = await db.files.aggregate(pipeline).to_list(length=None)

        if not results:
            return await status_msg.edit("❌ Database is empty. No files found.")

        file_path = "User_File_Stats.txt"
        
        # File Writing
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(f"=========================================\n")
            file.write(f"         USER FILE STATISTICS           \n")
            file.write(f"     Total Uploaders: {len(results)}\n")
            file.write(f"=========================================\n\n")
            file.write(f"{'Rank':<5} | {'User ID':<15} | {'Files Count'}\n")
            file.write(f"-----------------------------------------\n")

            for i, user in enumerate(results, start=1):
                user_id = user["_id"]
                total = user["total_files"]
                
                # Note: 'get_users' hata diya kyunki agar 1000+ users hue 
                # to bot hang ho jayega naam dhundne mein.
                # Sirf ID aur Count fast hota hai.
                
                file.write(f"{i:<5} | {str(user_id):<15} | {total}\n")

        # Send File
        await message.reply_document(
            document=file_path,
            caption=f"📊 **File Stats Generated!**\n\nTotal Users with files: `{len(results)}`",
            file_name="User_File_Stats.txt"
        )

        # Cleanup
        await status_msg.delete()
        if os.path.exists(file_path):
            os.remove(file_path)

    except Exception as e:
        await status_msg.edit(f"❌ Error: {e}")
        if os.path.exists("User_File_Stats.txt"):
            os.remove("User_File_Stats.txt")

