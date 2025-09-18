import os
from glob import glob
from logger import logger
def delete_file(filename: str):
    base_path = 'media/'
    path = fr'{base_path}*{filename}*'
    logger.info(f'Проверка пути {path}')
    files = glob(path)

    logger.info(f'Найденные файлы {files}')
    if files:
        for file in files:
            logger.info(f"Файл удален {file}")
            os.remove(f"{file}")
        return True
    return False
