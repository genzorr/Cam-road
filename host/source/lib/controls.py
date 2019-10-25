from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian


class Controller:
    def __init__(self):
        self.client = ModbusClient(method = "rtu", port="/dev/ttySAC3", stopbits = 1,
                                   bytesize = 8, parity = 'N', baudrate= 115200,
                                   timeout = 0.8, strict=False)
        self.id = 2

        # Try to connect to modbus client.
        client_status = self.client.connect()
        print("Modbus client init OK.") if client_status else print("Modbus init failed.")


    def saferead(self, addr, count, unit, retry = 3):
        while retry > 0:
            result = self.client.read_holding_registers(addr, count, unit=unit)
            if hasattr(result, 'registers'):
                return (result, True)
            retry -= 1
            print('# Saferead failed')
        #logging.info(f'addr {addr}, unit {unit}')
        return (None, False)

    def getEncoderValue(self, enc_num):
        result,succes = self.saferead(enc_num, 1, unit=self.id)
        decoder = BinaryPayloadDecoder.fromRegisters(result.registers,
                                                     byteorder=Endian.Big,
                                                     wordorder=Endian.Little)

        return decoder.decode_16bit_int()
