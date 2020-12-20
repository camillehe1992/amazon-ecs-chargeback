# logger.py

import os
import logging

os.environ.setdefault('ENABLE_DEBUG', 'True')

log_level = logging.INFO

if 'ENABLE_DEBUG' in os.environ.keys():
    enable_debug = os.environ['ENABLE_DEBUG']

    if enable_debug == 'True' or enable_debug == 'true':
        log_level = logging.DEBUG

LOG_FORMAT = "[%(module)s:%(funcName)s] %(levelname)s: %(message)s"
logging.basicConfig(
    level=log_level,
    format=LOG_FORMAT
)

logger = logging
