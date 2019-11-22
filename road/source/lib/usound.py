import smbus2 as smbus
import time

ADDRESS = 0x48
CONV_DATA_REG   = 0x00
CONFIG_REG      = 0x01
CONFIG_REG_DEF  = 0x8583
CONFIG_REG_DEF_ARR = [(CONFIG_REG_DEF & 0xFF00) >> 8, (CONFIG_REG_DEF & 0x00FF)]

class USound:
    def __init__(self):
        self.i2c = smbus.SMBus(2)
        self.addr = ADDRESS

        # self.i2c.write_byte(0x00, 0x06, 0x00)
        # time.sleep(1)

        data = self.i2c.read_i2c_block_data(self.addr, CONFIG_REG, 2)
        if data != CONFIG_REG_DEF_ARR:
            print('error', data, CONFIG_REG_DEF_ARR)
            return

        # Set registers.
        data = [0x84, 0x03]
        self.i2c.write_i2c_block_data(self.addr, CONFIG_REG, data)

        data = self.i2c.read_i2c_block_data(self.addr, CONFIG_REG, 2)
        print(data)


    def read(self):
        data = self.i2c.read_i2c_block_data(self.addr, CONV_DATA_REG, 2)
        data = (data[0] << 8) or (data[1])
        return data >> 4
        # return (data & (0xFFF0)) >> 4

    def read_converted(self):
        data = self.read()

