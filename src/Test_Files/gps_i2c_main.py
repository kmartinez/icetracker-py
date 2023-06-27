# SPDX-FileCopyrightText: 2017 Limor Fried for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""CircuitPython I2C Device Address Scan"""
# If you run this and it seems to hang, try manually unlocking
# your I2C bus from the REPL with
#  >>> import board
#  >>> board.I2C().unlock()

# import time
# import board
# import busio
# import glacstracker_gps

# # To use default I2C bus (most boards)
# # i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller

# # To create I2C bus on specific pins
# # import busio
# # i2c = busio.I2C(board.SCL1, board.SDA1)  # QT Py RP2040 STEMMA connector
# # i2c = busio.I2C(board.GP1, board.GP0)    # Pi Pico RP2040

# while not i2c.try_lock():
#     pass

# try:
#     while True:
#         print(
#             "I2C addresses found:",
#             [hex(device_address) for device_address in i2c.scan()],
#         )
#         time.sleep(2)

# finally:  # unlock the i2c bus when ctrl-c'ing out of the loop
#     i2c.unlock()


# SPDX-FileCopyrightText: 2022 Dan Halbert for Adafruit Industries
#
# SPDX-License-Identifier: MIT import asyncio
# import board
# import digitalio
# import asyncio 

# async def blink(pin, interval, count):
#     with digitalio.DigitalInOut(pin) as led:
#         led.switch_to_output(value=False)
#         for _ in range(count):
#             led.value = True
#             await asyncio.sleep(interval) # Don't forget the "await"!
#             led.value = False
#             await asyncio.sleep(interval) # Don't forget the "await"! 
# async def main():
#     led1_task = asyncio.create_task(blink(board.D1, 0.25, 10))
#     led2_task = asyncio.create_task(blink(board.D0, 0.1, 20)) 
#     await asyncio.gather(led1_task, led2_task) # Don't forget "await"!
#     print("done")
# asyncio.run(main())

import board
import digitalio
import asyncio
import busio
from busio import UART, I2C
from lib.mpy_decimal import DecimalNumber
# from glactracker_gps import GPS, GPS_GtopI2C

from Drivers.DGPS import *
from spi_sd import *
import time

# GPS_I2C Address = 0x42
# GPS_I2C: I2C = board.STEMMA_I2C()
# RTCM3_UART: UART = UART(board.D1, board.D0, baudrate=115200, receiver_buffer_size=2048)

# gps = GPS_GtopI2C(GPS_I2C)
# gps_uart = GPS(RTCM3_UART)

def main():
    mount_SD()
    # print(f"Flash size bytes free: ",diskfree("/"))
    # print(f"SPI SMT SD Card bytes free: ",diskfree("/sd"))


    while True:
    

        GPS_DEVICE.update()
        # print(gps.readline())
        # if gps.has_3d_fix:
            # if "$GNGGA" in gps.nmea_sentence or "$GNZDA" in gps.nmea_sentence:
        if GPS_DEVICE.nmea_sentence is None:
            continue
        if "$GNGGA" in GPS_DEVICE.nmea_sentence:
            print("====================")
            print("I2C GPS")
            print(GPS_DEVICE.nmea_sentence)
            print("====================")
            # print("exit")
        """ GPS UART """
        # gps_uart.update()
        # print(gps_uart.readline().decode())
        # if "$GNGGA" in gps_uart.readline().decode():
        #     print("UART GPS")
        #     print(gps_uart.readline().decode())
        #     print("====================")
        # time.sleep(1)
    # if "$G" in data: 
    # # data.decode()
    #     data.split("$")

    # print(RTCM3_UART.readline())
    # remove_file("/sd/test.txt")
    # make_dir("/sd/sent_data")
    # print_directory("/sd")
    # logger("/sd/data_entries/Temperature.txt")
    # read_file("/sd/data_entries/Temperature.txt")

if __name__ == '__main__':
    main()