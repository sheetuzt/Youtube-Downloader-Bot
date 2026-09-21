import os


def required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


BOT_TOKEN = required_env("BOT_TOKEN")
APP_ID = int(required_env("API_ID"))
API_HASH = required_env("API_HASH")

youtube_next_fetch = 0  # time in minutes
EDIT_TIME = 5
