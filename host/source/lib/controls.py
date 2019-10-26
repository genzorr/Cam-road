from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian

from PyQt5.QtCore import pyqtSlot


button_reg = 3
indicator_reg = 4

ENC_MAX = 100
ENC_MIN = 0

LED10   = (1 << 0)
LED9    = (1 << 1)
LED8    = (1 << 2)
LED7    = (1 << 3)
LED6    = (1 << 4)
LED5    = (1 << 5)
LED4    = (1 << 6)
LED3    = (1 << 7)
LED2    = (1 << 8)
LED1    = (1 << 9)
LEDALL  = LED1 | LED2 | LED3 | LED4 | LED5 | LED6 | LED7 | LED8 | LED9 | LED10

VAL0  = LEDALL
VAL10 = LED2 | LED3 | LED4 | LED5 | LED6 | LED7 | LED8 | LED9 | LED10
VAL20 = LED3 | LED4 | LED5 | LED6 | LED7 | LED8 | LED9 | LED10
VAL30 = LED4 | LED5 | LED6 | LED7 | LED8 | LED9 | LED10
VAL40 = LED5 | LED6 | LED7 | LED8 | LED9 | LED10
VAL50 = LED6 | LED7 | LED8 | LED9 | LED10
VAL60 = LED7 | LED8 | LED9 | LED10
VAL70 = LED8 | LED9 | LED10
VAL80 = LED9 | LED10
VAL90 = LED10
VAL100 = 0

VAL = [VAL0, VAL10, VAL20, VAL30, VAL40, VAL50, VAL60, VAL70, VAL80, VAL90, VAL100]


class Controller:
    def __init__(self):
        self.client = ModbusClient(method = "rtu", port="/dev/ttySAC3", stopbits = 1,
                                   bytesize = 8, parity = 'N', baudrate= 115200,
                                   timeout = 0.8, strict=False)
        self.id = 2
        self.encoders = [0, 0, 0]
        self.buttons = [0, 0, 0, 0, 0, 0, 0, 0, 0]

        # Try to connect to modbus client.
        self.status = self.client.connect()
        print("Modbus client init OK.") if self.status else print("Modbus init failed.")

        self.off()

    @pyqtSlot()
    def off(self):
        self.setEncoderValue(1, 0)
        self.setEncoderValue(2, 0)
        self.setEncoderValue(3, 0)

        self.setIndicator(1, 0)
        self.setIndicator(2, 0)
        self.setIndicator(3, 0)


    def saferead(self, addr, count, unit, retry = 3):
        if not self.status:
            return (None, False)

        while retry > 0:
            result = self.client.read_holding_registers(addr, count, unit=unit)
            if hasattr(result, 'registers'):
                return (result, True)
            retry -= 1
            self.status = False
        #logging.info(f'addr {addr}, unit {unit}')
        return (None, False)


    def getEncoderValue(self, encoder):
        result,success = self.saferead(encoder-1, 1, unit=self.id)
        if not success:
            return False
        decoder = BinaryPayloadDecoder.fromRegisters(result.registers,
                                                     byteorder=Endian.Big,
                                                     wordorder=Endian.Little)
        value = decoder.decode_16bit_int()
        if (value > ENC_MAX):
            value = ENC_MAX
            self.setEncoderValue(encoder, ENC_MAX)
        if (value < ENC_MIN):
            value = ENC_MIN
            self.setEncoderValue(encoder, ENC_MIN)

        self.encoders[encoder-1] = (value/ENC_MAX)*100
        return self.encoders[encoder-1]

    def setEncoderValue(self, encoder, value):
        builder = BinaryPayloadBuilder(byteorder=Endian.Big,
                                       wordorder=Endian.Little)
        builder.add_16bit_int(value)
        payload = builder.to_registers()[0]
        self.client.write_register((encoder-1), payload, unit=self.id)


    def getButtonValue(self, button):
        result,success = self.saferead(button_reg, 1, unit=self.id)
        if not success:
            return (False, False)
        decoder = BinaryPayloadDecoder.fromRegisters(result.registers,
                                                     byteorder=Endian.Big,
                                                     wordorder=Endian.Little)
        value = decoder.decode_16bit_int()
        self.buttons[button-1] = (value and (1 << (button-1)))
        return (self.buttons[button-1], value)

    def setButtonValue(self, button, value):
        if (value == 1):
            dummy, register = getButtonValue(button)
            if (register == False):
                return

            button -= 1
            register = ~(~register and (value << button))
            builder = BinaryPayloadBuilder(byteorder=Endian.Big,
                                           wordorder=Endian.Little)
            builder.add_16bit_int(value)
            payload = builder.to_registers()[0]
            self.client.write_register(button_reg, payload, unit=self.id)

    def setIndicator(self, indicator, count):
        builder = BinaryPayloadBuilder(byteorder=Endian.Big,
                                       wordorder=Endian.Little)
        builder.add_16bit_int(VAL[count])
        payload = builder.to_registers()[0]
        self.client.write_register(indicator_reg + (4-indicator), payload, unit=self.id)
