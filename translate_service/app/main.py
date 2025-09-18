import json

from logger import logger
from redis_client import r
from translate import translate


def translate_(msg_dict, key):
    try:
        text = 'Перевод...'
        r.lpush('answer', json.dumps({
            "message_id": key,
            "text": text,
            "method": "text"
        }, ensure_ascii=False))
        translate(msg_dict["video_id"])

        if msg_dict.get("audio_only"):
            r.hset(key, {
                "filename": f'{msg_dict["video_id"]}.mp3',
            })
            r.lpush('upload', key)

        else:
            r.hset(key, {
                "filename_audio": f'{msg_dict["video_id"]}.mp3',
            })
            r.lpush('merge', key)

        text = 'Переведено'
        r.lpush('answer', json.dumps({
            "message_id": key,
            "text": text,
            "method": "text"
        }, ensure_ascii=False))

        logger.info('Перевод скачан')

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
        msg = r.brpop("translate", timeout=0.1)
        if not msg:
            continue
        key = msg[1].decode()
        msg_dict = r.hmget(key, ['video_id', 'audio_only', 'id'])
        logger.info(msg_dict)
        translate_(msg_dict, key)


if __name__ == '__main__':
    logger.info("Service started")
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        r.close()
