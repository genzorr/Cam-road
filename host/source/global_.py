global mutex
global newHTR

global window

global watcher
global controlThread
global mbeeThread

global killer

global hostData
global roadData
global specialData

global settings
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

''' Unused function to configure logging
def configure_logging(level=logging.INFO):
    format = ' '.join([
        '%(asctime)s',
        '%(filename)s:%(lineno)d',
        '%(threadName)s',
        '%(levelname)s',
        '%(message)s'
    ])
    formatter = logging.Formatter(format)

    logger = logging.getLogger()

    # Remove existing handlers
    for handler in list(logger.handlers):
        logger.removeHandler(handler)

    logger.setLevel(level)

    fileHandler = logging.StreamHandler(sys.stderr)
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)
'''