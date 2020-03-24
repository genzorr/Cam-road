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

# Properly set styleSheet of "name" Qt object (without losing original style).
def addStyleSheet(obj, name, newStyleSheet):
    style = name + '{' + obj.styleSheet() + '} ' + newStyleSheet
    obj.setStyleSheet(style)
    print(obj, style)

def styleChangeProperty(obj, property, value):
    style = obj.styleSheet()

    newProperty = property + ': ' + value + ';'
    pos = style.find(property)    # position of property string
    if pos == -1:   # no property set
        style += newProperty
    else:
        pos_sep = style.find(';', pos)  # position of next separator
        style = style[0:pos] + newProperty + style[(pos_sep + 1):]
        # if (pos == 0):
        #     style += newProperty
        # elif (style[pos-1] == ';') or (style[pos-1] == '{'):  # check that it if full name
        #     pos_sep = style.find(';', pos)  # position of next separator
        #     if pos_sep == -1:
        #         style = style[0:pos] + newProperty
        #     else:
        #         style = style[0:pos] + newProperty + style[(pos_sep + 1):]  # new style with added value
        # else:
        #     pos = style.find(property, pos)  # to avoid similar strings like 'background-color' and 'color'
        #     if pos == -1:  # no property set
        #         style += newProperty
        #     else:
        #         pos_sep = style.find(';', pos)  # position of next separator
        #         if pos_sep == -1:
        #             style = style[0:pos] + newProperty
        #         else:
        #             style = style[0:pos] + newProperty + style[(pos_sep + 1):]  # new style with added value

    # print(obj, style, '| ', property, value)
    try:
        obj.setStyleSheet(style)
    except BaseException as ex:
        print('setStyleSheet exception caught: ', ex)

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