from __future__ import unicode_literals

import asyncio
import os

from pyrogram.types import InlineKeyboardButton
import yt_dlp as youtube_dl

from utils.util import humanbytes


def _downloaded_path(stdout, stderr):
    lines = [line.strip() for line in stdout.splitlines() if line.strip()]
    if not lines:
        raise RuntimeError(f"yt-dlp did not return a file path: {stderr.strip()}")
    return lines[-1]


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
    player_clients = [
        client.strip()
        for client in os.getenv(
            "YTDLP_PLAYER_CLIENTS", "android_vr,ios,web_safari"
        ).split(",")
        if client.strip()
    ]
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        # yt-dlp now uses Deno/EJS to solve YouTube's JavaScript challenges.
        'js_runtimes': {'deno': {}},
        'extractor_args': {
            'youtube': {'player_client': player_clients},
        },
    }
    youtube_proxy = os.getenv("YOUTUBE_PROXY")
    if youtube_proxy:
        ydl_opts['proxy'] = youtube_proxy
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
    # --print after_move:filepath.
    if process.returncode != 0:
        raise RuntimeError(f"Video download failed: {e_response}")
    return _downloaded_path(t_response, e_response)


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

    if process.returncode != 0:
        raise RuntimeError(f"Audio download failed: {e_response}")
    return _downloaded_path(t_response, e_response)
