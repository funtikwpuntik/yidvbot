from redis_client import r

from logger import logger

from merge import merge


def merge_(msg_dict, key):
    try:
        merge(msg_dict["filename"], msg_dict["filename_audio"])
        r.hset(key, key="filename", value=f"{msg_dict['filename']}_out.mp4")
        logger.info('Видео переведено')
        r.lpush('upload', key)

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
        msg = r.brpop("merge", timeout=0.1)
        if not msg:
            continue
        key = msg[1].decode()
        msg_dict = r.hmget(key, ['filename', 'filename_audio', 'id'])
        logger.info(msg_dict)
        merge_(msg_dict, key)




if __name__ == '__main__':
    logger.info("Service started")
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        r.close()
