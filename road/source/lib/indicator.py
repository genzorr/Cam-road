from .portex import PortExpander
import global_
from global_ import get_logger

#-------------------------------------------------------------------------------------#
#   Settings
V_MAX = 4.2
V_MIN = 3.3

LED10   = (1 << 8)
LED9    = (1 << 9)
LED8    = (1 << 10)
LED7    = (1 << 11)
LED6    = (1 << 12)
LED5    = (1 << 13)
LED4    = (1 << 14)
LED3    = (1 << 15)
LED2    = (1 << 0)
LED1    = (1 << 1)
LEDALL  = LED1 | LED2 | LED3 | LED4 | LED5 | LED6 | LED7 | LED8 | LED9 | LED10

BAT0  = LEDALL
BAT10 = LED2 | LED3 | LED4 | LED5 | LED6 | LED7 | LED8 | LED9 | LED10
BAT20 = LED3 | LED4 | LED5 | LED6 | LED7 | LED8 | LED9 | LED10
BAT30 = LED4 | LED5 | LED6 | LED7 | LED8 | LED9 | LED10
BAT40 = LED5 | LED6 | LED7 | LED8 | LED9 | LED10
BAT50 = LED6 | LED7 | LED8 | LED9 | LED10
BAT60 = LED7 | LED8 | LED9 | LED10
BAT70 = LED8 | LED9 | LED10
BAT80 = LED9 | LED10
BAT90 = LED10
BAT98 = 0

BAT = [BAT0, BAT10, BAT20, BAT30, BAT40, BAT50, BAT60, BAT70, BAT80, BAT90, BAT98]

num_cells = [4,6,8]
logger = get_logger('Indicator')
#-------------------------------------------------------------------------------------#
#   Initializes port expander for indicator
def indicator_init():
    port = []
    a = PortExpander(0)
    b = PortExpander(2)
    port.append(a)
    port.append(b)

    [i.setdir(LEDALL) for i in port]
    return port

#   Indicates by given voltage
def indicate(v, portex):
    for i in num_cells:
        value = (v/i - V_MIN) / (V_MAX - V_MIN)
        #print("indicate " + str(i) + " : " + str(value))
        if (value>0) and (value<1):
            break
        value = 0
        
    if (value > 0.1) and (value < 1) and len(num_cells) > 1:
        num_cells = [i]
        logger.info("Set num cells to ",i)
        
    res = value
    value = round(value*10) + 1
    if (value >= len(BAT) - 1):
        value = len(BAT) - 1
    elif value < 0:
        value = 0
    [i.setword(BAT[value]) for i in portex]
    return res*100
    #portex.setword(BAT[round(value)])

def indicator_off(portex):
    #indicate(V_MIN, portex)
    pass
