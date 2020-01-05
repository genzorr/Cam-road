VELO_MAX = 60
ACCEL_MAX = 20
BRAKING_MAX = 20

global lock
global hostData
global roadData
global specialData

global watcher
global writer
global mbee_thread
global motor_thread

import sys
import logging
import coloredlogs

format = "%(asctime)s — %(name)-7s — %(levelname)s — %(filename)-12s:%(lineno)3d — %(message)s"
FORMATTER = coloredlogs.ColoredFormatter(fmt=format, datefmt='%d-%m-%y %H:%M:%S')

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
