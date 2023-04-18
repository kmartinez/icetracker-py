import board
import busio
import bitbangio
import digitalio
from microcontroller import Pin
from main_sd import *

# i2c = board.I2C()


# def is_hardware_uart(tx, rx):
#     try:
#         p = busio.UART(tx, rx)
#         p.deinit()
#         return True
#     except ValueError:
#         return False


# def get_unique_pins():
#     exclude = ['NEOPIXEL', 'APA102_MOSI', 'APA102_SCK']
#     pins = [pin for pin in [
#         getattr(board, p) for p in dir(board) if p not in exclude]
#             if isinstance(pin, Pin)]
#     unique = []
#     for p in pins:
#         if p not in unique:
#             unique.append(p)
#     return unique

def hardware_uarts_instances():
    try:
        # gps_uart = busio.UART(board.A1, board.A2)


        # print(storage.getmount("/sd"))
        # print("Bytes Available: ", diskfree())
        print("Available UARTS: ")
        rtcm_gps_uart = busio.UART(board.D1, board.D0) # remember D1 = TX, 
D0 = RX
        radio_uart = busio.UART(board.D11, board.D10)
        gsm_uart = busio.UART(board.D13, board.D6)
        # gsm_uart = busio.UART(board.A5, board.D6)

        # free_uart = busio.UART(board.D13, board.D12)
        gsm_key = digitalio.DigitalInOut(board.A3)
        # print("All UART pins valid")
        ''' Invalid Pins'''
        # sd_slot = busio.SPI(board.SCK, board.MOSI, board.MISO)
        mount_SD()
        # rtc_i2c = busio.I2C(board.SDA, board.SCL)
        # rtc = board.I2C()
        gps_nmea = busio.I2C(board.SDA, board.SCL)

        ''' Can replace D12 io '''
        return True
    except ValueError:
        print("invalid pins")
        return False




def main():
    print(hardware_uarts_instances())

if __name__ == '__main__':
    main()
