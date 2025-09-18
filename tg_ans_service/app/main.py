import asyncio
from redis_client import r
import json
from logger import logger

from ans import ans_tg

def main():
    while True:
        # Получает id сообщения в качестве ключа
        msg = r.brpop("answer", timeout=0.1)
        if not msg:
            continue
        msg_dict = json.loads(msg[1].decode())
        logger.info(msg_dict)
        try:
            a = asyncio.run(ans_tg(msg_dict))
            if not a:
                raise Exception("Ошибка при ответном сообщении")

        except Exception as ex:

            value = {
                "error_message": str(ex) + '\n' + str(msg_dict),
                "reason": ex.__class__.__name__,
            }
            logger.error(value)

if __name__ == '__main__':
    logger.info("Service started")
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        r.close()