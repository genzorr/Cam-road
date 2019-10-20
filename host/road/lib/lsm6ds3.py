import smbus2 as smbus
from .lsm6ds3_const import *

WHO_AM_I_ANSWER = 0x69
WHO_AM_I_REG = 0xF
ADDRESS = 0x6A
ACCEL_SENS_SCALE = 0.061

class ACCGYRO:

    WHO_IAM_ANSWER = 0x69
    WHO_IAM_REG = 0xF

    def __init__(self, communication, dev_selector):
        # enable autoincrement
        tmp = self.read_u8(LSM6DS3_XG_CTRL3_C)
        tmp |= LSM6DS3_XG_IF_INC
        self.write_u8(LSM6DS3_XG_CTRL3_C, tmp)
        # Disable FIFO
        self.write(LSM6DS3_XG_FIFO_CTRL5,
                   LSM6DS3_XG_FIFO_MODE['BYPASS'] | LSM6DS3_XG_FIFO_ODR['NA'])

    def set_multi_byte(self, addr):
        ''' Multi byte read is configured in register CTRL3'''
        return addr

    def temperature(self):
        t = self.read_s16(LSM6DS3_TEMP_OUT_L)
        return 25.0 + t / 16.0


class Accelerometer:
    def __init__(self):
        self.i2c = smbus.SMBus(2)
        self.addr = ADDRESS
        self.scale = 0
        self.scale_byte = 0

        if self.i2c.read_byte_data(self.addr, WHO_AM_I_REG) == WHO_AM_I_ANSWER:
            # Make reset
            #   TODO: ADD

            # Enable autoincrement
            tmp = self.i2c.read_byte_data(self.addr, LSM6DS3_XG_CTRL3_C)
            tmp |= LSM6DS3_XG_IF_INC
            self.i2c.write_byte_data(self.addr, LSM6DS3_XG_CTRL3_C, tmp)

            # Disable FIFO
            self.i2c.write_byte_data(self.addr, LSM6DS3_XG_FIFO_CTRL5,
                       (LSM6DS3_XG_FIFO_MODE['BYPASS'] | LSM6DS3_XG_FIFO_ODR['NA']))

        else:
            raise Exception('Accelerometer LSM6DS3 init fail')

    def ctrl(self, g_odr='416HZ', g_full_scale_g='2G', g_axis_en="XYZ"):
        g_odr = g_odr.upper()
        g_full_scale_g = g_full_scale_g.upper()
        g_axis_en = g_axis_en.upper()
        self.scale = g_full_scale_g
        if self.scale == 2:
            self.scale_byte = 0
        elif self.scale == 4:
            self.scale_byte = 1
        elif self.scale == 6:
            self.scale_byte = 2
        elif self.scale == 8:
            self.scale_byte = 3
        elif self.scale == 16:
            self.scale_byte = 4

        tmp = self.i2c.read_byte_data(self.addr, LSM6DS3_XG_CTRL1_XL)
        tmp &= ~LSM6DS3_XL_ODR['MASK']
        tmp |= LSM6DS3_XL_ODR[g_odr]
        tmp &= ~LSM6DS3_XL_FS['MASK']
        tmp |= LSM6DS3_XL_FS[g_full_scale_g]
        self.i2c.write_byte_data(self.addr, LSM6DS3_XG_CTRL1_XL, tmp)

        tmp = self.i2c.read_byte_data(self.addr, LSM6DS3_XG_CTRL9_XL)
        tmp &= ~LSM6DS3_XL_AXIS_EN['MASK']
        tmp |= LSM6DS3_XL_AXIS_EN['X'] if 'X' in g_axis_en else 0
        tmp |= LSM6DS3_XL_AXIS_EN['Y'] if 'Y' in g_axis_en else 0
        tmp |= LSM6DS3_XL_AXIS_EN['Z'] if 'Z' in g_axis_en else 0
        self.i2c.write_byte_data(self.addr, LSM6DS3_XG_CTRL9_XL, tmp)


    #   FIXME: remove getting sensitivity every single time
    def getdata(self):
        '''
        Returns the acceleration in g.
        '''
        # Get raw data
        d = self.i2c.read_i2c_block_data(self.addr, LSM6DS3_XG_OUT_X_L_XL, 6)
        r = [int.from_bytes(d[i*2:i*2+2], byteorder='little', signed=True) for i in range(3)]
        # Get sensitivity
        sens = (1 << (self.scale_byte >> LSM6DS3_XL_FS['SHIFT'])) * ACCEL_SENS_SCALE * 9.81 / 1000
        return [i*sens for i in r]
