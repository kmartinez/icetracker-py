"""Main code for base stations.
Creates a scheduler and adds all base station tasks to it
"""


from adafruit_fona.adafruit_fona import FONA
import adafruit_fona.adafruit_fona_network as network
import adafruit_fona.adafruit_fona_socket as cellular_socket
from Drivers.SPI_SD import *
import time
from Drivers.PSU import * #EVERYTHING FROM THIS IS READONLY (you can use write functions, but cannot actually modify a variable)
from config import *
import json
import adafruit_requests as requests
import asyncio
import struct
import os
from microcontroller import watchdog
from watchdog import WatchDogMode
import adafruit_logging as logging

logger = logging.getLogger("BASE")


#this is a global variable so i can still get the data even if the rover loop times out
finished_rovers: dict[int, bool] = {}

if __name__ == "__main__":
    logger.info("ENABLING GSM COMMS")

    fona = FONA(GSM_UART, GSM_RST_PIN, debug=False)
    
    logger.info("FONA initialized")
    logger.debug("FONA VERSION: fona.version")

    network = network.CELLULAR(
        fona, (SECRETS["apn"], SECRETS["apn_username"], SECRETS["apn_password"])
    )

    while not network.is_attached:
        logger.info("Attaching to network...")
        time.sleep(0.5)
    logger.info("Attached!")

    while not network.is_connected:
        logger.info("Connecting to network...")
        network.connect()
        time.sleep(0.5)
    logger.info("Network Connected!")


# Initialize a requests object with a socket and cellular interface
    requests.set_socket(cellular_socket, fona)
    # except UnicodeError:
    #     logger.critical("FONA needs to be power cycled. Incorrect AT commands received.")

    TEXT_URL = "http://wifitest.adafruit.com/testwifi/index.html"
    logger.info("My IP address is: %s", fona.local_ip)
    logger.info("IP lookup adafruit.com: %s", fona.get_host_by_name("adafruit.com"))
    logger.info(requests.get(r = requests.get(TEXT_URL)).text)