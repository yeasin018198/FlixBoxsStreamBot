import re
import os
import time
import asyncio
import threading
import urllib.request
from datetime import datetime
from os import environ, getenv
from Script import script

# --- Helper Functions ---
def is_enabled(value, default):
    if value.lower() in ["true", "yes", "1", "on"]:
        return True
    elif value.lower() in ["false", "no", "0", "off"]:
        return False
    return default

# =========================================================
# 🤖 BOT INFO & CREDENTIALS
# =========================================================
SESSION = environ.get('SESSION', 'Webavbot')
API_ID = int(environ.get('API_ID', '29904834'))
API_HASH = environ.get('API_HASH', '8b4fd9ef578af114502feeafa2d31938')
BOT_TOKEN = environ.get('BOT_TOKEN', '8714836567:AAEUM36b-_Nri1HFjmAa0Yv1r_A_TPxI0eU')

# Admin Settings
ADMINS = [int(x) for x in environ.get('ADMINS', '7120801813').split()]
OWNER_USERNAME = environ.get("OWNER_USERNAME", 'ya_movies')

# =========================================================
# 🗄️ DATABASE CONNECTION
# =========================================================
DB_URL = environ.get('DATABASE_URI', "mongodb+srv://Testbot:Testbot@cluster0.5iukc4c.mongodb.net/?appName=Cluster0")
DB_NAME = environ.get('DATABASE_NAME', "testing")

# =========================================================
# 📢 CHANNELS & LOGS
# =========================================================
# Mandatory Channels
BIN_CHANNEL = int(environ.get("BIN_CHANNEL", '-1004498638459'))
LOG_CHANNEL = int(environ.get("LOG_CHANNEL", '-1004498638459'))

# Feature Specific Logs
PREMIUM_LOGS = int(environ.get("PREMIUM_LOGS", '-1004498638459'))
VERIFIED_LOG = int(environ.get('VERIFIED_LOG', '-1004498638459'))
SUPPORT_GROUP = int(environ.get("SUPPORT_GROUP", "-1004498638459"))

# Auth Channels (Safe Parsing)
auth_channel_str = environ.get("AUTH_CHANNEL", "-1004498638459")
AUTH_CHANNEL = [int(x) for x in auth_channel_str.split()] if auth_channel_str else []

# =========================================================
# 🔗 LINKS & URLS
# =========================================================
CHANNEL = environ.get('CHANNEL', 'https://t.me/AV_BOTz_UPDATE')
SUPPORT = environ.get('SUPPORT', 'https://t.me/AV_SUPPORT_GROUP')
TUTORIAL_LINK_1 = environ.get('TUTORIAL_LINK_1', 'https://t.me/1')
TUTORIAL_LINK_2 = environ.get('TUTORIAL_LINK_2', 'https://t.me/2')

# =========================================================
# 🔐 VERIFICATION & SHORTENER
# =========================================================
IS_VERIFY = is_enabled(environ.get("IS_VERIFY", "False"), True)
IS_SECOND_VERIFY = is_enabled(environ.get("IS_SECOND_VERIFY", "True"), True)
IS_SHORTLINK = is_enabled(environ.get('IS_SHORTLINK', "True"), True)

# Verification Config
VERIFY_EXPIRE = int(environ.get('VERIFY_EXPIRE', 60)) # In Minutes/Hours based on logic
SHORTLINK_URL = environ.get('SHORTLINK_URL', 'mdiskshortner.link')
SHORTLINK_API = environ.get('SHORTLINK_API', '96a3c0e8ae1b1abd429906762e38a40d3f2ec56c')

# Second Verification Config
SHORTLINK_WEBSITE2 = environ.get("SHORTENER_WEBSITE2", "mdiskshortner.link")
SHORTLINK_API2 = environ.get("SHORTENER_API2", "96a3c0e8ae1b1abd429906762e38a40d3f2ec56c")

# =========================================================
# ⚙️ SETTINGS & LIMITS
# =========================================================
FSUB = is_enabled(environ.get("FSUB", "True"), True)
ENABLE_LIMIT = is_enabled(environ.get("ENABLE_LIMIT", "True"), True)
MAINTENANCE_MODE = is_enabled(environ.get("MAINTENANCE_MODE", "False"), False)

# Time & Rate Limits
TIMEZONE = environ.get("TIMEZONE", "Asia/Kolkata")
PING_INTERVAL = int(environ.get("PING_INTERVAL", "1200"))
SLEEP_THRESHOLD = int(getenv('SLEEP_THRESHOLD', '60'))
RATE_LIMIT_TIMEOUT = int(environ.get("RATE_LIMIT_TIMEOUT", "600"))

# File Limits
MAX_FILES = int(environ.get("MAX_FILES", "50"))
BATCH_LIMIT = int(environ.get('BATCH_LIMIT', 60))

# 🗑️ AUTO DELETE SETTINGS
AUTO_DELETE = is_enabled(environ.get("AUTO_DELETE", "True"), True)
AUTO_DELETE_TIME = int(environ.get("AUTO_DELETE_TIME", "60")) # ১০ মিনিটের জন্য ৬০০ সেকেন্ড দিন

# 🔄 KEEP ALIVE / UPTIME SETTINGS
AUTO_KEEP_ALIVE = is_enabled(environ.get("AUTO_KEEP_ALIVE", "True"), True)

# =========================================================
# 🖼️ MEDIA & CAPTIONS
# =========================================================
QR_CODE = environ.get('QR_CODE', 'https://graph.org/file/6afb4093d5ec5c4176979.jpg')
VERIFY_IMG = environ.get("VERIFY_IMG", "https://graph.org/file/1669ab9af68eaa62c3ca4.jpg")
AUTH_PICS = environ.get('AUTH_PICS', 'https://envs.sh/AwV.jpg')
PICS = environ.get('PICS', 'https://ibb.co/VpTJNNCN')
FILE_PIC = environ.get('FILE_PIC', 'https://i.ibb.co/bj4My0bW/photo-2025-07-21-02-15-21-7529360175656861700.jpg')

FILE_CAPTION = environ.get('FILE_CAPTION', script.CAPTION)

# =========================================================
# 🌐 SERVER & APP CONFIG
# =========================================================
WORKERS = int(getenv('WORKERS', '50004'))
MULTI_CLIENT = False
name = str(environ.get('name', 'avbotz'))

# Heroku & Port Config
if 'DYNO' in environ:
    ON_HEROKU = True
    APP_NAME = str(getenv('APP_NAME'))
else:
    ON_HEROKU = False
    APP_NAME = None

PORT = int(getenv('PORT', '2626'))
NO_PORT = is_enabled(getenv("NO_PORT", "True"), False)
HAS_SSL = is_enabled(getenv("HAS_SSL", "False"), False)
BIND_ADDRESS = getenv("WEB_SERVER_BIND_ADDRESS", "127.0.0.1")

# URL Generation
custom_url = environ.get("URL")
if custom_url:
    URL = custom_url
else:
    FQDN = getenv("FQDN", BIND_ADDRESS)
    PROTOCOL = "http" if HAS_SSL else "https"
    PORT_SEGMENT = "" if NO_PORT else f":{PORT}"
    URL = f"{PROTOCOL}://{FQDN}{PORT_SEGMENT}/"

# Default fallback if nothing works
if not URL or URL == "/" or URL.startswith("https://127.0.0.1"):
    URL = "https://forward-jolyn-vnnmbs-62200c9e.koyeb.app/"

# =========================================================
# 🚀 AUTO UPTIME / KEEP-ALIVE LOGIC
# =========================================================
def ping_server():
    while True:
        try:
            urllib.request.urlopen(URL)
            print(f"Ping successful to: {URL}")
        except Exception as e:
            print(f"Ping failed: {e}")
        time.sleep(PING_INTERVAL)

if AUTO_KEEP_ALIVE:
    threading.Thread(target=ping_server, daemon=True).start()

# =========================================================
# 🗑️ UNIVERSAL AUTO-DELETE ENGINE (FOR ALL MEDIA TYPES)
# =========================================================
async def auto_delete_message(message, delay=None):
    """
    এটি ভিডিও, অডিও, ফটো, এপিকে, টেক্সট বা লিঙ্ক—যেকোনো মেসেজ
    নির্ধারিত সময় পর অটো ডিলিট করবে।
    """
    if not AUTO_DELETE:
        return
    
    # সময় নির্ধারণ (যদি আলাদা সময় না থাকে তবে ডিফল্ট নেবে)
    wait_time = delay if delay is not None else AUTO_DELETE_TIME
    
    await asyncio.sleep(wait_time)
    
    try:
        # মেইন মেসেজ ডিলিট করবে
        await message.delete()
        
        # যদি ওই মেসেজের সাথে কোনো ফাইল রিপ্লাই হিসেবে থাকে সেটিও ডিলিট করবে
        if hasattr(message, 'reply_to_message') and message.reply_to_message:
            try:
                await message.reply_to_message.delete()
            except:
                pass
    except Exception:
        # মেসেজ ডিলিট করতে না পারলে (যদি অলরেডি ডিলিট থাকে) স্কিপ করবে
        pass
