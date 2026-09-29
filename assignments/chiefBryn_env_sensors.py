"""Minimal MicroPython drivers for AHT20 and BMP280.
Save this file on the ESP32 alongside Exercise 2 or Exercise 3.
Based on the ASAIR AHT20 and Bosch BMP280 datasheets.
"""
from time import sleep_ms, ticks_ms, ticks_diff
import struct


class AHT20:
    def __init__(self, i2c, address=0x38):
        self.i2c, self.address = i2c, address
        sleep_ms(40)
        if not self._status() & 0x08:
            i2c.writeto(address, b'\xbe\x08\x00')
            sleep_ms(10)
        if not self._status() & 0x08:
            raise OSError('AHT20 calibration not ready')

    def _status(self):
        self.i2c.writeto(self.address, b'\x71')
        return self.i2c.readfrom(self.address, 1)[0]

    def read(self):
        self.i2c.writeto(self.address, b'\xac\x33\x00')
        sleep_ms(80)
        start = ticks_ms()
        while True:
            data = self.i2c.readfrom(self.address, 7)
            if not data[0] & 0x80:
                break
            if ticks_diff(ticks_ms(), start) > 200:
                raise OSError('AHT20 measurement timeout')
            sleep_ms(10)
        crc = 0xFF
        for value in data[:6]:
            crc ^= value
            for _ in range(8):
                crc = ((crc << 1) ^ 0x31) & 255 if crc & 128 else (crc << 1) & 255
        if crc != data[6]:
            raise OSError('AHT20 CRC failed')
        if not data[0] & 0x08:
            raise OSError('AHT20 lost calibration')
        humidity = ((data[1] << 12) | (data[2] << 4) | (data[3] >> 4))
        temp = ((data[3] & 15) << 16) | (data[4] << 8) | data[5]
        return temp * 200.0 / 1048576 - 50, humidity * 100.0 / 1048576


class BMP280:
    def __init__(self, i2c):
        self.i2c = i2c
        for address in (0x76, 0x77):
            try:
                if i2c.readfrom_mem(address, 0xD0, 1)[0] == 0x58:
                    self.address = address
                    break
            except OSError:
                pass
        else:
            raise OSError('BMP280 ID 0x58 missing at 0x76/0x77')
        start = ticks_ms()
        while self._read(0xF3, 1)[0] & 1:
            if ticks_diff(ticks_ms(), start) > 200:
                raise OSError('BMP280 calibration timeout')
            sleep_ms(5)
        self.cal = struct.unpack('<HhhHhhhhhhhh', self._read(0x88, 24))
        if self.cal[3] == 0:
            raise ValueError('BMP280 invalid calibration')
        # Temperature x1, pressure x1, sleep until forced measurement.
        i2c.writeto_mem(self.address, 0xF4, b'\x24')

    def _read(self, reg, count):
        return self.i2c.readfrom_mem(self.address, reg, count)

    def pressure_hpa(self):
        self.i2c.writeto_mem(self.address, 0xF4, b'\x25')
        sleep_ms(10)
        start = ticks_ms()
        while self._read(0xF3, 1)[0] & 8:
            if ticks_diff(ticks_ms(), start) > 200:
                raise OSError('BMP280 measurement timeout')
            sleep_ms(5)
        d = self._read(0xF7, 6)
        ap = (d[0] << 12) | (d[1] << 4) | (d[2] >> 4)
        at = (d[3] << 12) | (d[4] << 4) | (d[5] >> 4)
        if ap == 0x80000 or at == 0x80000:
            raise ValueError('BMP280 skipped measurement')
        return self._compensate(ap, at)

    def _compensate(self, ap, at):
        t1, t2, t3, p1, p2, p3, p4, p5, p6, p7, p8, p9 = self.cal
        v1 = (at / 16384.0 - t1 / 1024.0) * t2
        v2 = (at / 131072.0 - t1 / 8192.0) ** 2 * t3
        fine = v1 + v2
        v1 = fine / 2.0 - 64000.0
        v2 = v1 * v1 * p6 / 32768.0
        v2 += v1 * p5 * 2.0
        v2 = v2 / 4.0 + p4 * 65536.0
        v1 = (p3 * v1 * v1 / 524288.0 + p2 * v1) / 524288.0
        v1 = (1.0 + v1 / 32768.0) * p1
        if v1 == 0:
            raise ValueError('BMP280 pressure divisor is zero')
        pressure = (1048576.0 - ap - v2 / 4096.0) * 6250.0 / v1
        v1 = p9 * pressure * pressure / 2147483648.0
        v2 = pressure * p8 / 32768.0
        return (pressure + (v1 + v2 + p7) / 16.0) / 100.0
