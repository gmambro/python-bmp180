import pytest

from smbus2_bmp180 import BMP180

def test_constructor():
    sensor = BMP180()
