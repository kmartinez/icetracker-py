import board
from analogio import AnalogIn

class BATV():

    def battery_voltage(self, BAT_V):
        '''Returns Battery voltage'''
        return round(((BAT_V.value * 5) / 65536 - 0.1), 2)


BAT_V = AnalogIn(board.A0)

BAT_VOLTS: BATV = BATV()