#!/usr/bin/python
import smbus2
import time
import logging
import struct
from collections import namedtuple


class BMP180:
    # Original Author: Matt Hawkins

    # Register Addresses
    REG_CALIB = 0xAA
    REG_MEAS = 0xF4
    REG_MSB = 0xF6
    REG_LSB = 0xF7
    REG_ID = 0xD0

    # Control Register Address
    CRV_TEMP = 0x2E
    CRV_PRES = 0x34

    def __init__(self, bus=None, port=1, address=0x77):
        if bus is None:
            import smbus2

            self._managed = True
            self._bus = smbus2.SMBus(port)
        else:
            self._managed = False
            self._bus = bus
        self._addr = address

    def read_chip_id(self):
        # Chip ID Register Address
        (chip_id, chip_version) = self._bus.read_i2c_block_data(
            self._addr, self.REG_ID, 2
        )
        return (chip_id, chip_version)

    def read(self):
        # Oversample setting
        OVERSAMPLE = 3  # 0 - 3

        # Convert byte data to word values
        CalData = namedtuple(
            "CalData",
            [
                # order is the same as when reading from EEPROM
                "AC1",
                "AC2",
                "AC3",
                "AC4",
                "AC5",
                "AC6",
                "B1",
                "B2",
                "MB",
                "MC",
                "MD",
            ],
        )

        # Read calibration data from EEPROM
        raw_cal = self._bus.read_i2c_block_data(self._addr, self.REG_CALIB, 22)
        cal = CalData(*struct.unpack(">hhhHHHhhhhh", bytearray(raw_cal)))
        print("AC6", cal.AC6)
        print("B1", cal.B1)

        # Read temperature
        self._bus.write_byte_data(self._addr, self.REG_MEAS, self.CRV_TEMP)
        time.sleep(0.005)
        (msb, lsb) = self._bus.read_i2c_block_data(self._addr, self.REG_MSB, 2)
        UT = (msb << 8) + lsb

        # Refine temperature
        X1 = ((UT - cal.AC6) * cal.AC5) >> 15
        X2 = (cal.MC << 11) / (X1 + cal.MD)
        B5 = X1 + X2
        temperature = int(B5 + 8) >> 4
        temperature = temperature / 10.0

        # Read pressure
        self._bus.write_byte_data(
            self._addr, self.REG_MEAS, self.CRV_PRES + (OVERSAMPLE << 6)
        )
        time.sleep(0.04)
        (msb, lsb, xsb) = self._bus.read_i2c_block_data(self._addr, self.REG_MSB, 3)
        UP = ((msb << 16) + (lsb << 8) + xsb) >> (8 - OVERSAMPLE)

        # Refine pressure
        B6 = B5 - 4000
        B62 = int(B6 * B6) >> 12
        X1 = (cal.B2 * B62) >> 11
        X2 = int(cal.AC2 * B6) >> 11
        X3 = X1 + X2
        B3 = (((cal.AC1 * 4 + X3) << OVERSAMPLE) + 2) >> 2
        X1 = int(cal.AC3 * B6) >> 13
        X2 = (cal.B1 * B62) >> 16
        X3 = ((X1 + X2) + 2) >> 2
        B4 = (cal.AC4 * (X3 + 32768)) >> 15
        B7 = (UP - B3) * (50000 >> OVERSAMPLE)
        P = (B7 * 2) / B4
        X1 = (int(P) >> 8) * (int(P) >> 8)
        X1 = (X1 * 3038) >> 16
        X2 = int(-7357 * P) >> 16
        pressure = int(P + ((X1 + X2 + 3791) >> 4))

        return (temperature, pressure)


bus = smbus2.SMBus(1)
sensor = BMP180(bus)
print(sensor.read())
