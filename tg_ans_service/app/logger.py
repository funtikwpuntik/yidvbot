from loguru import logger
import os
common_config = {
    'rotation': "1 hour",
    'retention': "3 days",
    'compression': "zip",
    'encoding': 'utf-8',
}

logger.add(f'log/{os.environ.get("HOSTNAME")}.log', **common_config)