import board
import busio
import adafruit_tmp117

class TMP117(adafruit_tmp117.TMP117):
    def get_temperature(self):
        try:
            return round(self.temperature,2)
        except BaseException:
            print("Temperature sensor not detected.\n Please check connections.")
        
# I2C: busio.I2C = board.STEMMA_I2C()
'''I2C bus (for TMP module)'''

# TMP_117: TMP117 = TMP117(I2C)