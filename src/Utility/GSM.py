"""tests GSM/fona connection
sends test POST to a test server
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

    fona = FONA(GSM_UART, GSM_RST_PIN, debug=True)
    
    logger.info("FONA initialized")

    network = network.CELLULAR(
        fona, (SECRETS["apn"], SECRETS["apn_username"], SECRETS["apn_password"])
    )

    MAX_FAIL_COUNT=3
    failcount = 0
    while not network.is_attached:
        failcount += 1
        if failcount > MAX_FAIL_COUNT:
            raise Exception("FONA could not attach")
        logger.info("Attaching to network...")
        time.sleep(0.5)
    logger.info("Attached")

    logger.info(f"FONA RSSI: {fona.rssi}")

    failcount = 0
    while not network.is_connected:
        failcount += 1
        if failcount > MAX_FAIL_COUNT:
            raise Exception("FONA could not connect")
        logger.info("Connecting to network")
        network.connect()
        time.sleep(0.5)
    logger.info("Network Connected")


# Initialize a requests object with a socket and cellular interface
    requests.set_socket(cellular_socket, fona)
    # except UnicodeError:
    #     logger.critical("FONA needs to be power cycled. Incorrect AT commands received.")

    TEXT_URL = "http://wifitest.adafruit.com/testwifi/index.html"
    logger.info("My IP address is: %s", fona.local_ip)
    logger.info("IP lookup adafruit.com: %s", fona.get_host_by_name("adafruit.com"))
    #response = requests.get(TEXT_URL)
    while True:
        requests.set_socket(cellular_socket, fona)
        response = requests.post("http://iotgate.ecs.soton.ac.uk/postin", json=[{
            "test1": "asdfasdfasdfasdf",
            "test2": "asdfasdfasdfasdf",
            "test3": "asdfasdfasdfasdf",
        }])
        logger.info(f"STATUS: {response.status_code}")
        time.sleep(5)
