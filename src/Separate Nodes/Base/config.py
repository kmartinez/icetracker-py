import adafruit_logging as logging
import board
from busio import UART, SPI, I2C
from digitalio import DigitalInOut

DEVICE_ID = 100
'''ID of this device (Will become base station if is 100 or higher)'''
# SET FOR BASE STATION ONLY
ROVER_COUNT = 2


ADMIN_IO = DigitalInOut(board.A2)
'''Main Admin IO Pin'''
COMMS_EN = DigitalInOut(board.D12)
COMMS_EN.switch_to_output(value=False)
'''ENABLE LR COMMS'''
GPS_EN = DigitalInOut(board.D4)
GPS_EN.switch_to_output(value=False)
'''ENABLE GPS'''
BATV_EN = DigitalInOut(board.A1)
BATV_EN.switch_to_output(value=False)
'''ENABLE BATV INPUT'''
"""Pin Definitions"""


GLOBAL_FAILSAFE_TIMEOUT = 180 # CHANGE to anything over 1000 when attempting to broadcast for a long duration.
'''If this amount of seconds passes program should abort and base should send whatever it has'''


DEBUG =  {
    "FAKE_DATA": False, #Ignores actual GPS data and just uses fake static data instead
    "WATCHDOG_DISABLE": False #Disables watchdog resets so you can debug things
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
