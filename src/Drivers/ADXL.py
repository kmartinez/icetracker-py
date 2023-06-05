from config import *
from adafruit_adxl34x import ADXL343

class ADXL(ADXL343):
    # def __init__(self, i2c: I2C, address: int = 53):
        # super().__init__(i2c, address)

    # def __init__():
    #     pass

    def get_acceleration(self):
        x = round(self.acceleration[0],3)
        y = round(self.acceleration[1],3)
        z = round(self.acceleration[2],3)

        return x,y,z
    
