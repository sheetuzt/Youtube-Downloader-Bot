from __future__ import unicode_literals

import asyncio

from pyrogram import Client, Filters, StopPropagation, InlineKeyboardButton, InlineKeyboardMarkup
import yt_dlp as youtube_dl

from utils.util import humanbytes


def buttonmap(item):
    quality = item['format']
    if "audio" in quality:
        return [InlineKeyboardButton(
            f"{quality} 🎵 {humanbytes(item.get('filesize'))}",
            callback_data=f"ytdata||audio||{item['format_id']}||{item['yturl']}"
        )]
    return [InlineKeyboardButton(
        f"{quality} 📹 {humanbytes(item.get('filesize'))}",
        callback_data=f"ytdata||video||{item['format_id']}||{item['yturl']}"
    )]


# Return an array of buttons.
def create_buttons(quality_list):
    return map(buttonmap, quality_list)


# Extract YouTube information.
def extractYt(yturl):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        quality_list = []
        result = ydl.extract_info(yturl, download=False)
        for media_format in result.get('formats', []):
            # Filter DASH video-only formats; this bot downloads one format at a time.
            if "dash" not in str(media_format.get('format', '')).lower():
                quality_list.append({
                    "format": media_format.get('format', 'unknown'),
                    "filesize": media_format.get('filesize'),
                    "format_id": media_format['format_id'],
                    "yturl": yturl,
                })

        return result['title'], result.get('thumbnail'), quality_list


async def downloadvideocli(command_to_exec):
    process = await asyncio.create_subprocess_exec(
        *command_to_exec,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    print(e_response)
    # yt-dlp prints the final path because the command includes
    # --print after_move:filepath. Keep the last non-empty line as the path.
    return next(line for line in reversed(t_response.splitlines()) if line.strip()).strip()


async def downloadaudiocli(command_to_exec):
    process = await asyncio.create_subprocess_exec(
        *command_to_exec,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    print("Download error:", e_response)

    return next(line for line in reversed(t_response.splitlines()) if line.strip()).strip()
