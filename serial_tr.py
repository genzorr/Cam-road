import serial
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot

ACCUM_LEN = 1

class MsgAccumulator:
    def __init__(self, batch_size, signal):
        self.batch_size = batch_size
        self.signal = signal
        self.accumulator = []

    def push_message(self, msg):
        self.accumulator.append(msg)
        if len(self.accumulator) >= self.batch_size:
            self.signal.emit(self.accumulator)
            self.accumulator = []
            # print('PUSH COMPLETED')


class WatcherThread(QThread):


    def __init__(self, speed=9600):
        QThread.__init__(self)
        self.device = serial_init(speed)


    def run(self):
        while True and self.device:
            data = serial_recv(self.device)

            if data:
                data = int(data)
                self.data_signal.emit(data)
                print(data)


def serial_init(speed):
    try:
        dev = serial.Serial(
        # Здесь указывается устройство, с которым будет производится работа
        port='/dev/ttyUSB0',
        # Скорость передачи
        baudrate=speed,
        # Использование бита четности
        parity=serial.PARITY_NONE,
        # Длина стоп-бита
        stopbits=serial.STOPBITS_ONE,
        # Длина пакета
        bytesize=serial.EIGHTBITS,
        # Максимальное время ожидания устройства
        timeout=0.1
    )
    except serial.serialutil.SerialException:
        dev = None

    return dev

def serial_recv(dev):
    # Для простоты макс. кол-во символов для чтения - 255. Время ожидания - 0.1
    # decode необходим для конвертирования набора полученных байтов в строку
    string = dev.read(255).decode()
    return string

def serial_send(dev, string):
    # encode конвертирует строку в кодировке utf-8 в набор байтов
    dev.write(string.encode('utf-8'))