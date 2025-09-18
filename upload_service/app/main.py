import asyncio
import json

from logger import logger
from redis_client import r
from upload_media import upload
from dotenv import load_dotenv
load_dotenv()

def upload_(msg_dict, key):
    try:

        r.lpush('answer', json.dumps({
            "message_id": key,
            "text": f"Загрузка видео в тг.\nНазвание: {msg_dict['title']}\nПрогресс: {0}%",
            "method": "text"
        }, ensure_ascii=False))
        info = asyncio.run(upload(
            filename=msg_dict['filename'],
            message_id=key,
            title=msg_dict["title"],
            height=msg_dict['height'],
            width=msg_dict['width'],
            duration=msg_dict['duration'],
            audio_only=msg_dict.get("audio_only")
        ))
        r.lpush('answer', json.dumps({
            "message_id": key,
            "file_id": info['file_id'],
            "method": info['method'],
        }, ensure_ascii=False))
        r.lpush('delete', key)
        logger.info('Upload success')
    except Exception as ex:

        value = {
            "error_message": str(ex) + '\n' + msg_dict.get("id"),
            "reason": ex.__class__.__name__,
        }
        r.hset(key, mapping=value)
        logger.error(value)


def main():
    while True:
        # Получает id сообщения в качестве ключа
        msg = r.brpop("upload", timeout=0.1)
        if not msg:
            continue
        key = msg[1].decode()
        msg_dict = r.hmget(key, ['filename', 'title', 'height', 'width', 'duration', 'audio_only', 'id'])
        logger.info(msg_dict)
        upload_(msg_dict, key)


if __name__ == '__main__':
    logger.info("Service started")
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        r.close()
