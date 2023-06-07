from config import *
# TODO: turn print into an error log and STORE VALUE

import adafruit_tmp117
class TMP(adafruit_tmp117.TMP117):
    '''TEMPERATURE TMP117 I2C'''
    def get_temperature(self):
        try:
            print(round(self.temperature,2))
        except BaseException:
            print("Temperature sensor not detected!\n")
        


# TMP_117: TMP117 = TMP117(I2C)
