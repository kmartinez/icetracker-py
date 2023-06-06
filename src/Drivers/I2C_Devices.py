# PLACEHOLDER FOR ALL I2C Connected DEVICES
import busio, board
from Drivers.TMP117 import TMP117
from Drivers.DGPS import DGPS, RTCM3_UART
from Drivers.RTC import RTC
from Drivers.ADXL import *
# from Drivers.PSU import *
from config import GPS_EN
from time import sleep

GPS_EN.value = True

I2C = board.I2C()
'''Main I2C Bus for communication with TMP117, GPS NMEA and DS3231 Chip'''
TMP_117: TMP117 = TMP117(I2C)
'''TMP_117 I2C Init'''
GPS_DEVICE: DGPS = DGPS(I2C, RTCM3_UART)
'''DGPS I2C/UART Init'''
RTC_DEVICE: RTC = RTC(I2C)
'''RTC Init'''
ADXL_343: ADXL = ADXL(I2C)
'''ADXL Accelerometer Init'''

# tx, ty = ADXL_343.get_tilts(xoff=xoff, yoff=yoff)
# print(type(tx))
# while True:
#     print(tuple(ADXL_343.get_tilts(xoff=xoff, yoff=yoff)))
    
#     # print("{%d,%d}"%(tx))
#     sleep(0.5)