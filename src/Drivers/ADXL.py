import board
import time
import math
from adafruit_adxl34x import ADXL343


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
        print("Starting calibration, please make sure board is flat.")
        while True:
            x,y,z = self.acceleration
            if (x > -0.3 and x < 0.2) and (y > 0.0 and y > 0.4):
                print("Board is flat.\n Beginning Calibration.")
                break
            else:
                continue
        # print("set flat then press enter")
        # input()
        avx = 0.0
        avy = 0.0
        for n in range(10):
            '''self .acceleration is a property and can't be used in this statement'''
            x, y, z = self.acceleration
            # print(self.acceleration)
            avx = avx + x
            avy = avy + y
            time.sleep(0.1)
        print("Calibrated.")
        return avx/10, avy/10

    def get_tilts(self, xoff, yoff):
        x , y, z = self.acceleration
        x = x - xoff
        y = y - yoff       
        mag = math.sqrt(x**2 + y**2 + z**2)
        tilt_x = math.degrees(math.asin(x / mag))
        tilt_y = math.degrees(math.asin(y / mag))
        return round(tilt_x), round(tilt_y)

    def calibrate_offset(self):
        """Calibrates offset by populating once

        Returns:
            float: atan of calibrated offset to one slope
        """
        # offset in lab: (2,-2,0)
        # offset outside: tbc 
        self.offset = (0,0,0)
        x = self.raw_x
        y = self.raw_y
        z = self.raw_z

        self.offset = (
            round(-x / 8),
            round(-y / 8),
            round(-(z - 250) / 8), 
        )
        return self.offset

