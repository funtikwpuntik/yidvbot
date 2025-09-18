from logger import logger
from match import download_match_data
from redis_client import r


def download_(msg_dict, key):
    try:
        attempts = 0
        error_ = ''
        while attempts < 3:
            try:
                info = download_match_data(msg_dict, key)
                if info:

                    if msg_dict.get('translate'):
                        r.lpush('translate', key)
                    else:
                        r.lpush('upload', key)

                    logger.info('Видео скачано')
                    break
            except Exception as ex:
                attempts += 1
                error_ = ex
        else:
            raise error_

    except Exception as ex:

        value = {
            "error_message": str(ex) + '\n' + str(msg_dict.get("id")),
            "reason": ex.__class__.__name__,
        }
        r.hset(key, mapping=value)
        logger.error(value)


def main():
    while True:
        # Получает id сообщения в качестве ключа
        msg = r.brpop("download", timeout=0.1)
        if not msg:
            continue
        key = msg[1].decode()
        msg_dict = r.hmget(key, ['service', 'audio_only', 'id'])
        logger.info(msg_dict)
        download_(msg_dict, key)


if __name__ == '__main__':
    logger.info("Service started")
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        r.close()
