import os
from pyrogram import Client, filters
from pyrogram.types import Message
import secrets
from database.users_db import db
# ADMINS ko import karna zaruri hai
from info import URL, LOG_CHANNEL, ADMINS 

# -----------------------------------------------------------
# 1. PASSWORD COMMAND (Sabke liye open hai)
# -----------------------------------------------------------
@Client.on_message(filters.command("password") & filters.private)
async def generate_password_link(client: Client, message: Message):
    # ... (Iska code same rahega jo upar diya tha) ...
    try:
        text = message.text.split(None, 2)
        if len(text) < 3:
            return await message.reply("❌ Format: `/password [pass] [link]`")
        
        password = text[1]
        if len(password) != 6:
            return await message.reply("⚠️ Password must be 6 characters.")

        raw_data = text[2]
        parts = raw_data.split("|")
        original_url = parts[0].strip()
        title = parts[1].strip() if len(parts) > 1 else "Secured Content"
        channel_link = parts[2].strip() if len(parts) > 2 else None
        
        existing_data = await db.get_link_by_url(original_url)
        base_url = URL if URL.endswith("/") else f"{URL}/"

        if existing_data:
            token = existing_data['token']
            await db.update_protected_link(token, password, title, channel_link)
            action = "Updated"
        else:
            token = secrets.token_urlsafe(8)
            await db.add_protected_link(token, original_url, password, title, channel_link)
            action = "Created"

        protected_url = f"{base_url}p/{token}"

        msg = (
            f"🔒 𝘗𝘢𝘴𝘴𝘸𝘰𝘳𝘥 𝘓𝘪𝘯𝘬 {action}!\n\n"
            f"𝘗𝘢𝘴𝘴𝘸𝘰𝘳𝘥: `{password}`\n"
            f"𝘛𝘪𝘵𝘭𝘦: {title}\n"
            f"𝘓𝘪𝘯𝘬: {protected_url}\n"
        )
        if channel_link:
            msg += f"𝘎𝘦𝘵 𝘗𝘢𝘴𝘴: [𝘊𝘭𝘪𝘤𝘬 𝘏𝘦𝘳𝘦]({channel_link})\n"

        await message.reply(msg, disable_web_page_preview=True)

        if LOG_CHANNEL:
            log_msg = (
                f"**#NEW_LINK_GENERATED**\n\n"
                f"👤 **User:** {message.from_user.mention} (`{message.from_user.id}`)\n"
                f"🎬 **Title:** {title}\n"
                f"🔑 **Password:** `{password}`\n"
                f"🔗 **Short Link:** {protected_url}\n"
                f"⚡ **Action:** {action}"
            )
            await client.send_message(LOG_CHANNEL, log_msg, disable_web_page_preview=True)

    except Exception as e:
        print(f"Error: {e}")
        await message.reply("Error processing request.")

@Client.on_message(filters.command("delete_pass") & filters.private & filters.user(ADMINS))
async def delete_password_link(client: Client, message: Message):
    try:
        args = message.text.split()
        if len(args) < 2:
            return await message.reply("❌ **Format:** `/delete_pass [Link ya Token]`")

        input_data = args[1]
        
        # Logic: Agar user ne poora link diya hai to Token nikalo
        if "/p/" in input_data:
            # Example: https://site.com/p/TOKEN -> TOKEN
            token = input_data.split("/p/")[-1].split("?")[0] # '?' hata kar clean token
        else:
            # Agar user ne direct token diya hai
            token = input_data.strip()

        # Database se delete karein
        is_deleted = await db.delete_protected_link(token)

        if is_deleted:
            await message.reply(f"✅ **Success!**\n\nLink Token `{token}` ko database se **Delete** kar diya gaya hai.\nAb yeh link kaam nahi karega.")
            
            # (Optional) Log Channel me update
            if LOG_CHANNEL:
                await client.send_message(
                    LOG_CHANNEL,
                    f"🗑 **#LINK_DELETED**\n\n"
                    f"👮‍♂️ **Admin:** {message.from_user.mention}\n"
                    f"🎟 **Token:** `{token}`"
                )
        else:
            await message.reply("❌ **Error:** Yeh Link/Token database mein nahi mila.")

    except Exception as e:
        print(f"Delete Error: {e}")
        await message.reply("Error deleting link.")
        
# -----------------------------------------------------------
# 2. CHECK PASS COMMAND (Sirf ADMINS ke liye)
# -----------------------------------------------------------
@Client.on_message(filters.command("check_pass") & filters.private & filters.user(ADMINS))
async def check_all_passwords(client: Client, message: Message):
    
    status_msg = await message.reply("🔄 **Fetching all links from database...**")
    
    try:
        all_links = await db.get_all_protected_links()
        
        file_path = "all_passwords.txt"
        count = 0
        
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(f"--- ALL PROTECTED LINKS REPORT ---\n\n")
            
            async for link in all_links:
                count += 1
                base_url = URL if URL.endswith("/") else f"{URL}/"
                short_link = f"{base_url}p/{link['token']}"
                
                line = (
                    f"[{count}] Title: {link.get('title', 'No Title')}\n"
                    f"    Password: {link.get('password')}\n"
                    f"    Short Link: {short_link}\n"
                    f"    Original Link: {link.get('url')}\n"
                    f"----------------------------------------\n"
                )
                file.write(line)
        
        if count == 0:
            await status_msg.edit("❌ Database is empty. No links found.")
            if os.path.exists(file_path):
                os.remove(file_path)
            return

        await message.reply_document(
            document=file_path,
            caption=f"✅ **Total Links Found:** `{count}`\n\nYe rahi saare passwords aur links ki list.",
            file_name="All_Protected_Links.txt"
        )
        
        await status_msg.delete()
        if os.path.exists(file_path):
            os.remove(file_path)

    except Exception as e:
        await status_msg.edit(f"❌ Error: {e}")
        print(f"Check Pass Error: {e}")
        
