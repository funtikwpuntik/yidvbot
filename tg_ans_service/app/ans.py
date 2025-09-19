import asyncio
import os

from aiogram import Bot
from aiogram import types
from dotenv import load_dotenv

load_dotenv()


async def ans_tg(ans_data: dict):
    async with Bot(os.environ['BOT_API']) as bot:
        match ans_data.get("method"):
            case 'photo':

                await bot.edit_message_media(
                    media=types.InputMediaPhoto(media=ans_data.get("file_id"), caption='Загрузка', ),
                    inline_message_id=ans_data.get("message_id"), request_timeout=1)
            case 'video':
                media = types.InputMediaVideo(media=ans_data.get("file_id"))
                await asyncio.sleep(0.1)
                await bot.edit_message_media(media=media,
                                             inline_message_id=ans_data.get("message_id"), request_timeout=1)

            case 'text':
                await bot.edit_message_text(text=ans_data["text"], inline_message_id=ans_data.get("message_id"),
                                            request_timeout=1)

            case 'audio':
                media = types.InputMediaAudio(media=ans_data.get("file_id"))
                await asyncio.sleep(0.1)

                await bot.edit_message_media(media=media,
                                             inline_message_id=ans_data.get("message_id"), request_timeout=1)
            case _:
                raise Exception("Не указан метод обработки")

    return True
