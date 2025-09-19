import os

from pyrogram import Client
from pyrogram import utils
import json
from redis_client import r


def get_peer_type_new(peer_id: int) -> str:
    peer_id_str = str(peer_id)
    if not peer_id_str.startswith("-"):
        return "user"
    elif peer_id_str.startswith("-100"):
        return "channel"
    else:
        return "chat"


utils.get_peer_type = get_peer_type_new


async def upload(filename: str, height: int, width: int, duration: int, title: str, message_id: str,
                 audio_only: bool = False) -> dict:
    file_path = f"media/{filename}"
    last_percent = 0
    try:

        def progress_callback(current, total):
            nonlocal last_percent

            if (current / total) * 100 - last_percent >= 8 or (current / total) * 100 == 100:
                r.lpush('answer', json.dumps({
                    "message_id": message_id,
                    "text": f"Загрузка видео в тг.\nНазвание: {title}\nПрогресс: {last_percent}%",
                    "method": "text"
                }, ensure_ascii=False))
                last_percent = (current / total) * 100

        # Загружаем видео в телеграм
        async with Client(
                "my_bot",
                api_id=os.environ['API_ID'],
                api_hash=os.environ['API_HASH'],
                bot_token=os.environ['BOT_API'],
        ) as app:
            if audio_only:
                audio_id = await app.send_audio(
                    chat_id=os.environ['CHAT_ID'],
                    audio=file_path,
                    title=title,
                    file_name=title,
                    duration=duration,
                    progress=lambda cur, tot: progress_callback(cur, tot)
                )
                id_ = audio_id.audio.file_id
                method = "audio"
            else:
                video_id = await app.send_video(
                    chat_id=os.environ['CHAT_ID'],
                    video=file_path,
                    height=height,
                    width=width,
                    duration=duration,
                    file_name=title,
                    caption=title,
                    progress=lambda cur, tot: progress_callback(cur, tot)
                )
                id_ = video_id.video.file_id
                method = "video"
        return {
            "file_id": id_,
            "method": method
        }
    except Exception as ex:
        raise ex
