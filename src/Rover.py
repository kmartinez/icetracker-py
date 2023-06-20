from Drivers.I2C_Devices import GPS_DEVICE, RTC_DEVICE, ADXL_343, TMP_117, shutdown
# import Drivers.PSU as PSU
import Drivers.Radio as radio
from Drivers.Radio import PacketType
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

accurate_reading_saved: bool = False
sent_data_start_pos: int = 999999999

def truncate_degrees(longitude, latitude):
    #TODO: scale size can be adjusted - function could be redundant. 
    lat = latitude.split(".")[0] + "." + latitude.split(".")[1][:7]
    lon = longitude.split(".")[0] + "." + longitude .split(".")[1][:7]

    return lat, lon 


async def feed_watchdog():
    while True:
        if not DEBUG["WATCHDOG_DISABLE"]:
            watchdog.feed()
        await asyncio.sleep(0)

async def rover_loop():
    """Main loop of each rover.
    Waits for radio message and checks its type.
    If it's RTCM3, send back NMEA data.
    If it's an ACK for us, shutdown the system because the base has our stuff
    """
    # Rover needs to:
    # Receive packet
    # If RTCM3 received, get NMEA and send it
    # If ACK received, shutdown
    global accurate_reading_saved
    global sent_data_start_pos
    gc.collect()
    print("Point 3 Available memory: {} bytes".format(gc.mem_free()))
    while True:
        logger.info("Waiting for a radio packet")
        # watchdog.feed()
        try:
            packet = await radio.receive_packet()
        except radio.ChecksumError:
        # try:
        #     logger.info("Waiting for a radio packet")
        #     packet = await radio.receive_packet()
        # except radio.ChecksumError:
            continue
        # If incoming message is tagged as RTCM3
        if packet.type == PacketType.RTCM3 and not accurate_reading_saved:
            logger.info("receiving rtcm3")
            GPS_DEVICE.rtk_calibrate(packet.payload)
            gc.collect()
            print("Point 4 Available memory: {} bytes".format(gc.mem_free()))
            if GPS_DEVICE.update_with_all_available():
                print("In here")
                GPS_SAMPLES["lats"].append(GPS_DEVICE.latitude)
                GPS_SAMPLES["longs"].append(GPS_DEVICE.longitude)

                # Standard deviation for at least 5 samples
                if (len(GPS_SAMPLES["longs"].circularBuffer) < AVERAGING_SAMPLE_SIZE): continue
                
                debug_variance = util.var(GPS_SAMPLES["longs"].circularBuffer)
                logger.debug(f"VARIANCE_LONG: {debug_variance}")

                if util.var(GPS_SAMPLES["longs"].circularBuffer) < VAR_MAX and util.var(GPS_SAMPLES["lats"].circularBuffer) < VAR_MAX:
                    logger.info("Fix obtained: writing to file")
                    #TODO: Temporary fix for RTC timing data to be able to send packets across to the base.
                    #Enabling Battery Voltage Pin to read Bat Vol
                    enable_BATV()
                    sleep(2)
                    
                    #TODO: only confirm this if using reliable GPS data, otherwise, datetime lags behind
                    RTC_DEVICE.datetime = GPS_DEVICE.timestamp_utc
                    print(RTC_DEVICE.datetime)
                    #TODO: Get Static values from config file
                    xoff, yoff = ADXL_343.calib_accel()
                    gps_data = GPSData(
                        datetime.fromtimestamp(time.mktime(GPS_DEVICE.timestamp_utc)),
                        util.mean(GPS_SAMPLES["lats"].circularBuffer),
                        util.mean(GPS_SAMPLES["longs"].circularBuffer),
                        GPS_DEVICE.altitude_m,
                        GPS_DEVICE.fix_quality,
                        float(GPS_DEVICE.horizontal_dilution),
                        int(GPS_DEVICE.satellites),
                        TMP_117.get_temperature(),
                        BAT_VOLTS.battery_voltage(BAT_V),
                        tuple(ADXL_343.get_tilts(xoff=xoff, yoff=yoff))
                        )
                    
                    with open("/sd/data_entries/" + gps_data.timestamp.isoformat().replace(":", "_"), "w") as file:
                        file.write(gps_data.to_json() + "\n")
                    logger.info("File write complete")
                    accurate_reading_saved = True

                    gc.collect()
                    print("Point 7 Available memory: {} bytes".format(gc.mem_free()))
        elif packet.type == PacketType.RTCM3:
            #RTCM3 received and we have collected our data for this session
            #Send the oldest data point we have
            #If there aren't any, delete
            logger.info("got RTCM and accurate reading")
            remaining_paths = os.listdir("/sd/data_entries/")
            if (len(remaining_paths) > 0):
                logger.info("Sending reading to base")
                with open("/sd/data_entries/" + remaining_paths[0], "r") as file:
                    data_to_send = file.readline()
                    radio.broadcast_data(PacketType.NMEA, data_to_send.encode('utf-8'))
            else:
                logger.info("Telling base that we're finished")
                radio.broadcast_data(PacketType.FIN, struct.pack(FormatStrings.PACKET_DEVICE_ID, packet.sender))

        elif packet.type == PacketType.ACK and struct.unpack(radio.FormatStrings.PACKET_DEVICE_ID, packet.payload)[0] == DEVICE_ID:
            #ACK received: base received our data
            #We can now safely delete from SD
            logger.info("ACK received from base, deleting sent data")
            if len(os.listdir("/sd/data_entries/")) > 0:
                os.remove("/sd/data_entries/" + os.listdir("/sd/data_entries/")[0])
            
        elif packet.type == PacketType.FIN and struct.unpack(FormatStrings.PACKET_DEVICE_ID, packet.payload)[0] == DEVICE_ID:
            logger.info("Base said OK to shutdown!")
            gc.collect()
            print("Point 8 Available memory: {} bytes".format(gc.mem_free()))
            # TODO: I2C Buffer prevents proper shutdown when disabling GPS, need a workaround for this.
            # GPS_EN.value = False 
            # shutdown()
            break
    logger.info("ROVER COMPLETED: SHUTTING DOWN.")
    

if __name__ == "__main__":
    try:
        gc.collect()
        print("Point 2 Available memory: {} bytes".format(gc.mem_free()))
        # asyncio.run(asyncio.wait_for_ms(asyncio.gather(rover_loop(), feed_watchdog()), GLOBAL_FAILSAFE_TIMEOUT * 1000))
        asyncio.run(asyncio.wait_for_ms(asyncio.gather(rover_loop()), GLOBAL_FAILSAFE_TIMEOUT * 1000))
        # shutdown()
    except MemoryError:
        logger.critical("Out of Memory - Resetting Device.")
        microcontroller.reset()
    finally:
        shutdown()