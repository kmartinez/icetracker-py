"""Main code for base stations Aug 2023
Creates a scheduler and adds all base station tasks
"""

from Drivers.PSU import * #EVERYTHING FROM THIS IS READONLY
from config import *
from Drivers.RTC import *
from RadioMessages.GPSData import *
from Drivers.I2C_Devices import GPS_DEVICE, RTC_DEVICE, TMP_117
from Drivers.BATV import *
import Drivers.Radio as radio
from Drivers.Radio import PacketType
import time
from adafruit_datetime import datetime
import gc
print(gc.mem_free())
gc.enable()

import asyncio

import struct
import os
from microcontroller import watchdog
import adafruit_logging as logging
import supervisor

logger = logging.getLogger("BASE")

#keep track of completed rovers
finished_rovers: dict[int, bool] = {}
rtcm3_rovers: dict[int, bool] = {}

async def clock_calibrator():
    """waits until the GPS has timestamp then writes to RTC
    """
    while GPS_DEVICE.timestamp_utc is None:
        logger.debug("CLOCK_CALIB waiting")
        GPS_DEVICE.update()
        if GPS_DEVICE.timestamp_utc is not None:
            # only valid ts are read so write
            RTC_DEVICE.datetime = GPS_DEVICE.timestamp_utc
        await asyncio.sleep(0.5)

async def feed_watchdog():
    """feeds the watchdog then yields
    """
    while len(finished_rovers) < ROVER_COUNT:
        if not DEBUG["WATCHDOG_DISABLE"]:
            watchdog.feed()
        await asyncio.sleep(0)

async def read_sensors():
    """one-shot reads temperature and battery voltage"""
    enable_BATV()
    await asyncio.sleep(2)
    data = {}
    data["id"] = DEVICE_ID
    data["timestamp"] = datetime.fromtimestamp(time.mktime(RTC_DEVICE.datetime)).isoformat()
    data["temp"] = TMP_117.get_temperature()
    data["batv"] = BAT_VOLTS.battery_voltage(BAT_V)
    with open("/sd/data_entries/" + str(DEVICE_ID) + "-" + datetime.fromtimestamp(time.mktime(RTC_DEVICE.datetime)).isoformat().replace(":", "_"), "w") as file:
        logger.debug(f"WRITING_DATA_TO_FILE: {data}")
        file.write(json.dumps(data) + '\n')
    logger.debug("TEMP AND BATV data saved")

async def rtcm3_loop():
    """continuously broadcasts available RTCM3 correction data.
    """
    global rtcm3_rovers
    rtcm3_pause = False
    while len(finished_rovers) < ROVER_COUNT: #Finish running when rover data is done
        rtcm3_data = await GPS_DEVICE.get_rtcm3_message()
        if len(rtcm3_rovers) < 1:
            rtcm3_pause = False
        else:
            for k,v in rtcm3_rovers.items():
                if v:
                    rtcm3_pause = True
                    break
            rtcm3_pause = False
        
        logger.debug(f"RTCM3_PAUSE: {rtcm3_pause}")
        if not rtcm3_pause:
            radio.broadcast_data(PacketType.RTCM3, rtcm3_data)

async def rover_data_loop():
    """continuously process all incoming rover data until timeout or all rovers are finished.
    """
    while len(finished_rovers) < ROVER_COUNT: #While there are any Nones in finished list
        try:
            logger.info("Waiting for a radio packet")
            packet = await radio.receive_packet()
            logger.info(f"packet received from {packet.sender}")
            logger.debug(f"PACKET TYPE: {packet.type}")
        except radio.ChecksumError:
            logger.warning("Radio received invalid packet")
            continue
        if packet.sender < 0:
            logger.warning("""Packet sender's ID is out of bounds!
            check its config""")
            continue

        if packet.type == PacketType.NMEA:
            logger.info("Radio received GPS data from a rover",)
            if len(packet.payload) < 0:
                logger.warning("Empty GPS data received")
                continue
            data = GPSData.from_json(packet.payload.decode('utf-8'))
            #print(data)
            rtcm3_rovers[packet.sender] = True
            with open("/sd/data_entries/" + str(packet.sender) + "-" + data["timestamp"].replace(":", "_"), "w") as file:
                data['rover_id'] = packet.sender
                logger.debug(f"WRITING_DATA_TO_FILE: {data}")
                file.write(json.dumps(data) + '\n')
            
            radio.send_response(PacketType.ACK, packet.sender)

        elif packet.type == PacketType.FIN and struct.unpack(radio.FormatStrings.PACKET_DEVICE_ID, packet.payload)[0] == DEVICE_ID:
            logger.info(f"FIN RECEIVED FROM {packet.sender}")
            rtcm3_rovers[packet.sender] = False
            finished_rovers[packet.sender] = True
            await asyncio.sleep(3)
            for i in range(10):
                radio.send_response(PacketType.FIN, packet.sender)
                await asyncio.sleep(0.05)
            if not len(finished_rovers) < ROVER_COUNT:
                await asyncio.sleep(3) #give time to send before shutdown?
        logger.info("Received radio packet processed OK")
    logger.info("Loop for receiving rover data has ended")
                

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
        loop.run_until_complete(asyncio.wait_for_ms(asyncio.gather(read_sensors(), clock_calibrator(), rover_data_loop(), rtcm3_loop(), feed_watchdog()), GLOBAL_FAILSAFE_TIMEOUT * 1000))
        # loop.run_until_complete(rover_data_loop())
        #use this for indoor tests
        #loop.run_until_complete(asyncio.wait_for_ms(asyncio.gather(rover_data_loop(), rtcm3_loop(), feed_watchdog()), GLOBAL_FAILSAFE_TIMEOUT * 1000)) # for indoor testing
        logger.info("Async tasks have finished running")
    except asyncio.TimeoutError:
        logger.warning("Async tasks timed out")
        pass #Don't care
    except MemoryError:
        if RTC_DEVICE.alarm1_status:
            shutdown()
        else:
            supervisor.reload()
    finally:
        shutdown()