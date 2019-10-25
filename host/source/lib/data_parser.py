import struct, time
from .data_classes import *

DESCR1 = struct.pack('B', 0x7e)
DESCR2 = struct.pack('B', 0xa5)

#----------------------------------------------------------------------------------------------#
def encrypt_package(package):
    data = bytes()
    data += DESCR1
    data += DESCR2
    data += int_to_bytes(package.type)

    if package.type == 1:
        data += float_to_bytes(package.acceleration)
        data += float_to_bytes(package.braking)
        data += float_to_bytes(package.velocity)
        data += int_to_bytes(package.mode)
        data += int_to_bytes(package.direction)
        data += int_to_bytes(package.set_base)
        package.crc = package.acceleration + package.braking + package.velocity + \
                      package.mode + package.direction + package.set_base
        data += float_to_bytes(package.crc)

    elif package.type == 2:
        data += int_to_bytes(package.mode)
        data += float_to_bytes(package.coordinate)
        data += float_to_bytes(package.RSSI)
        data += float_to_bytes(package.voltage)
        data += float_to_bytes(package.current)
        data += float_to_bytes(package.temperature)
        data += float_to_bytes(package.base1)
        data += float_to_bytes(package.base2)
        package.crc = package.mode + package.coordinate + package.RSSI + \
                      package.voltage + package.current + package.temperature + \
                      package.base1 + package.base2
        data += float_to_bytes(package.crc)

    elif package.type == 3:
        data += int_to_bytes(package.direction)
        data += bool_to_bytes(package.soft_stop)
        data += bool_to_bytes(package.end_points)
        data += bool_to_bytes(package.end_points_stop)
        data += bool_to_bytes(package.end_points_reverse)
        data += bool_to_bytes(package.sound_stop)
        data += bool_to_bytes(package.swap_direction)
        data += bool_to_bytes(package.accelerometer_stop)
        data += bool_to_bytes(package.HARD_STOP)
        data += bool_to_bytes(package.lock_buttons)
        package.crc = package.direction + package.soft_stop + package.end_points + \
                      package.end_points_stop + package.end_points_reverse + package.sound_stop + \
                      package.swap_direction + package.accelerometer_stop + package.HARD_STOP + package.lock_buttons
        data += int_to_bytes(package.crc)

    else:
        return None

    return data

def get_decrypt_package(dev_read):
    try:
        curr_time = time.time()
        while True:
            if (time.time() - curr_time > 1):
                return None

            descr1 = dev_read.read(1)
            descr2 = dev_read.read(1)
            # print('got: ', descr1, descr2)

            if descr1 != DESCR1 and descr2 != DESCR2:
                if descr2 == DESCR1:
                    descr1 = DESCR1
                    descr2 = dev_read.read(1)

                    if descr2 == DESCR2:
                        break

                # print('Bad index', descr1, descr2)
            else: break

        crc = 0
        type = bytes_to_int(dev_read.read(4))

        if type == 1:
            package = HTRData()
            package.type = 1

            data = dev_read.read(package.size)
            if len(data) < package.size:
                return None

            package.acceleration = bytes_to_float(data[0:4])
            package.braking = bytes_to_float(data[4:8])
            package.velocity = bytes_to_float(data[8:12])
            package.mode = bytes_to_int(data[12:16])
            package.direction = bytes_to_int(data[16:20])
            package.set_base = bytes_to_int(data[20:24])
            crc = package.acceleration + package.braking + package.velocity + \
                    package.mode + package.direction + package.set_base
            package.crc = bytes_to_float(data[24:28])
            if package.crc != crc:
                print('Bad crc 1')
                return None

        elif type == 2:
            package = RTHData()
            package.type = 2

            data = dev_read.read(package.size)
            if len(data) < package.size:
                return None

            package.mode = bytes_to_int(data[0:4])
            package.coordinate = bytes_to_float(data[4:8])
            package.RSSI = bytes_to_float(data[8:12])
            package.voltage = bytes_to_float(data[12:16])
            package.current = bytes_to_float(data[16:20])
            package.temperature = bytes_to_float(data[20:24])
            package.base1 = bytes_to_float(data[24:28])
            package.base2 = bytes_to_float(data[28:32])
            crc = package.mode + package.coordinate + package.RSSI + \
                  package.voltage + package.current + package.temperature + \
                  package.base1 + package.base2
            package.crc = bytes_to_float(data[32:36])
            if package.crc != crc:
                print('Bad crc 2')
                return None

        elif type == 3:
            package = HBData()
            package.type = 3

            data = dev_read.read(package.size)
            if len(data) < package.size:
                return None

            package.direction = bytes_to_int(data[0:4])
            package.soft_stop = bytes_to_bool(data[4:5])
            package.end_points = bytes_to_bool(data[5:6])
            package.end_points_stop = bytes_to_bool(data[6:7])
            package.end_points_reverse = bytes_to_bool(data[7:8])
            package.sound_stop = bytes_to_bool(data[8:9])
            package.swap_direction = bytes_to_bool(data[9:10])
            package.accelerometer_stop = bytes_to_bool(data[10:11])
            package.HARD_STOP = bytes_to_bool(data[11:12])
            package.lock_buttons = bytes_to_bool(data[12:13])
            crc = package.direction + package.soft_stop + package.end_points + \
                  package.end_points_stop + package.end_points_reverse + package.sound_stop + \
                  package.swap_direction + package.accelerometer_stop + package.HARD_STOP + package.lock_buttons
            package.crc = bytes_to_int(data[13:17])
            if package.crc != crc:
                print('Bad crc 3')
                return None
        else:
            print('error: no such package')
            return None

        return package

    except ValueError or IndexError:
        # print('error')
        return None
    except struct.error:
        # print(data)
        return None


def bool_to_bytes(c):
    b = struct.pack('=?', c)
    return b

def int_to_bytes(i):
    b = struct.pack('=i', i)
    return b

def float_to_bytes(f):
    b = struct.pack('=f', f)
    return b

def bytes_to_bool(b):
    (x,) = struct.unpack('=?', b)
    return x

def bytes_to_int(b):
    (x,) = struct.unpack('=i', b)
    return x

def bytes_to_float(b):
    (x,) = struct.unpack('=f', b)
    return x
