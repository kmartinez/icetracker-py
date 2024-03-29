import json
from adafruit_datetime import datetime
from mpy_decimal import DecimalNumber
from config import *
import adafruit_logging as logging

logger = logging.getLogger("GPS")

class GPSData:
    timestamp: datetime
    latitude: str
    longitude: str
    altitude: float
    sats: int
    temp: float
    batv: float
    #tilt: tuple

    def __init__(
        self,
        timestamp: datetime,
        latitude: DecimalNumber,
        longitude: DecimalNumber,
        altitude: float,
        sats: int,
        temp: float,
        batv: float,
        #tilt: tuple
        ):
        self.timestamp = timestamp
        self.latitude = str(latitude)
        self.longitude = str(longitude)
        self.altitude = altitude
        self.sats = sats
        self.temp = temp
        self.batv = batv
        #self.tilt = tilt

    def to_json(self) -> str:
        """Serializes self to json and then to bytes ready to send over radio

        :return: self as JSON string
        :rtype: str
        """
        data = {
            "timestamp": self.timestamp.isoformat(),
            "latitude": self.latitude[0:12],
            "longitude": self.longitude[0:13],
            "altitude": self.altitude,
            "sats": self.sats,
            "temp": self.temp,
            "batv": self.batv,
            #"tilt": self.tilt
        }
        output = json.dumps(data)

        logger.debug(f"SERIALIZE_GPSDATA_JSON_DUMP_DICTIONARY: {data}")
        return output

    def from_json(json_str: str) -> dict:
        """Deserializes a byte array to a dict, *NOT A GPSDATA OBJECT*

        :param byte_arr: Bytes to deserialize
        :type byte_arr: bytes
        :return: Dict representing a GPSData object (ready to send over json)
        :rtype: dict
        """
        logger.debug(f"INPUT_STRING: {json_str}")

        output = json.loads(json_str)

        logger.debug(f"DESERIALIZE_GPSDATA_DICT_OUTPUT: {output}")
        return output
