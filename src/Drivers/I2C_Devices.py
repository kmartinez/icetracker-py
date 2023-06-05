# PLACEHOLDER FOR ALL I2C Connected DEVICES
import busio, board
from Drivers.TMP117 import *
from Drivers.DGPS import DGPS, RTCM3_UART
from Drivers.RTC import RTC
# from Drivers.PSU import *
from config import GPS_EN

GPS_EN.value = True

I2C = busio.I2C(board.SCL, board.SDA)
# I2C_STEMMA = board.STEMMA_I2C()
'''Main I2C Bus for communication with TMP117, GPS NMEA and DS3231 Chip'''
TMP_117: TMP = TMP(I2C)
'''TMP_117 I2C Init'''
GPS_DEVICE: DGPS = DGPS(I2C, RTCM3_UART)
'''DGPS I2C/UART Init'''
RTC_DEVICE: RTC = RTC(I2C)
'''RTC timer'''
