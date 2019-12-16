# Библиотека MBee-Python для работы с модулями MBee производства фирмы "Системы, модули и компоненты".
# "Системы модули и компоненты" ("СМК"). 2018. Москва.
# Распространяется свободно. Надеемся, что программные продукты, созданные
# с помощью данной библиотеки будут полезными, однако никакие гарантии, явные или
# подразумеваемые не предоставляются.
# The MIT License(MIT)
# MBee-Python Library.
# Copyright © 2017 Systems, modules and components. Moscow. Russia.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files(the "Software"), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and / or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions :
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import time
import binascii
import functools
from serial import Serial

##
# Класс для проектов, основанных на программном обеспечении SerialStar.
#
class SerialStar:
    START_BYTE = "7E"
    ESCAPED_CHARACTER = ["7E","7D","11","13"]
    RX_TIMEOUT = 0.2 #Таймаут чтения в секундах из последовательного порта.
    WR_TIMEOUT = 0 #Таймаут на запись данный в последовательный порт. Если этот таймаут не определить, то начинает иногда происходить соответствующее исключение.
    API_FRAME_TX_TIMEOUT = 0.05 #Минимальный интервал времени в секундах между двумя фреймами, посылаемыми в последовательный порт.
    LOCAL_TX_STATUS_RETRY_COUNT = 1 #Число попыток получения API-фрейма со статусом отправки пакета в эфир.
    LOCAL_RESPONSE_RETRY_COUNT = 1 #Число попыток получения API-фрейма с ответом на локальную команду.
    REMOTE_RX_STATUS_RETRY_COUNT = 1 #Число попыток получения API-фрейма с подтверждением получения пакета с данными удаленным узлом.
    GET_FRAME_RETRY_COUNT = 1 #Число попыток получения любого фрейма перед возвратом из метода run() в основной скрипт.
    IO_SAMPLE_RX_RETRY_COUNT = 1 #Число попыток получения API-фрейма с данными о состоянии линий ввода/вывода от удаленного модуля.

    TX_STATUS_DECODE = {
        "00": "TX_OK",
        "01": "UNSUFFICIENT_MEMORY_FOR_PACKET",
        "02": "INVALID_COMMAND_CODE",
        "03": "INVALID_COMMAND_PARAMETER",
        "04": "TX_CCA_FAILURE",
    }

    TX_STATUS_ENCODE = {
        "TX_OK": "00",
        "UNSUFFICIENT_MEMORY_FOR_PACKET": "01",
        "INVALID_COMMAND_CODE": "02",
        "INVALID_COMMAND_PARAMETER": "03",
        "TX_CCA_FAILURE": "04",
    }

    PIN_ID_DECODE = {
        "02": "L0",
        "03": "L1",
        "04": "L2",
        "06": "L3",
        "07": "L4",
        "09": "L5",
        "0B": "L6",
        "0C": "L7",
        "0D": "L8",
        "0E": "B0",
        "0F": "B1",
        "10": "B2",
        "11": "B3",
        "12": "B4",
        "13": "B5",
        "18": "R9",
        "1B": "R8",
        "1C": "R7",
        "1D": "R6",
        "1E": "R5",
        "1F": "R4",
        "20": "R3",
        "21": "R2",
        "22": "R1",
        "23": "R0"
    }

    PIN_MODE_DECODE = {
        "02": "ANALOG_INPUT",
        "03": "DIGITAL_INPUT",
        "04": "DIGITAL_OUTPUT_LOW",
        "05": "DIGITAL_OUTPUT_HIGH",
        "0D": "COUNTER_INPUT_1",
        "0E": "COUNTER_INPUT_2",
        "0F": "WAKEUP_INPUT_FALLING",
        "10": "WAKEUP_INPUT_RISING"
    }

    GET_SAMPLE_LENGTH = {
        "02": 4,
        "03": 0,
        "04": 0,
        "05": 0,
        "0D": 8,
        "0E": 8,
        "0F": 0,
        "10": 0
    }

    ## @param port - имя COM-порта, которому подключен радиомодуль, в виде символьной строки, например "COM11".
    #  @param baud - битовая скорость COM-порта. Целое число. Возможные значения 9600, 19200, 38400, 57600, 115200, 230400. Настраивается только с помощью программы SysMC Bootloader.
    #
    # Модуль должен быть предварительно настроен для работы в пакетном режиме с escape-символами (AP = 2).
    def __init__(self, port, baud, rx_timeout):
        self.baud = baud
        self.port = port
        self.ser = Serial(self.port, self.baud, timeout = rx_timeout, write_timeout = self.WR_TIMEOUT)
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        self.on_rx_81_8F_frame_callback  = None
        self.on_rx_83_frame_callback = None
        self.on_rx_87_88_89_frame_callback = None
        self.on_rx_8A_frame_callback = None
        self.on_rx_8B_frame_callback = None
        self.on_rx_8C_frame_callback = None
        self.on_rx_97_frame_callback = None

    def add_hex2(self, hex1, hex2):
        return hex(int(hex1, 16) + int(hex2, 16))

    def sub_hex2(self,hex1, hex2):
        return hex(int(hex1, 16) - int(hex2, 16))

    def xor_hex(self, a, b):
        return '%x' % (int(a, 16) ^ int(b, 16))

    def toHex(self, s):
        lst = []
        for ch in s:
            hv = hex(ch).replace('0x', '')
            if len(hv) == 1:
                hv = '0' + hv
            lst.append(hv)
        return functools.reduce(lambda x, y: x + y, lst)

    def add_bytes(self,byte):
        self.bytes.append(byte)

    def get_bytes(self):
        return self.bytes

    def read_frame_infos(self):
        wait = True
        self.bytes = []
        length = 0
        type_hex = "00"
        while True:
            start_byte = self.ser.read()
            if(start_byte == b""):
                return {"length" : 0, "frame_type" : "00"}
            if self.toHex(start_byte).upper() == self.START_BYTE:
                self.bytes.append(start_byte)
                i = 1
                detect = False
                while i < 3:
                    cc = self.ser.read()
                    if(cc == b""):
                        return {"length" : 0, "frame_type" : "00"}
                    self.bytes.append(cc)
                    length_hex = ""
                    if self.toHex(cc).upper() in self.ESCAPED_CHARACTER:
                        detect = True
                        continue
                    else:
                        if detect:
                            length_hex += self.xor_hex(self.toHex(cc),"20")
                            detect = False
                        else:
                            length_hex += self.toHex(cc)
                        i += 1
                length = int(length_hex, 16)
                type_byte = self.ser.read()
                if(type_byte == b""):
                    return {"length" : 0, "frame_type" : "00"}
                self.bytes.append(type_byte)
                type_hex = self.toHex(type_byte).upper()
                return {"length" : length , "frame_type" : type_hex}

    def read_rx_api(self, type = []):
        while True:
            infos = self.read_frame_infos()
            length = infos["length"]
            if (infos["frame_type"] == type or type == []) and length != 0:
                while length > 0:
                    byte = self.ser.read()
                    if(byte == b""):
                        return "ERROR : received less than length bytes"
                    self.bytes.append(byte)
                    if not (self.toHex(byte).upper() in self.ESCAPED_CHARACTER):
                        length -= 1
                return self.bytes
            else:
                return "ERROR : received a Wrong frame !!! "

    def filter_frame(self):
        if self.toHex(self.bytes[0]).upper() != self.START_BYTE:
            return "ERROR invalid Frame"
        self.fields = [self.START_BYTE]
        detect = False
        for j in range(1, len(self.bytes)):
            byte = self.toHex(self.bytes[j]).upper()
            if byte in self.ESCAPED_CHARACTER:
                detect = True
            else:
                if detect :
                    self.fields.append(self.sub_hex2(byte,"20")[2:4])
                    detect=False
                else:
                    self.fields.append(byte)
        return self.fields

    ## Метод для регистрации callback-функции.
    # @param frame_type - тип фрейма, для которого надо зарегистрировать callback-функцию. Два шестнадцатеричных символа без 0x. Например "83".
    # @param function_name - имя функции, например frame_83_received.
    #
    # Зарегистрированная функция будет вызываться каждый раз при получении от модуля данного типа пакета.
    def callback_registring(self, frame_type, function_name):
        if frame_type == "81":
            self.on_rx_81_frame_callback = function_name
        elif frame_type == "83":
            self.on_rx_83_frame_callback = function_name
        elif frame_type == "87":
            self.on_rx_87_frame_callback = function_name
        elif frame_type == "88":
            self.on_rx_88_frame_callback = function_name
        elif frame_type == "89":
            self.on_rx_89_frame_callback = function_name
        elif frame_type == "8A":
            self.on_rx_8A_frame_callback = function_name
        elif frame_type == "8B":
            self.on_rx_8B_frame_callback = function_name
        elif frame_type == "8C":
            self.on_rx_8C_frame_callback = function_name
        elif frame_type == "8F":
            self.on_rx_8F_frame_callback = function_name
        elif frame_type == "97":
            self.on_rx_97_frame_callback = function_name

    def send_local_at(self, frame_type, frame_id, at_command, at_parameter = ""):
        if len(at_command) != 2:
            return  "Error : verify the Command AT !!!!"
        else:
            frame_local_at = []
            ll = 4 + len(at_parameter) // 2
            length = str(format(ll,"04x"))
            frame_local_at.append(length[0:2])
            frame_local_at.append(length[2:4])
            frame_local_at.append(frame_type)
            frame_local_at.append(frame_id)
            frame_local_at.append(self.toHex(bytes(at_command.upper(), encoding = "ascii"))[0:2])
            frame_local_at.append(self.toHex(bytes(at_command.upper(), encoding = "ascii"))[2:4])
            if len(at_parameter) > 0:
                for i in range(0, len(at_parameter), 2):
                    pp = at_parameter.upper()[i:i + 2]
                    frame_local_at.append(pp)
            checksum = "00"
            for i in range(2, len(frame_local_at)): #При подсчете контрольной суммы байты с длиной фрейма не учитываются.
                checksum = self.add_hex2(frame_local_at[i], checksum)
            checksum = (self.sub_hex2("FF", checksum[len(checksum) - 2 : len(checksum)])[2:4]).zfill(2)
            frame_local_at.append(checksum)
            frame_local_at.insert(0, self.START_BYTE) #SerialStar не поддерживает режимы с escape-символами в направлении хост->модуль, поэтому анализ на их наличие не призводится.
            #print(frame_local_at)
            tx_packet = binascii.unhexlify("".join(map(str, frame_local_at)))
            self.ser.write(tx_packet)
            time.sleep(self.API_FRAME_TX_TIMEOUT)

    ## Отправка фрейма с локальной AT-командой с немедленным применением изменений: API-фрейм 0x07.
    # @param frame_id - обязательный аргумент - идентификатор фрейма, если равен 0, то подтверждение о приеме модулем (API-фрейм 0x87) не передается. Два шестнадцатеричных символа без 0x.
    # @param at_command - обязательный аргумент, AT-команда в виде двух ASCII-символов, например "M1".
    # @param at_parameter - необязательный аргумент, параметр команды. Если аргумент не передается - команда запрашивает текущее значение параметра, если присутствует, то команда изменяет параметр.
    # Представляет собой шестнадцатеричное число в виде строки шестнадцатеричных символов без 0x. Пример "0200" для команды "M1". Число символов должно быть четным. Ведущие нули обязательны.
    def send_immidiate_apply_local_at(self, frame_id, at_command, at_parameter = ""):
        return self.send_local_at("07", frame_id, at_command, at_parameter)

    ## Отправка фрейма с локальной AT-командой с немедленным применением и сохранением изменений в энергонезависимой памяти: API-фрейм 0x08.
    # @param frame_id - обязательный аргумент - идентификатор фрейма, если равен 0, то подтверждение о приеме модулем (API-фрейм 0x88) не передается.
    # @param at_command - обязательный аргумент, AT-команда в виде ASCII-символов, например "DM".
    # @param at_parameter - необязательный аргумент, параметр команды. Если аргумент не передается - команда запрашивает текущее значение параметра, если присутствует, то команда изменяет параметр.
    # Представляет собой шестнадцатеричное число в виде строки шестнадцатеричных символов без 0x. Пример "10" для команды "DM". Число символов должно быть четным. Ведущие нули обязательны.
    def send_immidiate_apply_and_save_local_at(self, frame_id, at_command, at_parameter = ""):
        return self.send_local_at("08", frame_id, at_command, at_parameter)

    ## Отправка фрейма с локальной AT-командой с помещением параметра в очередь: API-фрейм 0x09. Применения и сохранения параметра не происходит.
    # @param frame_id - обязательный аргумент - идентификатор фрейма, если равен 0, то подтверждение о приеме модулем (API-фрейм 0x89) не передается.
    # @param at_command - обязательный аргумент, AT-команда в виде ASCII-символов, например "TX".
    # @param at_parameter - необязательный аргумент, параметр команды. Если аргумент не передается - команда запрашивает текущее значение параметра, если присутствует, то команда изменяет параметр.
    # Представляет собой шестнадцатеричное число в виде строки шестнадцатеричных символов без 0x. Пример "0010" для команды "TX". Число символов должно быть четным. Ведущие нули обязательны.
    def send_queue_local_at(self, frame_id, at_command, at_parameter = ""):
        return self.send_local_at("09", frame_id, at_command, at_parameter)

    ## Отправка фрейма с данными удаленному модулю, которые должны быть переданы им в UART: API-фреймы 0x10, 0x0F.
    # @param frame_id - обязательный аргумент - идентификатор фрейма, если равен 0, то локальное подтверждение о передаче пакета в эфир (API-фрейм 0x8B) не передается.
    # @param destination_id - обязательный аргумент, идентификатор (адрес) удаленного модуля. Состоит из 4-х шестнадцатеричных символов без префикса 0x. Пример "0234". Ведущие нули обязательны.
    # @param data - обязательный аргумент, передаваемые данные. Представляют собой строку шестнадцатеричных символов без префикса 0x. Длина не должны превышать 40 байт (80 символов), если опции передачи
    # опущены. При этом в эфир передается API-фрейм 0x0F. Если байт опций имеется, то в эфир уходит пакет 0x10. Максимальная длина длина поля данных в этом случае равна 39 байт или 78 символов.
    # Число символов должно быть четным. Если в поле data поместить символы "023476", то в UART удаленного модуля будут выданы байты 0x02, 0x34, 0x76.
    # @param options - необязательный аргумент, опции передачи. Представляет собой шестнадцатеричное число, состоящее из 2 символов без префикса 0x. Пример "10". Биты байта опций:@n
    # 0 - управление отправки подтверждения получения пакета удаленным модулем: 0 - подтверждение получения включено, 1 - выключено.@n
    # 1 - зарезервирован.@n
    # 2 - зарезервирован.@n
    # 3 - зарезервирован.@n
    # 4 - управление режимом CCA (определение занятости частотного канала перед передачей пакета в эфир): 0 - анализ занятости эфира проводится перед передачей данного пакета, 1 - CCA выключено.@n
    # 5 - управление шифрованием: 0 - данный пакет будет передан незашифрованным, 1 - шифрование включено.@n
    # 6 - управление буферизацией: 0 - данный пакет будет сразу передан в эфир, 1 - данный пакет будет предан в эфир только после получения пакета от удаленного модуля, которому этот пакет предназначен.
    # Буферизация используется для управления модулями, находящимися в спящем режиме.@n
    # 7 - зарезервирован.@n
    def send_tx_request(self, frame_id, destination_id, data, options = ""):
        frame_tx_request = []
        if options == "":
            ll = 4 + len(data) // 2
        else:
            ll = 5 + len(data) // 2
        length = str(format(ll,"04x"))
        frame_tx_request.append(length[0:2])
        frame_tx_request.append(length[2:4])
        if options == "":
            frame_tx_request.append("0F")
        else:
            frame_tx_request.append("10")
        frame_tx_request.append(frame_id)
        frame_tx_request.append(destination_id[0:2])
        frame_tx_request.append(destination_id[2:4])
        if options != "":
            frame_tx_request.append(options)
        for i in range(0, len(data), 2):
                pp = data.upper()[i:i + 2]
                frame_tx_request.append(pp)
        checksum = "00"
        for i in range(2, len(frame_tx_request)):  #При подсчете контрольной суммы байты с длиной фрейма не учитываются.
            checksum = self.add_hex2(frame_tx_request[i], checksum)
        checksum = (self.sub_hex2("FF", checksum[len(checksum) - 2 : len(checksum)])[2:4]).zfill(2)
        frame_tx_request.append(checksum)
        frame_tx_request.insert(0, self.START_BYTE) #SerialStar не поддерживает режимы с escape-символами в направлении хост->модуль, поэтому анализ на их наличие не призводится.
        tx_packet = binascii.unhexlify("".join(map(str, frame_tx_request)))
        self.ser.write(tx_packet)
        time.sleep(self.API_FRAME_TX_TIMEOUT)

    ## Отправка фрейма с AT-командой удаленному модулю: API-фрейм 0x17.
    # @param frame_id - обязательный аргумент - идентификатор фрейма, если равен 0, то локальное подтверждение о передаче пакета в эфир (API-фрейм 0x8B) не передается.
    # @param destination_id - обязательный аргумент, идентификатор (адрес) удаленного модуля. Состоит из 4-х шестнадцатеричных символов без префикса 0x. Пример "0234". Ведущие нули обязательны.
    # @param options - обязательный аргумент, опции передачи. Представляет собой шестнадцатеричное число, состоящее из 2 символов без префикса 0x. Пример "01". Биты байта опций:@n
    # 0 - управление отправкой ответа на команду удаленным модулем: 0 - ответ будет отправлен, 1 - ответ не требуется.@n
    # 1,2 - управление применением и сохранением параметра команды: 00 - параметр помещается в буфер удаленного модуля, 01 - применение и сохранение нового значения параметра в энергонезависимой памяти
    # удаленного модуля, 10 и 11 - применение параметра без сохранения его значения в энергонезависимой памяти.@n
    # 3 - зарезервирован.@n
    # 4 - управление режимом CCA (определение занятости частотного канала перед передачей пакета в эфир): 0 - анализ занятости эфира проводится перед передачей данного пакета, 1 - CCA выключено.@n
    # 5 - управление шифрованием: 0 - данный пакет будет передан незашифрованным, 1 - шифрование включено.@n
    # 6 - управление буферизацией: 0 - данный пакет будет сразу передан в эфир, 1 - данный пакет будет предан в эфир только после получения пакета от удаленного модуля, которому этот пакет предназначен.
    # Буферизация используется для управления модулями, находящимися в спящем режиме.@n
    # 7 - зарезервирован.@n
    # @param at_command - обязательный аргумент, AT-команда в виде ASCII-символов, например "TX".
    # @param at_parameter - необязательный аргумент, параметр команды. Если аргумент не передается - команда запрашивает текущее значение параметра, если присутствует, то команда изменяет параметр.
    # Представляет собой шестнадцатеричное число в виде строки без символов 0x. Пример "0210" для команды "TX". Число символов должно быть четным. Ведущие нули обязательны.
    def send_remote_at(self, frame_id, destination_id, options, at_command, at_parameter = ""):
        if len(at_command) != 2:
            return  "Error : verify the Command AT !!!!"
        else:
            frame_at = []
            ll = 7 + len(at_parameter) // 2
            length = str(format(ll,"04x"))
            frame_at.append(length[0:2])
            frame_at.append(length[2:4])
            frame_at.append("17")
            frame_at.append(frame_id)
            frame_at.append(destination_id[0:2])
            frame_at.append(destination_id[2:4])
            frame_at.append(options)
            frame_at.append(self.toHex(bytes(at_command.upper(), encoding = "ascii"))[0:2])
            frame_at.append(self.toHex(bytes(at_command.upper(), encoding = "ascii"))[2:4])
            if len(at_parameter) > 0:
                for i in range(0, len(at_parameter), 2):
                    pp = at_parameter.upper()[i:i + 2]
                    frame_at.append(pp)
            checksum = "00"
            for i in range(2, len(frame_at)):
                checksum = self.add_hex2(frame_at[i], checksum)
            checksum = (self.sub_hex2("FF", checksum[len(checksum) - 2 : len(checksum)])[2:4]).zfill(2)
            frame_at.append(checksum)
            frame_at.insert(0, self.START_BYTE)
            tx_packet = binascii.unhexlify("".join(map(str, frame_at)))
            self.ser.write(tx_packet)
            time.sleep(self.API_FRAME_TX_TIMEOUT)

    def get_frame_common_fields(self):
        ss = "".join(map(str, self.fields))
        self.frame["DELIMITER"] = ss[0:2]
        self.frame["LENGTH"] = int(ss[2:6], 16)
        self.frame["FRAME_TYPE"] = ss[6:8]
        return ss

    ## Получение фрейма с данными от удаленного модуля, переданными с байтом опций: API-фрейм 0x81.
    # Данная функция применяется для опроса приемного буфера последовательного порта и поиска в нем фрейма 0x81. Поиск осуществляется до первого найденного фрейма данного типа. При этом все прочие пакеты,
    # принятые до первого пакета 0x10 теряются. Делается ограниченное число попыток получения данного типа фрейма. Число попыток регулируется константой LOCAL_RESPONSE_RETRY_COUNT и равно
    # по-умолчанию 1. Функция обычно применяется, если опрос модуля осуществляется из основного скрипта периодической проверкой, а не с помощью callback-функций.
    # @return В случае успешного приема пакета словарь (dictionary) следующего вида:@n
    # ["DELIMITER"]: "7E" - стартовый байт фрейма.@n
    # ["LENGTH"]: xx - длина пакета  в байтах между полями length и checksum (то есть всегда на 4 байта меньше, чем полная длина принятого пакета). Десятичное число.@n
    # ["FRAME_TYPE"]: "xx" - "81" тип фрейма.@n
    # ["SOURCE_ADDRESS_DEC"]: "xxxxx" - адрес отправителя в виде строки десятичных символов.@n
    # ["SOURCE_ADDRESS_HEX"]: "xxxx" - адрес отправителя в виде строки шестнадцатеричных символов без префикса 0x.@n
    # ["RSSI"]: xxxx - уровень RSSI в dBm на входе приемника при получении данного пакета в виде десятичного числа со знаком.@n
    # ['OPTIONS']: "xx" - опции. Два шестнадцатеричных символа без 0x. Биты байта опций:@n
    # 0 - информация о требовании отправителем подтверждения о приеме пакета: 0 - подтверждение требовалось, 1 - подтверждение не требовалось.@n
    # 1 - информация о режиме отправки пакета: 0 - пакет передавался в адресном режиме, 1 - пакет передавался с широковещательным адресом.@n
    # 2 - зарезервирован.@n
    # 3 - зарезервирован.@n
    # 4 - зарезервирован.@n
    # 5 - зарезервирован.@n
    # 6 - зарезервирован.@n
    # 7 - зарезервирован.@n
    # ['DATA']: "xxx...x" - данные в виде строки шестнадцатеричных символов без префикса 0x.@n
    # ["CHECKSUM"]: "xx" - контрольная сумма. Два шестнадцатеричных символа без 0x.@n
    # Если пакета данного типа в буфере не обнаружено, то возвращается пустой словарь.
    def get_tx_request(self):
        self.frame = {}
        for i in range(0, self.LOCAL_RESPONSE_RETRY_COUNT):
            response = self.read_rx_api("81")
            if not "ERROR" in response:
                self.filter_frame()
                self.export_81_8F_frame(self.get_frame_common_fields())
                break
        return self.frame

    ## Получение фрейма с данными от удаленного модуля, переданными без байта опций: API-фрейм 0x8F.
    # Данная функция применяется для опроса приемного буфера последовательного порта и поиска в нем фрейма 0x8F. Поиск осуществляется до первого найденного фрейма данного типа. При этом все прочие пакеты,
    # принятые до первого пакета 0x8F теряются. Делается ограниченное число попыток получения данного типа фрейма. Число попыток регулируется константой LOCAL_RESPONSE_RETRY_COUNT и равно
    # по-умолчанию 1. Функция обычно применяется, если опрос модуля осуществляется из основного скрипта периодической проверкой, а не с помощью callback-функций.
    # @return В случае успешного приема пакета словарь (dictionary) следующего вида:@n
    # ["DELIMITER"]: "7E" - стартовый байт фрейма.@n
    # ["LENGTH"]: xx - длина пакета в байтах между полями length и checksum (то есть всегда на 4 байта меньше, чем полная длина принятого пакета). Десятичное число.@n
    # ["FRAME_TYPE"]: "xx" - "81" тип фрейма.@n
    # ["SOURCE_ADDRESS_DEC"]: "xxxxx" - адрес отправителя в виде строки десятичных символов.@n
    # ["SOURCE_ADDRESS_HEX"]: "xxxx" - адрес отправителя в виде строки шестнадцатеричных символов без префикса 0x.@n
    # ["RSSI"]: xxxx - уровень RSSI в dBm на входе приемника при получении данного пакета в виде десятичного числа со знаком.@n
    # ['OPTIONS']: "xx" - опции. Два шестнадцатеричных символа без 0x. Биты байта опций:@n
    # 0 - зарезервирован.@n
    # 1 - информация о режиме отправки пакета: 0 - пакет передавался в адресном режиме, 1 - пакет передавался с широковещательным адресом.@n
    # 2 - зарезервирован.@n
    # 3 - зарезервирован.@n
    # 4 - зарезервирован.@n
    # 5 - зарезервирован.@n
    # 6 - зарезервирован.@n
    # 7 - зарезервирован.@n
    # ['DATA']: "xxx...x" - данные в виде строки шестнадцатеричных символов без префикса 0x.@n
    # ["CHECKSUM"]: "xx" - контрольная сумма. Два шестнадцатеричных символа без 0x.@n
    # Если пакета данного типа в буфере не обнаружено, то возвращается пустой словарь.
    def get_tx_request_without_option(self):
        self.frame = {}
        for i in range(0, self.LOCAL_RESPONSE_RETRY_COUNT):
            response = self.read_rx_api("8F")
            if not "ERROR" in response:
                self.filter_frame()
                self.export_81_8F_frame(self.get_frame_common_fields())
                break
        return self.frame

    def export_81_8F_frame(self, ss):
        self.frame["SOURCE_ADDRESS_DEC"] = str(int(ss[8:12], 16)).zfill(5)
        self.frame["SOURCE_ADDRESS_HEX"] = ss[8:12]
        self.frame["RSSI"] = int(ss[12:14], 16) - 256
        self.frame['OPTIONS'] = ss[14:16]
        self.frame['DATA'] = ss[16:len(ss) - 2]
        self.frame["CHECKSUM"] = ss[len(ss) - 2 : len(ss)]
        return self.frame

    ## Получение фрейма, подтверждающего прием пакета с локальной AT-командой с немедленным применением изменений: API-фрейм 0x87.
    # Данная функция применяется для опроса приемного буфера последовательного порта и поиска в нем фрейма 0x87. Поиск осуществляется до первого найденного фрейма данного типа. При этом все прочие пакеты,
    # принятые до первого пакета 0x87 теряются. Делается ограниченное число попыток получения данного типа фрейма. Число попыток регулируется константой LOCAL_RESPONSE_RETRY_COUNT и равно
    # по-умолчанию 1. Функция обычно применяется, если опрос модуля осуществляется из основного скрипта периодической проверкой, а не с помощью callback-функций.
    # @return В случае успешного приема пакета словарь (dictionary) следующего вида:@n
    # ["DELIMITER"]: "7E" - стартовый байт фрейма.@n
    # ["LENGTH"]: xx - длина пакета в байтах между полями length и checksum (то есть всегда на 4 байта меньше, чем полная длина принятого пакета). Десятичное число.@n
    # ["FRAME_TYPE"]: "xx" - "87" тип фрейма.@n
    # ["FRAME_ID"]: "xx" - идентификатор фрейма. Равен идентификатору фрейма 0x07 ответом на который он является. Два шестнадцатеричных символа без 0x.@n
    # ["AT_COMMAND"]: "xx" - AT-команда в виде двух ASCII-символов.
    # ["STATUS"]: "xx" - статус команды. "00" - команда выполнена, "01" - недостаточно памяти для выполнения команды, "02" - недопустимая команда, "03" - недопустимое значение параметра.@n
    # ["AT_PARAMETER"]: "xx..x" - параметр команды в виде строки шестнадцатеричных символов без префикса 0x. Если команда записывала данные, то значением этого ключа является пустая строка.
    # ["CHECKSUM"]: "xx" - контрольная сумма. Два шестнадцатеричных символа без 0x.@n
    # Если пакета данного типа в буфере не обнаружено, то возвращается пустой словарь.
    def get_immidiate_apply_local_at_response(self):
        self.frame = {}
        for i in range(0, self.LOCAL_RESPONSE_RETRY_COUNT):
            response = self.read_rx_api("87")
            if not "ERROR" in response:
                self.filter_frame()
                self.export_87_88_89_frame(self.get_frame_common_fields())
                break
        return self.frame

    ## Получение фрейма, подтверждающего прием пакета с локальной AT-командой с немедленным применением и сохраненим изменений: API-фрейм 0x88.
    # Данная функция применяется для опроса приемного буфера последовательного порта и поиска в нем фрейма 0x88. Поиск осуществляется до первого найденного фрейма данного типа. При этом все прочие пакеты,
    # принятые до первого пакета 0x88 теряются. Делается делается ограниченное число попыток получения данного типа фрейма. Число попыток регулируется константой LOCAL_RESPONSE_RETRY_COUNT и равно
    # по-умолчанию 1. Функция обычно применяется, если опрос модуля осуществляется из основного скрипта периодической проверкой, а не с помощью callback-функций.
    # @return В случае успешного приема пакета словарь (dictionary) следующего вида:@n
    # ["DELIMITER"]: "7E" - стартовый байт фрейма.@n
    # ["LENGTH"]: xx - длина пакета в байтах между полями length и checksum (то есть всегда на 4 байта меньше, чем полная длина принятого пакета). Десятичное число.@n
    # ["FRAME_TYPE"]: "xx" - "88" тип фрейма.@n
    # ["FRAME_ID"]: "xx" - идентификатор фрейма. Равен идентификатору фрейма 0x08 ответом на который он является. Два шестнадцатеричных символа без 0x.@n
    # ["AT_COMMAND"]: "xx" - AT-команда в виде двух ASCII-символов.
    # ["STATUS"]: "xx" - статус команды. "00" - команда выполнена, "01" - недостаточно памяти для выполнения команды, "02" - недопустимая команда, "03" - недопустимое значение параметра.@n
    # ["AT_PARAMETER"]: "xx..x" - параметр команды в виде строки шестнадцатеричных символов без префикса 0x. Если команда записывала данные, то значением этого ключа является пустая строка.
    # ["CHECKSUM"]: "xx" - контрольная сумма. Два шестнадцатеричных символа без 0x.@n
    # Если пакета данного типа в буфере не обнаружено, то возвращается пустой словарь.
    def get_immidiate_apply_and_save_local_at_response(self):
        self.frame = {}
        for i in range(0, self.LOCAL_RESPONSE_RETRY_COUNT):
            response = self.read_rx_api("88")
            if not "ERROR" in response:
                self.filter_frame()
                self.export_87_88_89_frame(self.get_frame_common_fields())
                break
        return self.frame

    ## Получение фрейма, подтверждающего прием пакета с локальной AT-командой и помещением параметра в очередь: API-фрейм 0x89.
    # Данная функция применяется для опроса приемного буфера последовательного порта и поиска в нем фрейма 0x89. Поиск осуществляется до первого найденного фрейма данного типа. При этом все прочие пакеты,
    # принятые до первого пакета 0x89 теряются. Делается ограниченное число попыток получения данного типа фрейма. Число попыток регулируется константой LOCAL_RESPONSE_RETRY_COUNT и равно
    # по-умолчанию 1. Функция обычно применяется, если опрос модуля осуществляется из основного скрипта периодической проверкой, а не с помощью callback-функций.
    # @return В случае успешного приема пакета словарь (dictionary) следующего вида:@n
    # ["DELIMITER"]: "7E" - стартовый байт фрейма.@n
    # ["LENGTH"]: xx - длина пакета в байтах между полями length и checksum (то есть всегда на 4 байта меньше, чем полная длина принятого пакета). Десятичное число.@n
    # ["FRAME_TYPE"]: "xx" - "89" тип фрейма.@n
    # ["FRAME_ID"]: "xx" - идентификатор фрейма. Равен идентификатору фрейма 0x09 ответом на который он является. Два шестнадцатеричных символа без 0x.@n
    # ["AT_COMMAND"]: "xx" - AT-команда в виде двух ASCII-символов.
    # ["STATUS"]: "xx" - статус команды. "00" - команда выполнена, "01" - недостаточно памяти для выполнения команды, "02" - недопустимая команда, "03" - недопустимое значение параметра.@n
    # ["AT_PARAMETER"]: "xx..x" - параметр команды в виде строки шестнадцатеричных символов без префикса 0x. Если команда записывала данные, то значением этого ключа является пустая строка.
    # ["CHECKSUM"]: "xx" - контрольная сумма. Два шестнадцатеричных символа без 0x.@n
    # Если пакета данного типа в буфере не обнаружено, то возвращается пустой словарь.
    def get_queue_local_at_response(self):
        self.frame = {}
        for i in range(0, self.LOCAL_RESPONSE_RETRY_COUNT):
            response = self.read_rx_api("89")
            if not "ERROR" in response:
                self.filter_frame()
                self.export_87_88_89_frame(self.get_frame_common_fields())
                break
        return self.frame

    def export_87_88_89_frame(self, ss):
        self.frame["FRAME_ID"] = ss[8:10]
        self.frame["AT_COMMAND"] = binascii.unhexlify(ss[10:14]).decode("ascii")
        self.frame["STATUS"] = ss[14:16]
        if len(ss) - 2 == 0:
            self.frame["AT_PARAMETER_HEX"] = []
            self.frame["AT_PARAMETER"] = []
        else:
            self.frame["AT_PARAMETER_HEX"] = ss[16:len(ss) - 2]
            self.frame["AT_PARAMETER"] = binascii.unhexlify(ss[16:len(ss) - 2])
        self.frame["CHECKSUM"] = ss[len(ss) - 2 : len(ss)]
        return self.frame

    ## Получение фрейма со статусом модуля, отправляемого им при рестарте: API-фрейм 0x8A.
    # Данная функция применяется для опроса приемного буфера последовательного порта и поиска в нем фрейма 0x8A. Поиск осуществляется до первого найденного фрейма данного типа. При этом все прочие пакеты,
    # принятые до первого пакета 0x8A теряются. Делается ограниченное число попыток получения данного типа фрейма. Число попыток регулируется константой LOCAL_RESPONSE_RETRY_COUNT и равно
    # по-умолчанию 1. Функция обычно применяется, если опрос модуля осуществляется из основного скрипта периодической проверкой, а не с помощью callback-функций.
    # @return В случае успешного приема пакета словарь (dictionary) следующего вида:@n
    # ["DELIMITER"]: "7E" - стартовый байт фрейма.@n
    # ["LENGTH"]: 2 - длина пакета в байтах между полями length и checksum.@n
    # ["FRAME_TYPE"]: "xx" - "8A" тип фрейма.@n
    # ["STATUS"]: "xx" - статус команды. "00" - рестарт модуля произошел вследствие включения питания, "01" - программный рестарт или активация входа RESET.@n
    # ["CHECKSUM"]: "xx" - контрольная сумма. Два шестнадцатеричных символа без 0x.@n
    # Если пакета данного типа в буфере не обнаружено, то возвращается пустой словарь.
    def get_modem_status(self):
        self.frame = {}
        for i in range(0, self.LOCAL_RESPONSE_RETRY_COUNT):
            response = self.read_rx_api("8A")
            if not "ERROR" in response:
                self.filter_frame()
                self.export_8A_frame(self.get_frame_common_fields())
                break
        return self.frame

    def export_8A_frame(self, ss):
        self.frame["STATUS"] = ss[8:10]
        self.frame["CHECKSUM"] = ss[10:12] #Этот пакет имеет фиксированную длину, поэтому контрольная сумма всегда на одном и том же месте.
        return self.frame

    ## Получение фрейма со статусом отправки пакета, предназначенного для передачи в эфир: API-фрейм 0x8B.
    # Данная функция применяется для опроса приемного буфера последовательного порта и поиска в нем фрейма 0x8B. Поиск осуществляется до первого найденного фрейма данного типа. При этом все прочие пакеты,
    # принятые до первого пакета 0x8B теряются. Делается ограниченное число попыток получения данного типа фрейма. Число попыток регулируется константой LOCAL_TX_STATUS_RETRY_COUNT и равно
    # по-умолчанию 1. Функция обычно применяется, если опрос модуля осуществляется из основного скрипта периодической проверкой, а не с помощью callback-функций.
    # @return В случае успешного приема пакета словарь (dictionary) следующего вида:@n
    # ["DELIMITER"]: "7E" - стартовый байт фрейма.@n
    # ["LENGTH"]: 7 - длина пакета в байтах между полями length и checksum.@n
    # ["FRAME_TYPE"]: "xx" - "8B" тип фрейма.@n
    # ["FRAME_ID"]: "xx" - идентификатор фрейма. Равен идентификатору фрейма ответом на который он является. Два шестнадцатеричных символа без 0x.@n
    # ["DESTINATION_ADDRESS_DEC"]: "xxxxx" - адрес получателя в виде строки десятичных символов.@n
    # ["DESTINATION_ADDRESS_HEX"]: "xxxx" - адрес получателя в виде строки шестнадцатеричных символов без префикса 0x.@n
    # ["TX_RETRY_COUNT"]: x - число попыток, сделанных при отправке пакета в эфир. Ресятичное число.@n
    # ["STATUS"]: "xx" - статус отправки. "00" - пакет отправлен, "01" - недостаточно памяти размещения пакета в памяти, "02" - недопустимая команда, "03" - недопустимое значение параметра, "04" - пакет в эфир
    # не отправлен по причине занятости частотного канала.@n
    # ["RESERVE"]: "00" - зарезеривровано.@n
    # ["CHECKSUM"]: "xx" - контрольная сумма. Два шестнадцатеричных символа без 0x.@n
    # Если пакета данного типа в буфере не обнаружено, то возвращается пустой словарь.
    def get_local_tx_status(self):
        self.frame = {}
        for i in range(0, self.LOCAL_TX_STATUS_RETRY_COUNT):
            response = self.read_rx_api("8B")
            if not "ERROR" in response:
                self.filter_frame()
                self.export_8B_frame(self.get_frame_common_fields())
                break
        return self.frame

    def export_8B_frame(self, ss):
        self.frame["FRAME_ID"] = ss[8:10]
        self.frame["DESTINATION_ADDRESS_DEC"] = str(int(ss[10:14], 16)).zfill(5)
        self.frame["DESTINATION_ADDRESS_HEX"] = ss[10:14]
        self.frame["TX_RETRY_COUNT"] = int(ss[14:16], 16)
        self.frame["STATUS"] = ss[16:18]
        self.frame["RESERVE"] = ss[18:20]
        self.frame["CHECKSUM"] = ss[20:22] #Этот пакет имеет фиксированную длину, поэтому контрольная сумма всегда на одном и том же месте.
        return self.frame

    ## Получение фрейма с подтверждением доставки пакета с данными удаленному модулю: API-фрейм 0x8C.
    # Данная функция применяется для опроса приемного буфера последовательного порта и поиска в нем фрейма 0x8C. Поиск осуществляется до первого найденного фрейма данного типа. При этом все прочие пакеты,
    # принятые до первого пакета 0x8C теряются. Делается ограниченное число попыток получения данного типа фрейма. Число попыток регулируется константой REMOTE_RX_STATUS_RETRY_COUNT и равно
    # по-умолчанию 1. Функция обычно применяется, если опрос модуля осуществляется из основного скрипта периодической проверкой, а не с помощью callback-функций.
    # @return В случае успешного приема пакета словарь (dictionary) следующего вида:@n
    # ["DELIMITER"]: "7E" - стартовый байт фрейма.@n
    # ["LENGTH"]: 6 - длина пакета в байтах между полями length и checksum.@n
    # ["FRAME_TYPE"]: "xx" - "8С" тип фрейма.@n
    # ["SOURCE_ADDRESS_DEC"]: "xxxxx" - адрес отправителя подтверждения в виде строки десятичных символов.@n
    # ["SOURCE_ADDRESS_HEX"]: "xxxx" - адрес отправителя подтверждения в виде строки шестнадцатеричных символов без префикса 0x.@n
    # ["RSSI"]: xxxx - уровень RSSI в dBm на входе приемника при получении данного пакета в виде десятичного числа со знаком.@n
    # ["OPTIONS"]: "00" - опции передачи. В текущей версии поле зарезервировано.@n
    # ["FRAME_ID"]: "xx" - идентификатор фрейма. Равен идентификатору фрейма ответом на который он является. Два шестнадцатеричных символа без 0x.@n
    # ["CHECKSUM"]: "xx" - контрольная сумма. Два шестнадцатеричных символа без 0x.@n
    # Если пакета данного типа в буфере не обнаружено, то возвращается пустой словарь.
    def get_remote_tx_status(self):
        self.frame = {}
        for i in range(0, self.REMOTE_RX_STATUS_RETRY_COUNT):
            response = self.read_rx_api("8C")
            if not "ERROR" in response:
                self.filter_frame()
                self.export_8C_frame(self.get_frame_common_fields())
                break
        return self.frame

    def export_8C_frame(self, ss):
        self.frame["SOURCE_ADDRESS_DEC"] = str(int(ss[8:12], 16)).zfill(5)
        self.frame["SOURCE_ADDRESS_HEX"] = ss[8:12]
        self.frame["RSSI"] = int(ss[12:14], 16) - 256
        self.frame["OPTIONS"] = ss[14:16]
        self.frame['FRAME_ID'] = ss[16:18]
        self.frame["CHECKSUM"] = ss[18:20] #Этот пакет имеет фиксированную длину, поэтому контрольная сумма всегда на одном и том же месте.
        return self.frame

    ## Получение фрейма с ответом от удаленного модуля на отправленную ему AT-команду: API-фрейм 0x97.
    # Данная функция применяется для опроса приемного буфера последовательного порта и поиска в нем фрейма 0x97. Поиск осуществляется до первого найденного фрейма данного типа. При этом все прочие пакеты,
    # принятые до первого пакета 0x97 теряются. Делается ограниченное число попыток получения данного типа фрейма. Число попыток регулируется константой REMOTE_RX_STATUS_RETRY_COUNT и равно
    # по-умолчанию 1. Функция обычно применяется, если опрос модуля осуществляется из основного скрипта периодической проверкой, а не с помощью callback-функций.
    # @return В случае успешного приема пакета словарь (dictionary) следующего вида:@n
    # ["DELIMITER"]: "7E" - стартовый байт фрейма.@n
    # ["LENGTH"]: xx - длина пакета в байтах между полями length и checksum.@n
    # ["FRAME_TYPE"]: "xx" - "97" тип фрейма.@n
    # ["SOURCE_ADDRESS_DEC"]: "xxxxx" - адрес отправителя пакета в виде строки десятичных символов.@n
    # ["SOURCE_ADDRESS_HEX"]: "xxxx" - адрес отправителя пакета в виде строки шестнадцатеричных символов без префикса 0x.@n
    # ["RSSI"]: xxxx - уровень RSSI в dBm на входе приемника при получении данного пакета в виде десятичного числа со знаком.@n
    # ["OPTIONS"]: "00" - опции. В текущей версии поле зарезервировано.@n
    # ["AT_COMMAND"]: "xx" - AT-команда в виде двух ASCII-символов.@n
    # ["STATUS"]: "00" - статус команды. В текущей версии поле зарезервировано.@n
    # ["AT_PARAMETER"]: "xx..x" - параметр команды в виде строки шестнадцатеричных символов без префикса 0x. Если команда записывала данные, то значением этого ключа является пустая строка.@n
    # ["CHECKSUM"]: "xx" - контрольная сумма. Два шестнадцатеричных символа без 0x.@n
    # Если пакета данного типа в буфере не обнаружено, то возвращается пустой словарь.
    def get_remote_at_command_response(self): #Getting remote AT-command delivery status API-frame(Frame type 0x97).
        self.frame = {}
        for i in range(0, self.REMOTE_RX_STATUS_RETRY_COUNT):
            response = self.read_rx_api("97")
            if not "ERROR" in response:
                self.filter_frame()
                self.export_97_frame(self.get_frame_common_fields())
                break
        return self.frame

    def export_97_frame(self, ss):
        self.frame["SOURCE_ADDRESS_DEC"] = str(int(ss[8:12], 16)).zfill(5)
        self.frame["SOURCE_ADDRESS_HEX"] = ss[8:12]
        self.frame["RSSI"] = int(ss[12:14], 16) - 256
        self.frame["OPTIONS"] = ss[14:16]
        self.frame["AT_COMMAND"] = binascii.unhexlify(ss[16:20]).decode("ascii")
        self.frame["STATUS"] = ss[20:22]
        if len(ss) - 2 == 0:
            self.frame["AT_PARAMETER_HEX"] = []
            self.frame["AT_PARAMETER"] = []
        else:
            self.frame["AT_PARAMETER_HEX"] = ss[22:len(ss) - 2]
            self.frame["AT_PARAMETER"] = binascii.unhexlify(ss[22:len(ss) - 2])
        self.frame["CHECKSUM"] = ss[len(ss) - 2 : len(ss)]
        return self.frame

    ## Получение фрейма с данными о состоянии линий ввода вывода удаленного модуля: API-фрейм 0x83.
    # Данная функция применяется для опроса приемного буфера последовательного порта и поиска в нем фрейма 0x83. Поиск осуществляется до первого найденного фрейма данного типа. При этом все прочие пакеты,
    # принятые до первого пакета 0x83 теряются. Делается ограниченное число попыток получения данного типа фрейма. Число попыток регулируется константой IO_SAMPLE_RX_RETRY_COUNT и равно
    # по-умолчанию 1. Функция обычно применяется, если опрос модуля осуществляется из основного скрипта периодической проверкой, а не с помощью callback-функций.
    # @return В случае успешного приема пакета словарь (dictionary) следующего вида:@n
    # ["DELIMITER"]: "7E" - стартовый байт фрейма.@n
    # ["LENGTH"]: xx - длина пакета в байтах между полями length и checksum.@n
    # ["FRAME_TYPE"]: "xx" - "83" тип фрейма.@n
    # ["SOURCE_ADDRESS_DEC"]: "xxxxx" - адрес отправителя пакета в виде строки десятичных символов.@n
    # ["SOURCE_ADDRESS_HEX"]: "xxxx" - адрес отправителя пакета в виде строки шестнадцатеричных символов без префикса 0x.@n
    # ["RSSI"]: xxxx - уровень RSSI в dBm на входе приемника при получении данного пакета в виде десятичного числа со знаком.@n
    # ["OPTIONS"]: "xx" - опции приема. "00" - пакет предназначался данному модулю, "01" - пакет был передан с широковещательным адресом.@n
    # ["TEMPERATURE"]: xxx - температура встроенного термодатчика модуля отправителя в градусах Цельсия, целое десятичное число со знаком.@n
    # ["VCC"]: xxxx - напряжение источника питания на модуле отправителе в вольтах. Положительное десятичное число с двумя знаками после запятой.@n
    # ["DATA_HEX"]: "xx..x" - содержимое поля данных в виде строки шестнадцатеричных символов без префикса 0x.@n
    # ["DATA_PARSED"]: {pin_number: {pin_mode: value},..} - словарь, ключами которого являются физические номера выводов модуля в виде двух шестнадцатеричных символов без 0x. В качестве значений выступает
    # также словарь, с ключом, представляющим собой номер режима ввода/вывода в виде двух шестнадцатеричных символов, например "02", если данная линия работает в режиме аналогового входа. Подробная
    # информация о доступных режимах имеется в документации по проекту SerialStar.
    # Значения словаря - это состояние линии, зависящее от ее режима. Возможные значения:@n
    # Режим 2 (ANALOG_INPUT) - "xxxx" оцифрованное значение напряжения на входе. Представляет собой четыре шестнадцатеричных символа без 0x. Значащими являются младшие 12 бит. Если число превышает
    # 4096, это означает, что напряжение на входе равно 0.@n
    # Режим 3 (DIGITAL_INPUT) - "HIGH", "LOW".@n
    # Режим 4 (DIGITAL_OUTPUT_LOW) - "HIGH", "LOW".@n
    # Режим 5 (DIGITAL_OUTPUT_LOW) - "HIGH", "LOW".@n
    # Режим 13 (COUNTER_INPUT_1) - "xxxxxxxx" текущее число подсчитанных импульсов на данном входе. Представляет собой восемь шестнадцатеричных символов без 0x.@n
    # Режим 14 (COUNTER_INPUT_2) - "xxxxxxxx" текущее число подсчитанных импульсов на данном входе. Представляет собой восемь шестнадцатеричных символов без 0x.@n
    # Режим 15 (WAKEUP_INPUT_FALLING) - "HIGH", "LOW".@n
    # Режим 16 (WAKEUP_INPUT_RISING) - "HIGH", "LOW".@n
    # ["DATA_PARSED_DECODED"]: {pin_name: {pin_mode_name: value},..} - словарь, ключами которого являются имена выводов модуля, используемые в проекте SerialStar, в виде двух ASCII-символов, например
    # физическому выводу модуля №31, будет соответствовать ключ "R4". В качестве значений выступает также словарь, с ключом, представляющим собой имя режима, так, как оно представлено в документации на
    # SerialStar, например, если линия работает в режиме аналоговом входа, то ключом словаря будет строка ASCII-символов "ANALOG_INPUT".@n
    # Значения словаря - это состояние линии, зависящее от ее режима. Возможные значения совпадают с со значениями, представленными выше при описании ключа "DATA_PARSED".@n
    # ["DATA_RAW"]: "xx..x" - поле данных в виде последовательности байт (тип данных bytearray).@n
    # ["CHECKSUM"]: "xx" - контрольная сумма. Два шестнадцатеричных символа без 0x.@n
    # Если пакета данного типа в буфере не обнаружено, то возвращается пустой словарь.
    def get_io_sample_rx(self):
        self.frame = {}
        for i in range(0, self.IO_SAMPLE_RX_RETRY_COUNT):
            response = self.read_rx_api("83")
            if not "ERROR" in response:
                self.filter_frame()
                self.export_83_frame(self.get_frame_common_fields())
                break
        return self.frame

    def export_83_frame(self, ss):
        self.frame["SOURCE_ADDRESS_DEC"] = str(int(ss[8:12], 16)).zfill(5)
        self.frame["SOURCE_ADDRESS_HEX"] = ss[8:12]
        self.frame["RSSI"] = int(ss[12:14], 16) - 256
        self.frame["OPTIONS"] = ss[14:16]
        self.frame["TEMPERATURE"] = int(ss[16:18], 16)
        self.frame["VCC"] = round(int(ss[18:20], 16) / 51, 2)
        self.frame["DATA_HEX"] = ss[20:len(ss) - 2]
        self.frame["DATA_PARSED"] = {}
        self.frame["DATA_PARSED_DECODED"] = {}
        i = 20
        while i < len(ss) - 2:
            pin_number = ss[i:i + 2]
            pin_id =  pin_number
            i += 2
            pin_mode = ss[i:i + 2]
            pin_mode_decoded = format((int(pin_mode, 16) & 0x7F), 'X').zfill(2)
            sample_length = self.GET_SAMPLE_LENGTH[pin_mode_decoded]
            i += 2
            if sample_length == 0:
                if int(pin_mode, 16) & 0x80:
                    value = "HIGH"
                else:
                    value = "LOW"
            else:
                value = ss[i:i + sample_length]
            i += sample_length
            self.frame["DATA_PARSED"][pin_id] = {pin_mode_decoded: value}
            self.frame["DATA_PARSED_DECODED"][self.PIN_ID_DECODE[pin_id]] = {self.PIN_MODE_DECODE[pin_mode_decoded]: value}
        self.frame["DATA_RAW"] = binascii.unhexlify(ss[20:len(ss) - 2])
        self.frame["CHECKSUM"] = ss[len(ss) - 2 : len(ss)]
        return self.frame

    ## Метод, осуществляющий постоянный опрос буфера последовательного порта с целью обнаружения в нем всех типов фреймов, поддерживаемых в проекте SerialStar. В случае приема любого валидного
    # пакета, метод осуществляет проверку на наличие зарегистрированной callback-функции, предназначенный для обработки данного пакета в основном скрипте. Если callback-функция для данного типа
    # фрейма зарегистирована, то осуществляется ее вызов.@n
    # Метод применяется при организации в основном скрипте взаимодействия с модулем с помощью callback-функций. Метод должен вызываться постоянно в основном цикле скрипта.
    def run(self): #Getting API-frame from UART.
        self.frame = {}
        for i in range(0, self.GET_FRAME_RETRY_COUNT):
            response = self.read_rx_api()
            if not "ERROR" in response:
                self.filter_frame()
                ss = self.get_frame_common_fields()
                if self.frame["FRAME_TYPE"] == "81" and self.on_rx_81_frame_callback:
                    self.on_rx_81_frame_callback(self.export_81_8F_frame(ss))
                elif self.frame["FRAME_TYPE"] == "83" and self.on_rx_83_frame_callback:
                    self.on_rx_83_frame_callback(self.export_83_frame(ss))
                elif self.frame["FRAME_TYPE"] == "87" and self.on_rx_87_frame_callback:
                    self.on_rx_87_frame_callback(self.export_87_88_89_frame(ss))
                elif self.frame["FRAME_TYPE"] == "88" and self.on_rx_88_frame_callback:
                    self.on_rx_88_frame_callback(self.export_87_88_89_frame(ss))
                elif self.frame["FRAME_TYPE"] == "89" and self.on_rx_89_frame_callback:
                    self.on_rx_89_frame_callback(self.export_87_88_89_frame(ss))
                elif self.frame["FRAME_TYPE"] == "8A" and self.on_rx_8A_frame_callback:
                    self.on_rx_8A_frame_callback(self.export_8A_frame(ss))
                elif self.frame["FRAME_TYPE"] == "8B" and self.on_rx_8B_frame_callback:
                    self.on_rx_8B_frame_callback(self.export_8B_frame(ss))
                elif self.frame["FRAME_TYPE"] == "8C" and self.on_rx_8C_frame_callback:
                    self.on_rx_8C_frame_callback(self.export_8C_frame(ss))
                elif self.frame["FRAME_TYPE"] == "8F" and self.on_rx_8F_frame_callback:
                    self.on_rx_8F_frame_callback(self.export_81_8F_frame(ss))
                elif self.frame["FRAME_TYPE"] == "97" and self.on_rx_97_frame_callback:
                    self.on_rx_97_frame_callback(self.export_97_frame(ss))
                else:
                    #print(self.frame)
                    pass
                break
        return self.frame
