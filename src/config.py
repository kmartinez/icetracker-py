import adafruit_logging as logging
import board
from busio import UART, SPI, I2C
from digitalio import DigitalInOut
from Drivers.I2C_Devices import *

"""PIN Definitions"""
# I2C = board.I2C()
'''Main I2C Bus for communication with TMP117, GPS NMEA and DS3231 Chip'''
ADMIN_IO = DigitalInOut(board.A2)
'''Main Admin IO Pin'''
GPS_EN = DigitalInOut(board.D4)
GPS_EN.switch_to_output(value=False)
'''ENALBE GPS'''
BATV_EN = DigitalInOut(board.A1)
BATV_EN.switch_to_output(value=False)
'''ENABLE BATV INPUT'''

def calibrate_offset():
    """Calibrates offset by populating once

    Returns:
        float: atan of calibrated offset to one slope
    """
    ADXL_343.offset = (0,0,0)
    x = ADXL_343.raw_x
    y = ADXL_343.raw_y
    z = ADXL_343.raw_z

    ADXL_343.offset(
        round(-x / 8),
        round(-y / 8),
        round(-(z - 250) / 8), 
    )
    x, y ,z = ADXL_343.offset
    slope = ADXL_343.accelerometer_to_slope(x,y)
    return slope



GLOBAL_FAILSAFE_TIMEOUT = 120
'''If this amount of seconds passes program should abort and base should send whatever it has'''
TIME_BETWEEN_WAKEUP = 180
'''Amount of seconds RTC should wait before setting off the alarm again (waking up the system in the process)'''
DEVICE_ID = 18
'''ID of this device (Will become base station if is 0)'''
ROVER_COUNT = 1

DEBUG =  {
    "FAKE_DATA": False, #Ignores actual GPS data and just uses fake static data instead
    "WATCHDOG_DISABLE": True #Disables watchdog resets so you can debug things
}

logging.getLogger("BASE").setLevel(logging.INFO)
logging.getLogger("DEVICE").setLevel(logging.INFO)
logging.getLogger("ROVER").setLevel(logging.INFO)
logging.getLogger("ASYNC_UART").setLevel(logging.INFO)
logging.getLogger("RADIO").setLevel(logging.INFO)
logging.getLogger("MAIN_FILE").setLevel(logging.INFO)
logging.getLogger("GPS").setLevel(logging.DEBUG)


SECRETS = { #I would put this on its own file untracked by git if you ever put any actual sensitive info here
    "apn": "TM",
    "apn_username": "",
    "apn_password": "",
}
