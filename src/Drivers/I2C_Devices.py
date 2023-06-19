# sort out ALL I2C Connected DEVICES
import busio, board
from Drivers.TMP117 import TMP117
from Drivers.DGPS import DGPS, RTCM3_UART
from Drivers.RTC import RTC
# from Drivers.PSU import *
from config import *
from time import sleep
import supervisor
logger = logging.getLogger("DEVICE")
GPS_EN.value = True
try:
    I2C = busio.I2C(board.SCL, board.SDA)
    '''Main I2C Bus for communication with TMP117, GPS NMEA and DS3231 Chip'''
    TMP_117: TMP117 = TMP117(I2C)
    '''TMP_117 I2C Init'''
    GPS_DEVICE: DGPS = DGPS(I2C, RTCM3_UART)
    '''DGPS I2C/UART Init'''
    RTC_DEVICE: RTC = RTC(I2C)
    '''RTC timer'''
except RuntimeError:
    logger.critical("I2C Connection Aborted - Restarting Device.")
    supervisor.reload()
# except ValueError:
#     logger.warning("I2C Connection with Module Lost")
#     supervisor.reload()

# tx, ty = ADXL_343.get_tilts(xoff=xoff, yoff=yoff)
# print(type(tx))
# while True:
#     print(tuple(ADXL_343.get_tilts(xoff=ACC_X_OFF, yoff=ACC_Y_OFF)))
    
#     # print("{%d,%d}"%(tx))
#     sleep(0.5)

# def shutdown():
#     """Resets timer, causing shutdown of device
#     """
#     logger.info("Device shutting down!")
#     RTC_DEVICE.alarm2_status = False
#     RTC_DEVICE.alarm1_status = False
