from config import *

from adafruit_tmp117 import TMP117
class TMP117(TMP117):
    '''TEMPERATURE TMP117 I2C'''
    temp: float
    def get_temperature(self):
        temp = self.temperature
        try:
            return round((temp),2)
        except BaseException:
            logging.critical("Temperature sensor not detected.\n Please check connections.")
        

# TMP_117: TMP117 = TMP117(I2C)