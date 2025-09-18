from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineQuery, InlineKeyboardMarkup, \
    InlineKeyboardButton, InlineQueryResultArticle, InputTextMessageContent, ChosenInlineResult, CallbackQuery

from func import extract_youtube_id, search_youtube, get_youtube_query
from redis_client import r

router = Router()


@router.message(Command("start"))
async def start(message: Message):
    await message.reply('Hi!')


@router.inline_query()
async def inline_download(inline_query: InlineQuery):
    text = inline_query.query
    if not text:
        return

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=" ", callback_data="button1")],
    ])
    if 'instagram' in text:
        results = [
            InlineQueryResultArticle(
                id=f"{inline_query.id}?instagram",
                title='Отправить видео',
                description=f"Отправка видео по ссылке {text}",
                input_message_content=InputTextMessageContent(message_text=text),
                reply_markup=keyboard,
            ),
            InlineQueryResultArticle(
                id=f"{inline_query.id}?instagram?audio_only",
                title='Отправить аудио',
                description=f"Отправка аудио по ссылке {text}",
                input_message_content=InputTextMessageContent(message_text=text),
                reply_markup=keyboard,
            )
        ]

    elif extract_youtube_id(text):
        results = [
            InlineQueryResultArticle(
                id=f"{inline_query.id}?youtube",
                title='Отправить видео',
                description=f"Отправка видео по ссылке {text}",
                input_message_content=InputTextMessageContent(message_text=text),
                reply_markup=keyboard,
            ),
            InlineQueryResultArticle(
                id=f"{inline_query.id}?youtube?audio_only",
                title='Отправить аудио',
                description=f"Отправка аудио по ссылке {text}",
                input_message_content=InputTextMessageContent(message_text=text),
                reply_markup=keyboard,
            ),
            InlineQueryResultArticle(
                id=f"{inline_query.id}?youtube?translate",
                title='Отправить видео с переводом',
                description=f"Отправка видео с переводом по ссылке {text}",
                input_message_content=InputTextMessageContent(message_text=text),
                reply_markup=keyboard,
            ),
            InlineQueryResultArticle(
                id=f"{inline_query.id}?youtube?translate?audio_only",
                title='Отправить аудио перевода',
                description=f"Отправка аудио перевода по ссылке {text}",
                input_message_content=InputTextMessageContent(message_text=text),
                reply_markup=keyboard,
            ),

        ]
    else:
        data = await search_youtube(text)
        variants = get_youtube_query(data)
        print(variants)
        results = [
            InlineQueryResultArticle(
                id=f"{id_}?pass",
                title='Отправить видео',
                description=description,
                input_message_content=InputTextMessageContent(message_text=description),
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[[
                        InlineKeyboardButton(text="Скачать видео", callback_data=f"download?{id_}?video"),
                        InlineKeyboardButton(text="Скачать только аудио", callback_data=f"download?{id_}?audio"),
                    ],
                        [

                            InlineKeyboardButton(text="Скачать видео с переводом",
                                                 callback_data=f"download?{id_}?translate?video"),
                            InlineKeyboardButton(text="Скачать только аудио с переводом",
                                                 callback_data=f"download?{id_}?translate?audio"),
                        ]]
                ),
            ) for description, id_ in variants[:10]
        ]

    await inline_query.answer(results=results, cache_time=1)


@router.callback_query(F.data.startswith("download?"))
async def process_callback_variant(callback: CallbackQuery):
    message_id = callback.inline_message_id
    id_ = callback.data.split('?')[1]
    bot = callback.bot
    audio_only = '1' if 'audio' in callback.data else '0'
    translate = '1' if 'translate' in callback.data else '0'

    r.hset(message_id, mapping={
        "service": "youtube",
        "id": id_,
        "audio_only": audio_only,
        "translate": translate,
    })
    r.lpush('download', message_id)

    await bot.edit_message_text(text=f'Загрузка...',
                                inline_message_id=message_id)
    return


@router.chosen_inline_result()
async def test(chosen_inline_result: ChosenInlineResult):
    if chosen_inline_result.result_id.split('?')[-1] == 'pass':
        return
    message_id = chosen_inline_result.inline_message_id
    bot = chosen_inline_result.bot
    service_ = chosen_inline_result.result_id.split('?')[1]
    youtube_id = extract_youtube_id(chosen_inline_result.query)
    audio_only = '1' if chosen_inline_result.result_id.split('?')[-1] == "audio_only" else '0'
    translate = '1' if "translate" in chosen_inline_result.result_id else '0'
    if not youtube_id:
        youtube_id = chosen_inline_result.result_id.split('?')[0]
    if service_ == "youtube":
        r.hset(message_id, mapping={
            "service": "youtube",
            "id": youtube_id,
            "audio_only": audio_only,
            "translate": translate,
        })
        r.lpush('download', message_id)

    elif service_ == "instagram":
        r.hset(message_id, mapping={
            "service": "instagram",
            "id": chosen_inline_result.query,
            "audio_only": audio_only,
            "translate": "0",
        })
        r.lpush('download', message_id)


    else:
        return

    await bot.edit_message_text(text=f'Загрузка...',
                                inline_message_id=message_id)
    return
