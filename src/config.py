import adafruit_logging as logging
import board
from busio import UART, SPI, I2C
from digitalio import DigitalInOut

DEVICE_ID = 18
'''ID of this device (Will become base station if is 100 or higher)'''
# accel offsets (find manually and enter here)
ACC_X_OFF = 0
ACC_Y_OFF = 0
ANT_OFFSET = 0
#SET FOR BASE STATION ONLY
ROVER_COUNT = 1

"""PIN Definitions"""
ADMIN_IO = DigitalInOut(board.A2)
'''Main Admin IO Pin'''
COMMS_EN = DigitalInOut(board.D12)
COMMS_EN.switch_to_output(value=False)
'''ENABLE LR COMMS - BASE ONLY'''
GPS_EN = DigitalInOut(board.D4)
GPS_EN.switch_to_output(value=False)
'''ENABLE GPS'''
BATV_EN = DigitalInOut(board.A1)
BATV_EN.switch_to_output(value=False)
'''ENABLE BATV INPUT'''

GLOBAL_FAILSAFE_TIMEOUT = 180
'''If this amount of seconds passes program should abort and base should send whatever it has'''

DEBUG =  {
    "FAKE_DATA": False, #Ignores actual GPS data and just uses fake static data instead
    "WATCHDOG_DISABLE": False #Disables watchdog resets so you can debug things
}

LOGGER_NAMES = ["BASE", "DEVICE", "ROVER", "ASYNC_UART", "RADIO", "MAIN_FILE", "GPS"]
for name in LOGGER_NAMES:
    logging.getLogger(name).setLevel(logging.INFO)

COMMS_TIME = [13] #Final version should be 13 or 14
WAKE_UP_WINDOW_HRS  = [0, 3, 6, 9, 12, 13, 15, 18, 21]
WAKE_UP_WINDOW_MINS = [0]

SECRETS = { #I would put this on its own file untracked by git if you ever put any actual sensitive info here
    "apn": "TM",
    "apn_username": "",
    "apn_password": "",
}
