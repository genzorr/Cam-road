import smbus2 as smbus

class PortExpander:
    IODIRA = 0
    IODIRB = 1
    IOPOLA = 2
    IOPOLB = 3
    GPINTTENA = 4
    GPINTTENB = 5
    DEFVALA = 6
    DEFVALB = 7
    INTCONA = 8
    INTCONB = 9
    IOCON = 10
    GPPUA = 12
    GPPUB = 13
    INTFA = 14
    INTFB = 15
    INTCAPA = 16
    INTCAPB = 17
    GPIOA = 18
    GPIOB = 19
    OLATA = 20
    OLATB = 21

    def __init__(self, addres_offset = 0):
        self.i2c = smbus.SMBus(2)
        self.addr = 0x20 + addres_offset
        self.i2c.write_byte_data(self.addr, 5,0) #if BANK = 1 set it to 0
        self.i2c.write_byte_data(self.addr, self.IOCON, 1<<2 | 1<<6)
        

    '''set pin direction 8 bits per ports
       A port is LO byte
       B port is HI byte
       each bit mean
       0 - input
       1 - output'''
    def setdir(self, value):
        value = (~value)&0xFFFF
        self.i2c.write_i2c_block_data(self.addr, self.IODIRA, value.to_bytes(2, byteorder='little'))
        #self.i2c.write_byte_data(self.addr, self.IODIRA + (port & 1), (~value)&0xFF)

    def getdir(self):
        l = self.i2c.read_i2c_block_data(self.addr, self.IODIRA, 2)
        value = int.from_bytes(l, byteorder='little')
        return (~value)&0xFFFF
        #return (~self.i2c.read_byte_data(self.addr, self.IODIRA + (port & 1)))&0xFF

    def setdirbits(self, bitmask):
        b = self.getdir()
        b |= bitmask
        self.setdir(b)

    def resetdirbits(self,bitmask):
        b = self.getdir(port)
        b &= (~bitmask) & 0xFFFF
        self.setdir(b)

    def setinterrupt(self, bitmask, changemask, pinmask):
        ''' bitmask - какие пины могут вызывать прерывание
            changemask - 0 сравнивается с предыдущим значением, 1 - с pinmask ''' 
        self.i2c.write_i2c_block_data(self.addr, self.GPINTTENA, bitmask.to_bytes(2, byteorder='little'))
        self.i2c.write_i2c_block_data(self.addr, self.INTCONA, changemask.to_bytes(2, byteorder='little'))
        self.i2c.write_i2c_block_data(self.addr, self.DEFVALA, pinmask.to_bytes(2, byteorder='little'))
        
    def clearinterrupt(self):
        self.getinterruptport()

    def setpullup(self, bitmask):
        self.i2c.write_i2c_block_data(self.addr, self.GPPUA, bitmask.to_bytes(2, byteorder='little'))

    '''if bit set its pin caused interrupt
       to clear call getinterruptport()'''
    def getinterruptflag(self):
        l = self.i2c.read_i2c_block_data(self.addr, self.INTFA, 2)
        value = int.from_bytes(l, byteorder='little')
        return value

    '''port captured state when interrupt occurred'''
    def getinterruptport(self):
        l = self.i2c.read_i2c_block_data(self.addr, self.INTCAPA, 2)
        value = int.from_bytes(l, byteorder='little')
        return value

    def getword(self):
        l = self.i2c.read_i2c_block_data(self.addr, self.GPIOA, 2)
        value = int.from_bytes(l, byteorder='little')
        return value

    def getbyte(self, port):
        return self.i2c.read_byte_data(self.addr, self.GPIOA + (port & 1))

    def getdatareg(self):
        l = self.i2c.read_i2c_block_data(self.addr, self.OLATA, 2)
        value = int.from_bytes(l, byteorder='little')
        return value

    def setbyte(self, port, value):
        self.i2c.write_byte_data(self.addr, self.OLATA + (port & 1), value)

    def setword(self, value):
        self.i2c.write_i2c_block_data(self.addr, self.OLATA, value.to_bytes(2, byteorder='little'))

    def setbits(self,bitmask):
        b = self.getdatareg()
        b |= bitmask
        self.setword(b)

    def resetbits(self,bitmask):
        b = self.getdatareg()
        b &= (~bitmask)&0xFFFF
        self.setword(b)
