from Drivers.I2C_Devices import GPS_DEVICE, RTC_DEVICE, TMP_117
# import Drivers.PSU as PSU
import Drivers.Radio as radio
from Drivers.Radio import PacketType, RadioPacket
import struct
from config import *
from Statistics.StatsBuffer import StatsBuffer
import ulab.numpy as np
from Statistics import Util as util
from mpy_decimal import *
from RadioMessages.GPSData import *
from Drivers.Radio import FormatStrings
import os
from microcontroller import watchdog
import adafruit_logging as logging
import time
from time import sleep
import asyncio
import gc
import microcontroller


from Drivers.BATV import * 
from Drivers.PSU import *


logger = logging.getLogger("ROVER")



DecimalNumber.set_scale(16)
SD_MAX = DecimalNumber("0.0001")
VAR_MAX = SD_MAX ** 2
'''Maximum acceptible standard deviation [m]'''
AVERAGING_SAMPLE_SIZE = 5
'''number of samples to take a rolling standard deviation and average of'''

GPS_SAMPLES: dict[str, StatsBuffer] = {
    "lats": StatsBuffer(AVERAGING_SAMPLE_SIZE),
    "longs": StatsBuffer(AVERAGING_SAMPLE_SIZE)
}

fix4_reading_saved: bool = False
sent_data_start_pos: int = 999999999

def truncate_degrees(longitude, latitude):
    #TODO: scale size can be adjusted - function could be redundant. 
    lat = latitude.split(".")[0] + "." + latitude.split(".")[1][:7]
    lon = longitude.split(".")[0] + "." + longitude .split(".")[1][:7]

    return lat, lon 

ACK_Packets: list[RadioPacket] = []
RTCM3_Packets: list[RadioPacket] = []
FIN_Received: bool = False

async def feed_watchdog():
    global FIN_Received
    while not FIN_Received:
        if not DEBUG["WATCHDOG_DISABLE"]:
            watchdog.feed()
        await asyncio.sleep(0)
    
    logger.debug("ROVER: STOP_FEEDING_WATCHDOG")

async def clock_calibrator():
    """Task that waits until the GPS has a timestamp and then calibrates the RTC using GPS time
    """
    gc.collect()
    while GPS_DEVICE.timestamp_utc is None:
        #let GPS update with the GPS task
        logger.debug("CLOCK_CALIB_RUN!")
        await asyncio.sleep(0.5)
    RTC_DEVICE.datetime = GPS_DEVICE.timestamp_utc

async def radio_receive_loop():
    """Receives radio messages"""
    global ACK_Packets
    global RTCM3_Packets
    global FIN_Received
    while not FIN_Received:
        logger.info("ROVER: Waiting for packet")
        try:
            packet = await radio.receive_packet()
        except radio.ChecksumError:
            logger.warning("ROVER: radio checksum fail")
            logger.warning(f"ROVER: radio buffer size {radio.UART.in_waiting}")
            radio.UART.reset_input_buffer() #clear garbage?
            continue
        logger.info("ROVER: packet received")
        logger.debug(f"ROVER: PACKET_TYPE: {packet.type}")

        if packet.type == PacketType.ACK and fix4_reading_saved and struct.unpack(radio.FormatStrings.PACKET_DEVICE_ID, packet.payload)[0] == DEVICE_ID:
            logger.debug("ROVER_RADIO_TASK: ACK RECEIVED")
            ACK_Packets.append(packet)
        elif packet.type == PacketType.RTCM3 and not fix4_reading_saved:
            RTCM3_Packets.append(packet)
        elif packet.type == PacketType.FIN and fix4_reading_saved and struct.unpack(FormatStrings.PACKET_DEVICE_ID, packet.payload)[0] == DEVICE_ID:
            logger.debug("ROVER_RADIO_TASK: FIN RECEIVED")
            FIN_Received = True
            break
    
    logger.debug("ROVER: RADIO_TASK_END")

async def handle_rtcm3_packets():
    global RTCM3_Packets
    while not fix4_reading_saved:
        while len(RTCM3_Packets) > 0:
            GPS_DEVICE.rtk_calibrate(RTCM3_Packets[0].payload)
            RTCM3_Packets = RTCM3_Packets[1:]
            logger.info("ROVER: RTCM3 processed")
        await asyncio.sleep(0)
    
    logger.debug("ROVER: RTCM_TASK_END")

async def handle_gps_updates():
    """Updates GPS info asynchronously"""
    global fix4_reading_saved
    while not fix4_reading_saved:
        gps_updated = False
        GPS_DEVICE.update() #no garbage
        logger.log(5, "ROVER_GPS_UPDATE_BEGIN")
        while GPS_DEVICE.update():
            logger.debug("ROVER_GPS_UPDATE_SUCCESS?")
            gps_updated = True
        logger.log(5, "ROVER_GPS_UPDATE_END")
        if gps_updated:
            logger.debug("GPS_UPDATED!")
        if gps_updated and GPS_DEVICE.fix_quality == 4:
        # if gps_updated:
            logger.info("New coords with fix 4 found!")
            GPS_SAMPLES["lats"].append(GPS_DEVICE.latitude)
            GPS_SAMPLES["longs"].append(GPS_DEVICE.longitude)

            # Standard deviation for at least 5 samples
            if (len(GPS_SAMPLES["longs"].circularBuffer) < AVERAGING_SAMPLE_SIZE):
                await asyncio.sleep(0)
                continue
            logger.debug(f"VARIANCE_LONG_AFTER_CHECK: {util.var(GPS_SAMPLES["longs"].circularBuffer)}")

            if util.var(GPS_SAMPLES["longs"].circularBuffer) < VAR_MAX and util.var(GPS_SAMPLES["lats"].circularBuffer) < VAR_MAX:
                logger.info("Fix obtained and variance verified: writing to file")
                #TODO: Temporary fix for RTC timing data to be able to send packets across to the base.
                #Enabling Battery Voltage Pin to read Bat Vol
                enable_BATV()
                await asyncio.sleep(2)
                
                #TODO: only confirm this if using reliable GPS data, otherwise, datetime lags behind
                #If it got here without reliable GPS data, God help you
                RTC_DEVICE.datetime = GPS_DEVICE.timestamp_utc
                #TODO: Get Static values from config file
                # xoff, yoff = ADXL_343.calib_accel()
                gps_data = GPSData(
                    datetime.fromtimestamp(time.mktime(GPS_DEVICE.timestamp_utc)),
                    util.mean(GPS_SAMPLES["lats"].circularBuffer),
                    util.mean(GPS_SAMPLES["longs"].circularBuffer),
                    GPS_DEVICE.altitude_m,
                    int(GPS_DEVICE.satellites),
                    TMP_117.get_temperature(),
                    BAT_VOLTS.battery_voltage(BAT_V),
                    # tuple(ADXL_343.get_tilts(xoff=ACC_X_OFF, yoff=ACC_Y_OFF))
                    )
                
                with open("/sd/data_entries/" + gps_data.timestamp.isoformat().replace(":", "_"), "w") as file:
                    file.write(gps_data.to_json() + "\n")
                logger.info("File write complete")
                fix4_reading_saved = True

                gc.collect()
                logger.debug("Point 7 Available memory: {} bytes".format(gc.mem_free()))
        logger.log(5, "GPS_TASK_SLEEPING")
        await asyncio.sleep(0.5)
    
    logger.debug("ROVER: GPS_TASK_END")

async def handle_acks():
    global ACK_Packets
    global FIN_Received
    """Handles any ACKs that come in"""
    while not fix4_reading_saved:
        await asyncio.sleep(0)
    #ACK received: base received our data
    #We can now safely delete from SD
    logger.info("ROVER: RECV ACKS")
    while not FIN_Received:
        while len(ACK_Packets) > 0 and len(os.listdir("/sd/data_entries/")) > 0:
            #WARNING, this has no means of checking what data this ack is for
            logger.info("ACK received from base, deleting sent data")
            os.remove("/sd/data_entries/" + os.listdir("/sd/data_entries/")[0])
            
        if len(os.listdir("/sd/data_entries/")) < 1:
            break
        await asyncio.sleep(0)
    
    logger.debug("ROVER: ACK_TASK_END")
    
async def transmit_data():
    global FIN_Received
    while not fix4_reading_saved:
        await asyncio.sleep(1)
    logger.info("Rover is finished collecting!")

    logger.debug("ROVER_TRANSMIT_TASK: WARNING: clearing radio buffer to maybe help lag? ")
    radio.UART.reset_input_buffer()
    while not FIN_Received:
        remaining_paths = os.listdir("/sd/data_entries/")
        if (len(remaining_paths) > 0):
            logger.info("Sending reading to base")
            with open("/sd/data_entries/" + remaining_paths[0], "r") as file:
                data_to_send = file.readline()
                radio.broadcast_data(PacketType.NMEA, data_to_send.encode('utf-8'))
        else:
            logger.info("Telling base that we're finished")
            radio.broadcast_data(PacketType.FIN, struct.pack(FormatStrings.PACKET_DEVICE_ID, BASE_ID))
        await asyncio.sleep(4)# let base respond (within 2 seconds)
    
    logger.debug("ROVER: TRANSMIT_TASK_END")   

if __name__ == "__main__":
    try:
        gc.collect()
        logger.debug("Point 2 Available memory: {} bytes".format(gc.mem_free()))
        asyncio.run(asyncio.wait_for_ms(asyncio.gather(radio_receive_loop(), transmit_data(), handle_acks(), handle_rtcm3_packets(), handle_gps_updates(), clock_calibrator(), feed_watchdog()), GLOBAL_FAILSAFE_TIMEOUT * 1000))
        # asyncio.run(asyncio.wait_for_ms(asyncio.gather(rover_loop()), GLOBAL_FAILSAFE_TIMEOUT * 1000))
        logger.info("ROVER_COMPLETE")
        # shutdown()
    except MemoryError:
        logger.critical("Out of Memory - Resetting Device.")
        microcontroller.reset()
    finally:
        shutdown()