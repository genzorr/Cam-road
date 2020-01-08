global mutex

global window

global watcher
global controlThread
global mbeeThread

global killer

global hostData
global roadData
global specialData

global TX_ADDR_HOST
global TX_ADDR_ROAD

import sys
import logging
import coloredlogs

format = "%(asctime)s — %(name)-7s — %(levelname)s — %(filename)-12s:%(lineno)3d — %(message)s"
# FORMATTER = logging.Formatter(format)
FORMATTER = coloredlogs.ColoredFormatter(format)

def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler

def get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    logger.addHandler(get_console_handler())
    logger.propagate = False
    return logger
