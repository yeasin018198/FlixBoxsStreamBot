import jinja2
from info import *
from utils import temp
from web.bot import WebavBot
from utils import humanbytes
from web.utils.file_properties import get_file_ids
from web.server.exceptions import InvalidHash
import urllib.parse
import aiofiles
import logging
import aiohttp
import jinja2

async def render_page(id, secure_hash, src=None):
    file = await WebavBot.get_messages(int(BIN_CHANNEL), int(id))
    file_data = await get_file_ids(WebavBot, int(BIN_CHANNEL), int(id))
    
    if file_data.unique_id[:6] != secure_hash:
        logging.debug(f"link hash: {secure_hash} - {file_data.unique_id[:6]}")
        logging.debug(f"Invalid hash for message with - ID {id}")
        raise InvalidHash

    # --- FIX START ---
    # 1. Ensure file_name is a string for internal use
    raw_file_name = file_data.file_name if file_data.file_name else f"File_{id}"
    
    # 2. For the display name (cleaner look)
    file_name = raw_file_name.replace("_", " ").replace(".", " ")
    
    # 3. Use str() inside quote_plus to prevent the 'None' type error
    safe_quoted_name = urllib.parse.quote_plus(str(raw_file_name))
    
    src = urllib.parse.urljoin(
        URL,
        f"{id}/{safe_quoted_name}?hash={secure_hash}",
    )
    # --- FIX END ---

    tag = file_data.mime_type.split("/")[0].strip()
    file_size = humanbytes(file_data.file_size)
    
    if tag in ["video", "audio"]:
        template_file = "web/template/webav.html"
    else:
        template_file = "web/template/dl.html"
        # Note: It's better to use file_data.file_size instead of 
        # making a secondary request to your own server to get the Content-Length.
        # But keeping your logic:
        async with aiohttp.ClientSession() as s:
            async with s.get(src) as u:
                content_len = u.headers.get("Content-Length")
                if content_len:
                    file_size = humanbytes(int(content_len))

    async with aiofiles.open(template_file, mode='r') as f:
        template_content = await f.read()
        template = jinja2.Template(template_content)

    file_get_link = f"https://t.me/{temp.U_NAME}?start=file_{id}"
    
    return template.render(
        file_name=file_name,
        file_url=src,
        file_size=file_size,
        file_get=file_get_link,
        file_unique_id=file_data.unique_id,
    )
    

