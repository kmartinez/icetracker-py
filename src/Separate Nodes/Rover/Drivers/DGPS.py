# import glactracker_gps
import glactracker_gps 
from busio import UART
import adafruit_logging as logging
from config import *
from mpy_decimal import DecimalNumber
from time import localtime,time
import board
from Drivers.AsyncUART import AsyncUART
import binascii
import gc

logger = logging.getLogger("GPS")

class DGPS(glactracker_gps.GPS_GtopI2C):
    def __init__(self, i2c: I2C, rtcm_uart: AsyncUART, debug: bool = False) -> None:
        super().__init__(i2c, address=0x42, debug=False)
        self.rtcm_uart = rtcm_uart
    
    def rtk_calibrate(self, rtcm3_data: bytes):
        logger.debug(f"CALIBRATING_RTCM3_BYTES: {binascii.hexlify(rtcm3_data)}")
        print(len(binascii.hexlify(rtcm3_data)))
        self.rtcm_uart.write(rtcm3_data)

    def to_dict(self):
        return {
            "LAT": self.latitude,
            "LONG": self.longitude,
            "ALTITUDE": self.altitude_m,
            "TIMESTAMP": self.timestamp_utc,
            "QUALITY": self.fix_quality,
            "HDOP_STR": self.horizontal_dilution,
            "SATELLITES_STR": self.satellites,
            "REMAINING_BUFFER_SIZE": self.in_waiting
        }
    
    def update_with_all_available(self):
        logger.info("read GPS")

        gc.collect()
        print("Point 5 Available memory: {} bytes".format(gc.mem_free()))

        device_updated: bool = self.update() #Potentially garbage line so we continue anyway even if it doesn't actually work
        # normally using 'not' self.update() to be able to read New incoming nmea sentences.
        # wait until new NMEA received from GPS
        # while self.update():
        while not self.update(): #- to be used for outdoors sim
            print(device_updated)
            device_updated = True #Performs as many GPS updates as there are NMEA strings available in UART
        
        if (DEBUG["FAKE_DATA"]):
            #Fake data
            logger.warning("Fake data mode is on! No real GPS data will be used on this device!!!!")
            self.latitude = DecimalNumber("59.3")
            self.longitude = DecimalNumber("-1.2")
            self.altitude_m = 5002.3
            self.timestamp_utc = localtime(time())
            self.fix_quality = 4
            self.horizontal_dilution = "0.01"
            self.satellites = "9"
        
        logger.debug(f"GPS_DATA: {self.to_dict()}")

        gc.collect()

        # If NMEA received back
        if self.fix_quality == 4:
            logger.info("GPS fix")
            gc.collect()
            print("Point 6 Available memory: {} bytes".format(gc.mem_free()))
            # print(device_updated)
            device_updated = True
            return device_updated
        else:
            logger.info("GPS quality is currently insufficient")
            return False
    
    async def get_rtcm3_message(self):
        """Returns the corrections from the GPS as a bytearray

        :return: Bytes object of the 5 RTCM3 messages
        :rtype: bytes()
        """
        # Read UART for newline terminated data - produces bytestr
        logger.info("Retrieving RTCM3 from UART")
        RTCM3_UART.reset_input_buffer()
        await RTCM3_UART.aysnc_read_RTCM3_packet_forever() #Garbled maybe
        data = bytearray()
        for i in range(5):
            d = await RTCM3_UART.aysnc_read_RTCM3_packet_forever()
            data += d
        logger.debug(f"RTCM3_BYTES: {binascii.hexlify(bytes(data))}")
        logger.info("RTCM3 obtained from UART")
        return bytes(data)

RTCM3_UART: AsyncUART = AsyncUART(board.D1, board.D0, baudrate=115200, receiver_buffer_size=2048)
'''GPS RTCM3 UART'''

