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
    # loop = asyncio.new_event_loop()
    #Base needs to:
    #Get RTCM3 correction.
    #Send RTCM3 data
    #Receive packet
    #If GPS data received:
    # If rover not already received, store GPS data.
    # Send ACK to rover
    #end
        
    logger.info("DISABLING GPS")
    # GPS_EN.value = False

    if not DEBUG["WATCHDOG_DISABLE"]:
        watchdog.timeout = 16
        watchdog.mode = WatchDogMode.RESET
        watchdog.feed()

     # - enable_fona now exists in the adafruit_library
    # try:
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


# logger.info(f"My Local IP address is: {fona.local_ip}")

# Initialize a requests object with a socket and cellular interface
    requests.set_socket(cellular_socket, fona)
    # except UnicodeError:
    #     logger.critical("FONA needs to be power cycled. Incorrect AT commands received.")

    #TODO: add checker to make sure that the contents are > 0
    http_payload = []
    data_paths = os.listdir("/sd/data_entries/")[-1:]
    if len(data_paths) > 0:
        for path in data_paths:
            with open("/sd/data_entries/" + path, "r") as file:
                try:
                    http_payload.append(json.loads(file.readline()))
                except:
                    logger.warning(f"Invalid saved data found at /data_entries/{path}")
                    #os.remove("/data_entries/" + path) #This could be dangerous - DON'T DO!
                #TODO: RAM limit
        logger.debug(f"HTTP_PAYLOAD: {http_payload}")
    else:
        logger.warning("No Stored data on system. Turning off.")
        shutdown()

    try:
        logger.info("Sending HTTP request!")
        # response = requests.post("http://iotgate.ecs.soton.ac.uk/glacsweb/api/ingest", json=http_payload)
        response = requests.post("http://iotgate.ecs.soton.ac.uk/myapp", json=http_payload)
        logger.info(f"STATUS CODE: {response.status_code}, REASON: {response.reason}")
        #requests.post("http://google.com/glacsweb/api/ingest", json=http_payload)
        #TODO: check if response OK

        # If data ingested correcttly, move files sent from /data_entries/ to /sent_data/
        if str(response.status_code) == "200":
            paths_sent = os.listdir("/sd/data_entries/")[-1:]
            for path in paths_sent:
                os.rename("/sd/data_entries/" + path, "/sd/sent_data/" + path)
            logger.info("HTTP request successful! Removing all sent data")
        else:
            logger.warning(f"STATUS CODE: {response.status_code}, REASON: {response.reason}")
    finally:
        # import microcontroller
        
        print("Turning Off...")
        # microcontroller.
        shutdown()