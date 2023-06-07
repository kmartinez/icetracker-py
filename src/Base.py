"""Main code for base stations.
Creates a scheduler and adds all base station tasks to it
reads RTCM corrections from GPS and sends to radio to broadcast
waits for a fix message from rovers and stores data in a file
at COMS time sends data to a server
TODO: clean data file store archive if disk is "full", remove unwanted commented code, check when gc called
"""

from adafruit_fona.adafruit_fona import FONA
import adafruit_fona.adafruit_fona_network as network
import adafruit_fona.adafruit_fona_socket as cellular_socket
import time
from Drivers.PSU import * #EVERYTHING FROM THIS IS READONLY (you can use write functions, but cannot actually modify a variable)
from config import *
from RadioMessages.GPSData import *
# from Drivers.DGPS import GPS_DEVICE
from Drivers.I2C_Devices import GPS_DEVICE, RTC_DEVICE
import Drivers.Radio as radio
from Drivers.Radio import PacketType

import adafruit_requests as requests

import gc
print(gc.mem_free())
gc.enable()

import asyncio

import struct
import os
from microcontroller import watchdog
import adafruit_logging as logging


logger = logging.getLogger("BASE")

#this is a global variable so i can still get the data even if the rover loop times out
finished_rovers: dict[int, bool] = {}
# when to send data
COMMS_TIME = [12]

# async def clock_calibrator():
#     """Task that waits until the GPS has a timestamp and then calibrates the RTC using GPS time
#     """
#     gc.collect()
#     while GPS_DEVICE.timestamp_utc == None:
#         while not GPS_DEVICE.update():
#             pass
#         RTC_DEVICE.datetime = GPS_DEVICE.timestamp_utc

# Untested but just needs to run ONCE when GPS has been running a while
def clock_calibrator():
    """Task that runs a flag to check if RTC timestamp has deviated and needs to be calibrated with GPS time."""
    rtc_calibrated = False
    while GPS_DEVICE.timestamp_utc == None:
            while not GPS_DEVICE.update():
                pass
    
    while not rtc_calibrated:
        if RTC_DEVICE.datetime != GPS_DEVICE.timestamp_utc:
            RTC_DEVICE.datetime = GPS_DEVICE
            rtc_calibrated = True
        

async def feed_watchdog():
    """Upon being executed by a scheduler, this task will feed the watchdog then yield.
    Added as a task to the asyncio scheduler by this module's main code.
    """
    while len(finished_rovers) < ROVER_COUNT:
        if not DEBUG["WATCHDOG_DISABLE"]:
            watchdog.feed()
        await asyncio.sleep(0)

async def rtcm3_loop():
    """Task that continuously broadcasts available RTCM3 correction data.
    """
    while len(finished_rovers) < ROVER_COUNT: #Finish running when rover data is done
        rtcm3_data = await GPS_DEVICE.get_rtcm3_message()
        radio.broadcast_data(PacketType.RTCM3, rtcm3_data)

async def rover_data_loop():
    """Task that continuously processes all incoming rover data until timeout or all rovers are finished.
    """
    while len(finished_rovers) < ROVER_COUNT: #While there are any Nones in rover_data
        try:
            logger.info("Waiting for a rover data")
            packet = await radio.receive_packet()
            logger.info(f"Rover data received from {packet.sender}")
        except radio.ChecksumError:
            logger.warning("Radio received an invalid packet")
            continue
        if packet.sender < 0:
            logger.warning("""Rover's ID is out of bounds!
            check its ID in its config!""")
            continue

        if packet.type == PacketType.NMEA:
            logger.info("Received Rover data is GPS data",)
            if len(packet.payload) < 0:
                logger.warning("Rover GPS data empty!")
                continue
            data = GPSData.from_json(packet.payload.decode('utf-8'))
            with open("/sd/data_entries/" + str(packet.sender) + "-" + data["timestamp"].replace(":", "_"), "w") as file:
                data['rover_id'] = packet.sender
                logger.debug(f"WRITING_DATA_TO_FILE: {data}")
                file.write(json.dumps(data) + '\n')
            
            radio.send_response(PacketType.ACK, packet.sender)

        elif packet.type == PacketType.FIN and struct.unpack(radio.FormatStrings.PACKET_DEVICE_ID, packet.payload)[0] == DEVICE_ID:
            finished_rovers[packet.sender] = True
            radio.send_response(PacketType.FIN, packet.sender)
        logger.info("Rover data processed OK")
    logger.info("Ending rover data receiver")
                

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    #Base needs to:
    #Get RTCM3 correction.
    #Send RTCM3 data
    #Receive packet
    #If GPS data received:
    # If rover not already received, store GPS data.
    # Send ACK to rover
    #end
    

    try:
        logger.info("Starting async tasks")
        loop.run_until_complete(asyncio.wait_for_ms(asyncio.gather(rover_data_loop(), rtcm3_loop(), feed_watchdog()), GLOBAL_FAILSAFE_TIMEOUT * 1000))
        logger.info("Async tasks have finished running")
    except asyncio.TimeoutError:
        logger.warning("Async tasks timed out! Continuing with any remaining data")
        pass #Don't care, we have data, just send what we got

    
    # if its COMMS_TIME time just do off-site data sending
    # otherwise, turn off.

    # try:
    logger.info("Checking current time")
    # clock_calibrator updates time on RTC # may need to feed watchdog here...
    # use clock calibrator, make sure that watchdog has been fed through it, and then use RTC
    '''Can utilise a similar script from clock_calibrator if RTC_DEVICE fails to update'''
    # while GPS_DEVICE.timestamp_utc == None:
    #     while not GPS_DEVICE.update():
    #         pass
    
    GPS_EN.value = False

    if RTC_DEVICE.datetime[3] in COMMS_TIME and RTC_DEVICE.datetime[4] < 15:
        logger.info('Comms Time: Enabling GSM.')
        # try:
        #     from adafruit_fona.adafruit_fona import FONA
        #     # from adafruit_fona.fona_3g import FONA3G
        #     import adafruit_fona.adafruit_fona_network as network
        #     import adafruit_fona.adafruit_fona_socket as cellular_socket
        #     # Temporary Delay needed when cold booting fona to avoid unicode error...
        # except ImportError:
        #     logger.critical("Unable to import files.")
        # enable_fona()
        # time.sleep(5)

        fona = FONA(GSM_UART, GSM_RST_PIN, debug=True)
        
        logger.info("FONA initialized")
        #logger.debug(f"FONA VERSION: fona.version")

        network = network.CELLULAR(
            fona, (SECRETS["apn"], SECRETS["apn_username"], SECRETS["apn_password"])
        )

        while not network.is_attached:
            logger.info("Attaching to network")
            time.sleep(0.5)
        logger.info("Attached!")

        while not network.is_connected:
            logger.info("Connecting to network")
            network.connect()
            time.sleep(0.5)
        logger.info("Network Connected")
        
        gc.collect()
        # Initialize a requests object with a socket and cellular interface
        requests.set_socket(cellular_socket, fona)

        http_payload = []
        data_paths = os.listdir("/sd/data_entries/")
        for path in data_paths:
            with open("/sd/data_entries/" + path, "r") as file:
                try:
                    http_payload.append(json.loads(file.readline()))
                except:
                    logger.warning(f"Invalid saved data found in /data_entries/{path}")
                    #os.remove("/data_entries/" + path) #This could be dangerous - DON'T DO! BUT need to clean if full
                #TODO: RAM limit
        logger.debug(f"HTTP_PAYLOAD: {http_payload}") # heavy print


        try:
            logger.info("Sending HTTP request")
            # response = requests.post("http://iotgate.ecs.soton.ac.uk/glacsweb/api/ingest", json=http_payload)
            response = requests.post("http://iotgate.ecs.soton.ac.uk/myapp", json=http_payload)
            logger.info(f"STATUS CODE: {response.status_code}, REASON: {response.reason}")
            #requests.post("http://google.com/glacsweb/api/ingest", json=http_payload)
            #TODO: check if response OK log OK if 200 else log code

            # If data ingested correcttly, move files sent from /data_entries/ to /sent_data/
            if str(response.status_code) == "200":
                paths_sent = os.listdir("/sd/data_entries/")
                for path in paths_sent:
                    os.rename("/sd/data_entries/" + path, "/sd/sent_data/" + path)
                logger.info("HTTP request successful! Removing all sent data")
            else:
                logger.warning(f"STATUS CODE: {response.status_code}, REASON: {response.reason}")
        finally:
            shutdown()
    else:
        logger.warning("Logged data and shutting down")
        shutdown()
    # except OSError:
    #     logger.critical("Unexpected Behaviour Here.")
    #     shutdown()
