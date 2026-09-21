from pyrogram import Client
import config

DOWNLOAD_LOCATION = "./Downloads"
BOT_TOKEN = config.BOT_TOKEN

APP_ID = config.APP_ID
API_HASH = config.API_HASH


plugins = dict(
    root="plugins",
)

Client(
    "YouTubeDlBot",
    bot_token=BOT_TOKEN,
    api_id=APP_ID,
    api_hash=API_HASH,
    # Heroku dynos use an ephemeral filesystem. Do not reuse a stale
    # session file, which can produce BadMsgNotification [16] on startup.
    in_memory=True,
    plugins=plugins,
    workers=100
).run()
