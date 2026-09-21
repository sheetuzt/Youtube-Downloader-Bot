import asyncio
import os

from pyrogram import Client, ContinuePropagation
from pyrogram.enums import ChatAction
from pyrogram.types import (InlineKeyboardButton,
                            InlineKeyboardMarkup,
                            InputMediaDocument,
                            InputMediaVideo,
                            InputMediaAudio)

from helper.ffmfunc import duration
from helper.ytdlfunc import downloadvideocli, downloadaudiocli
from PIL import Image

@Client.on_callback_query()
async def catch_youtube_fmtid(c, m):
    cb_data = m.data
    if cb_data.startswith("ytdata||"):
        yturl = cb_data.split("||")[-1]
        format_id = cb_data.split("||")[-2]
        media_type = cb_data.split("||")[-3].strip()
        print(media_type)
        if media_type == 'audio':
            buttons = InlineKeyboardMarkup([[InlineKeyboardButton(
                "Audio", callback_data=f"{media_type}||{format_id}||{yturl}"), InlineKeyboardButton("Document",
                                                                                                    callback_data=f"docaudio||{format_id}||{yturl}")]])
        else:
            buttons = InlineKeyboardMarkup([[InlineKeyboardButton(
                "Video", callback_data=f"{media_type}||{format_id}||{yturl}"), InlineKeyboardButton("Document",
                                                                                                    callback_data=f"docvideo||{format_id}||{yturl}")]])

        await m.edit_message_reply_markup(buttons)

    else:
        raise ContinuePropagation


@Client.on_callback_query()
async def catch_youtube_dldata(c, q):
    cb_data = q.data.strip()
    #print(q.message.chat.id)
    # Callback Data Check
    yturl = cb_data.split("||")[-1]
    format_id = cb_data.split("||")[-2]
    thumb_image_path = os.path.join(
        os.getcwd(), "downloads", f"{q.message.chat.id}.jpg"
    )
    print(thumb_image_path)
    width = 0
    height = 0
    if os.path.exists(thumb_image_path):
        img = Image.open(thumb_image_path)
        width, height = img.size
        if cb_data.startswith(("audio", "docaudio", "docvideo")):
            img = img.resize((320, height))
        else:
            img = img.resize((90, height))
        img.save(thumb_image_path, "JPEG")
    if not cb_data.startswith(("video", "audio", "docaudio", "docvideo")):
        print("no data found")
        raise ContinuePropagation

    filext = "%(title)s.%(ext)s"
    userdir = os.path.join(os.getcwd(), "downloads", str(q.message.chat.id))

    if not os.path.isdir(userdir):
        os.makedirs(userdir)
    await q.edit_message_reply_markup(
        InlineKeyboardMarkup([[InlineKeyboardButton("Downloading...", callback_data="down")]]))
    filepath = os.path.join(userdir, filext)
    # await q.edit_message_reply_markup([[InlineKeyboardButton("Processing..")]])

    audio_command = [
        "yt-dlp",
        "-c",
        "--no-playlist",
        "--no-progress",
        "--no-warnings",
        "--extractor-args",
        f"youtube:player_client={os.getenv('YTDLP_PLAYER_CLIENTS', 'android_vr,ios,web_safari')}",
        "--print", "after_move:filepath",
        "--prefer-ffmpeg",
        "-f", format_id,
        "--extract-audio",
        "--audio-format", "mp3",
        "-o", filepath,
        yturl,

    ]

    video_command = [
        "yt-dlp",
        "-c",
        "--no-playlist",
        "--no-progress",
        "--no-warnings",
        "--extractor-args",
        f"youtube:player_client={os.getenv('YTDLP_PLAYER_CLIENTS', 'android_vr,ios,web_safari')}",
        "--print", "after_move:filepath",
        "--embed-subs",
        "-f", f"{format_id}+bestaudio/best",
        "--merge-output-format", "mp4",
        "-o", filepath,
        "--hls-prefer-ffmpeg", yturl]

    loop = asyncio.get_event_loop()

    med = None
    if cb_data.startswith("audio"):
        filename = await downloadaudiocli(audio_command)
        med = InputMediaAudio(
            media=filename,
            thumb=thumb_image_path,
            caption=os.path.basename(filename),
            title=os.path.basename(filename)
        )

    if cb_data.startswith("video"):
        filename = await downloadvideocli(video_command)
        dur = round(duration(filename))
        med = InputMediaVideo(
            media=filename,
            duration=dur,
            width=width,
            height=height,
            thumb=thumb_image_path,
            caption=os.path.basename(filename),
            supports_streaming=True
        )

    if cb_data.startswith("docaudio"):
        filename = await downloadaudiocli(audio_command)
        med = InputMediaDocument(
            media=filename,
            thumb=thumb_image_path,
            caption=os.path.basename(filename),
        )

    if cb_data.startswith("docvideo"):
        filename = await downloadvideocli(video_command)
        dur = round(duration(filename))
        med = InputMediaDocument(
            media=filename,
            thumb=thumb_image_path,
            caption=os.path.basename(filename),
        )
    if med:
        loop.create_task(send_file(c, q, med, filename, thumb_image_path))
    else:
        print("med not found")


async def send_file(c, q, med, filename, thumb_image_path):
    print(med)
    try:
        await q.edit_message_reply_markup(
            InlineKeyboardMarkup([[InlineKeyboardButton("Uploading...", callback_data="down")]]))
        await c.send_chat_action(
            chat_id=q.message.chat.id,
            action=ChatAction.UPLOAD_DOCUMENT,
        )
        # this one is not working
        await q.edit_message_media(media=med)
    except Exception as e:
        print(e)
        await q.edit_message_text(e)
    finally:
        try:
            os.remove(filename)
            os.remove(thumb_image_path)
        except:
            pass
