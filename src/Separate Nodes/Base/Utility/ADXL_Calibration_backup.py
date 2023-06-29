"""
use an accelerometer to measure the tilt from flat
we only need round degree values
change import to your accelerometer
"""

import board
import time
import math
from config import GPS_EN
from adafruit_adxl34x import ADXL343

GPS_EN.value = True
i2c = board.I2C() # uses board.SCL and board.SDA

class ADXL(ADXL343):
    def __init__(self, *args):
        super(ADXL, self).__init__(*args)
        
    def accelerometer_to_slope(self, x, y):
        slope = math.degrees(math.atan2(math.sqrt(x**2 + y**2), 1))
        return slope

    def accelerometer_to_inclination(self, x, y):
        inclination = math.degrees(math.atan2(y, x))
        return inclination

    def calib_accel(self):
        # interactive - needed once only and values need to go in calib file
        print("set flat then press enter")
        input()
        avx = 0.0
        avy = 0.0
        for n in range(10):
            '''self .acceleration is a property and can't be used in this statement'''
            x, y, z = self.acceleration
            # print(self.acceleration)
            avx = avx + x
            avy = avy + y
            time.sleep(0.1)
        return avx/10, avy/10

    def get_tilts(self, xoff, yoff):
        x , y, z = self.acceleration
        x = x - xoff
        y = y - yoff       
        mag = math.sqrt(x**2 + y**2 + z**2)
        tilt_x = math.degrees(math.asin(x / mag))
        tilt_y = math.degrees(math.asin(y / mag))
        return round(tilt_x), round(tilt_y)



ADXL_343: ADXL = ADXL(i2c)
# xoff, yoff = ADXL_343.calib_accel()
# # print(xoff, yoff)
# while True:
#     tx, ty = ADXL_343.get_tilts(xoff=xoff, yoff=yoff)
#     # print(tx, ty)
#     print("{%d,%d}"%(tx,ty))
    
#     time.sleep(.5)

