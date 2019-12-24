#!/usr/bin/env python3

from smbus2 import SMBus, i2c_msg
import struct
from time import sleep

def calculateCRC(input):
    crc = 0xFF
    for i in range (0, 2):
        crc = crc ^ input[i]
        for j in range(8, 0, -1):
            if crc & 0x80:
                crc = (crc << 1) ^ 0x31
            else:
                crc = crc << 1
    crc = crc & 0x0000FF
    return crc

def checkCRC(result):
    for i in range(2, len(result), 3):
        data = []
        data.append(result[i-2])
        data.append(result[i-1])

        crc = result[i]

        if crc == calculateCRC(data):
            crc_result = True
        else:
            crc_result = False
    return crc_result

def bytes_to_int(bytes):
    result = 0
    for b in bytes:
        result = result * 256 + int(b)
    return result

def convertPMValues(value):
    string_value = str(hex(value)).replace("0x", "")

    byte_value = bytes.fromhex(string_value)

    return struct.unpack('>f', byte_value)[0]

class SPS30():
    SPS_ADDR = 0x69

    START_MEAS   = [0x00, 0x10]
    STOP_MEAS    = [0x01, 0x04]
    R_DATA_RDY   = [0x02, 0x02]
    R_VALUES     = [0x03, 0x00]
    RW_AUTO_CLN  = [0x80, 0x04]
    START_CLN    = [0x56, 0x07]
    R_ARTICLE_CD = [0xD0, 0x25]
    R_SERIAL_NUM = [0xD0, 0x33]
    RESET        = [0xD3, 0x04]

    NO_ERROR = 1
    ARTICLE_CODE_ERROR = -1
    SERIAL_NUMBER_ERROR = -2
    AUTO_CLN_INTERVAL_ERROR = -3
    DATA_READY_FLAG_ERROR = -4
    MEASURED_VALUES_ERROR = -5

    dict_values = {"pm1p0"  : None,
                   "pm2p5"  : None,
                   "pm4p0"  : None,
                   "pm10p0" : None,
                   "nc0p5"  : None,
                   "nc1p0"  : None,
                   "nc2p5"  : None,
                   "nc4p0"  : None,
                   "nc10p0" : None,
                   "typical": None}

    def __init__(self, port):
        self.bus = SMBus(port)

    def read_article_code(self):
        result = []
        article_code = []

        write = i2c_msg.write(self.SPS_ADDR, self.R_ARTICLE_CD)
        self.bus.i2c_rdwr(write)

        read = i2c_msg.read(self.SPS_ADDR, 48)
        self.bus.i2c_rdwr(read)

        for i in range(read.len):
            result.append(bytes_to_int(read.buf[i]))

        if checkCRC(result):
            for i in range (2, len(result), 3):
                article_code.append(chr(result[i-2]))
                article_code.append(chr(result[i-1]))
            return str("".join(article_code))
        else:
            return self.ARTICLE_CODE_ERROR

    def read_device_serial(self):
        result = []
        device_serial = []

        write = i2c_msg.write(self.SPS_ADDR, self.R_SERIAL_NUM)
        self.bus.i2c_rdwr(write)

        read = i2c_msg.read(self.SPS_ADDR, 48)
        self.bus.i2c_rdwr(read)

        for i in range(read.len):
            result.append(bytes_to_int(read.buf[i]))

        if checkCRC(result):
            for i in range(2, len(result), 3):
                device_serial.append(chr(result[i-2]))
                device_serial.append(chr(result[i-1]))
            return str("".join(device_serial))
        else:
            return self.SERIAL_NUMBER_ERROR

    def read_auto_cleaning_interval(self):
        result = []

        write = i2c_msg.write(self.SPS_ADDR, self.RW_AUTO_CLN)
        self.bus.i2c_rdwr(write)

        read = i2c_msg.read(self.SPS_ADDR, 6)
        self.bus.i2c_rdwr(read)

        for i in range(read.len):
            result.append(bytes_to_int(read.buf[i]))

        if checkCRC(result):
            result = result[0] * pow(2, 24) + result[1] * pow(2, 16) + result[3] * pow(2, 8) + result[4]
            return result
        else:
            return self.AUTO_CLN_INTERVAL_ERROR

    def set_auto_cleaning_interval(self, seconds):
        self.RW_AUTO_CLN.append((seconds >> 24) & 0xFF)
        self.RW_AUTO_CLN.append((seconds >> 16) & 0xFF)

        self.RW_AUTO_CLN.append(calculateCRC(self.RW_AUTO_CLN[2:4]))

        self.RW_AUTO_CLN.append((seconds >> 8) & 0xFF)
        self.RW_AUTO_CLN.append(seconds & 0xFF)

        self.RW_AUTO_CLN.append(calculateCRC(self.RW_AUTO_CLN[5:7]))

        write = i2c_msg.write(self.SPS_ADDR, self.RW_AUTO_CLN)
        self.bus.i2c_rdwr(write)

    def start_fan_cleaning(self):
        write = i2c_msg.write(self.SPS_ADDR, self.START_CLN)
        self.bus.i2c_rdwr(write)

    def start_measurement(self):
        self.START_MEAS.append(0x03)
        self.START_MEAS.append(0x00)

        crc = calculateCRC(self.START_MEAS[2:4])
        self.START_MEAS.append(crc)

        write = i2c_msg.write(self.SPS_ADDR, self.START_MEAS)
        self.bus.i2c_rdwr(write)

    def stop_measurement(self):
        write = i2c_msg.write(self.SPS_ADDR, self.STOP_MEAS)
        self.bus.i2c_rdwr(write)

    def read_data_ready_flag(self):
        result = []

        write = i2c_msg.write(self.SPS_ADDR, self.R_DATA_RDY)
        self.bus.i2c_rdwr(write)

        read = i2c_msg.read(self.SPS_ADDR, 3)
        self.bus.i2c_rdwr(read)

        for i in range(read.len):
            result.append(bytes_to_int(read.buf[i]))

        if checkCRC(result):
            return result[1]
        else:
            return self.DATA_READY_FLAG_ERROR

    def read_measured_values(self):
        result = []

        write = i2c_msg.write(self.SPS_ADDR, self.R_VALUES)
        self.bus.i2c_rdwr(write)

        read = i2c_msg.read(self.SPS_ADDR, 60)
        self.bus.i2c_rdwr(read)

        for i in range(read.len):
            result.append(bytes_to_int(read.buf[i]))

        if checkCRC(result):
            self.parse_sensor_values(result)
            return self.NO_ERROR
        else:
            return self.MEASURED_VALUES_ERROR

    def device_reset(self):
        write = i2c_msg.write(self.SPS_ADDR, self.RESET)
        self.bus.i2c_rdwr(write)
        sleep(1)

    def parse_sensor_values(self, input):
        index = 0
        pm_list = []
        for i in range (4, len(input), 6):
            value = input[i] + input[i-1] * pow(2, 8) +input[i-3] * pow(2, 16) + input[i-4] * pow(2, 24)
            pm_list.append(value)

        for i in self.dict_values.keys():
            self.dict_values[i] = convertPMValues(pm_list[index])
            index += 1
