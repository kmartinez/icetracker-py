from config import *
# from Drivers.RTC import RTC_DEVICE
from Drivers.I2C_Devices import RTC_DEVICE
logger = logging.getLogger("DEVICE")

GSM_UART: UART = UART(board.A5, board.D6, baudrate=9600)
'''GSM FONA UART'''
# GSM_KEY = DigitalInOut(board.D5) # can be pinned to GND
'''GSM KEY PIN'''
GSM_RST_PIN = DigitalInOut(board.D9) # should be D9, but throws a UnicodeError Upon Reset.
'''GSM RST PIN'''


def enable_fona():
    COMMS_EN.value = True

def enable_gps():
    GPS_EN.value = True

def enable_system():
    BATV_EN.value = True

def shutdown():
    """Resets RTC alarm, causing poweroff of device
    """
    logger.info("Device shutting down!")
    # RTC_DEVICE.alarm2_status = False
    RTC_DEVICE.alarm1_status = False