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

def send_and_delete_json_payload(http_payload, payload_paths):
    if len(http_payload) < 1:
        logger.info("Not sending empty payload! This is normal")
        return

    logger.debug("CREATING_NEW_SOCKET_FOR_REQUESTS_WORKAROUND")
    requests.set_socket(cellular_socket, fona)

    logger.info("Sending HTTP Request!")
    logger.debug(f"HTTP_REQUEST_DATA: {http_payload}")
    response = requests.post("http://iotgate.ecs.soton.ac.uk/myapp", json=http_payload)
    logger.info("Request complete!")

    logger.debug(f"HTTP_STATUS: {response.status_code}")
    # If data ingested correcttly, move files sent from /data_entries/ to /sent_data/
    if response.status_code == 200:
        logger.info("HTTP request successful - Removing sent data")
        for path in payload_paths:
            os.rename("/sd/data_entries/" + path, "/sd/sent_data/" + path)
    else:
        logger.warning(f"HTTP_REQUEST_STATUS: {response.status_code}, REASON: {response.reason}")

if __name__ == "__main__":
    logger.info("DISABLING GPS")
    # GPS_EN.value = False

    if not DEBUG["WATCHDOG_DISABLE"]:
        watchdog.timeout = 16
        watchdog.mode = WatchDogMode.RESET
        watchdog.feed()

     # - enable_fona now exists in the adafruit_library
    # try:
    logger.info("ENABLING GSM COMMS")

    fona = FONA(GSM_UART, GSM_RST_PIN, debug=True)
    
    logger.info("FONA initialized")
    logger.debug("FONA VERSION: fona.version")

    network = network.CELLULAR(
        fona, (SECRETS["apn"], SECRETS["apn_username"], SECRETS["apn_password"])
    )

    MAX_FAIL_COUNT = 10
    failcount = 0
    while not network.is_attached:
        failcount += 1
        if failcount > MAX_FAIL_COUNT:
            raise Exception("FONA could not attach")
        logger.info("Attaching to network...")
        time.sleep(0.5)
    logger.info("Attached!")

    failcount = 0
    while not network.is_connected:
        failcount += 1
        if failcount > MAX_FAIL_COUNT:
            raise Exception("FONA could not connect")
        logger.info("Connecting to network...")
        network.connect()
        time.sleep(0.5)
    logger.info("Network Connected!")


# Initialize a requests object with a socket and cellular interface
    # except UnicodeError:
    #     logger.critical("FONA needs to be power cycled. Incorrect AT commands received.")

    data_paths = os.listdir("/sd/data_entries/")
    http_payload = []
    payload_paths = []

    if len(data_paths) < 1:
        logger.warning("No unsent data on SD")
    for path in data_paths:
        with open("/sd/data_entries/" + path, "r") as file:
            try:
                http_payload.append(json.loads(file.readline()))
                payload_paths.append(path)
            except:
                logger.warning(f"Invalid saved data found at /data_entries/{path}")
        if len(http_payload) >= MAX_READINGS_IN_SINGLE_HTTP:
            send_and_delete_json_payload(http_payload, payload_paths)
            http_payload = []
            payload_paths = []
            #time.sleep(2)
    
    send_and_delete_json_payload(http_payload, payload_paths)
    shutdown()