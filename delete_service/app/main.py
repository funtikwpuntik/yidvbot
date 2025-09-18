from delete_file import delete_file
from logger import logger
from redis_client import r

def main():
    while True:
        msg = r.brpop("delete", timeout=1)
        if not msg:
            continue
        key = msg[1].decode()
        msg_dict = r.hmget(key, ['video_id'])
        logger.info(msg_dict)

        logger.info(msg_dict)
        try:
            filename = msg_dict["video_id"]
            if delete_file(filename):
                logger.info(f"Файл {filename} удален!")
            else:
                logger.warning(f"Файл {filename} удален!")

        except Exception as ex:

            value = {
                "error_message": str(ex) + '\n' + msg_dict.get("video_id"),
                "reason": ex.__class__.__name__,
            }
            r.hset(key, mapping=value)
            logger.error(value)



if __name__ == '__main__':
    logger.info("Service started")
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        r.close()

