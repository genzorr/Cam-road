import sys
sys.path.append('../fortune-controls/Lib')
import threading

from pymodbus.client.sync import ModbusSerialClient as ModbusClient #initialize a serial RTU client instance
from x4motor import X4Motor
from lib.indicator import *
from watcher import *
from lib.lsm6ds3 import *
import time

global NO_MOTOR

#-------------------------------------------------------------------------------------#
#   Settings
config = {'id': 1,\
        'Mode': 'Angle',\
        'PWM_Limit' : 300,\
        'PWM_inc_limit' : 2,\
        'I_limit': 5.0,\
        'V_min': 12.0,\
        'Angle_PID_P' : 100,\
        'Angle_PID_I' : 1,\
        'Speed_PID_P' : 100,\
        'Speed_PID_I' : 100,\
        'StepsPerMM': 210,\
        'TimeOut' : 1000,\
        'TempShutDown' : 75,\
        'Reverse': 0}           #   210 - 1step = 0.01m
#-------------------------------------------------------------------------------------#

def initAll():
    # FIXME: MOTOR
    # print("Motor connection...")
    # client= ModbusClient(method = "rtu", port="/dev/ttyS1", stopbits = 1,
    #                      bytesize = 8, parity = 'N', baudrate= 115200,
    #                      timeout = 0.8, strict=False )

    # #   Try to connect to modbus client
    # client_status = client.connect()

    # #   Motor initialization
    # M = X4Motor(client, settings = config)
    # print("OK") if client_status and M else print("Failed")

    # #   Print all registers
    # registers = M.readAllRO()
    # print(registers)

    # #   Indicator initialization
    # portex = indicator_init()
    client, M, portex = None, None, None

    #   Serial init
    serial_device = serial_init()
    if (serial_device == None):
        print('Could not open port')

    #   Accel init
    accel = Accelerometer()
    accel.ctrl()

    return client, M, portex, serial_device, accel


if __name__ == '__main__':
    try:
        client, M, portex, serial_device, accel = initAll()

        writer = Writer()
        writer.start()

        motor_control = Motor_control(motor=M)
        motor_control.start()

        watcher = Watcher(motor_control=motor_control, writer=writer, serial_device=serial_device, accel=accel)
        watcher.start()

        # FIXME: MOTOR
        # while True:
        #     V = M.readV()
        #     indicate(V, portex)
        #     time.sleep(10)


    except KeyboardInterrupt:
        print()

        watcher.do_run = False
        watcher.join()

        motor_control.do_run = False
        motor_control.join()

        writer.do_run = False
        writer.join()

        # FIXME: MOTOR
        # indicator_off(portex)
        # M.release()             # Release motor
        # client.close()
