import os
import board
import busio
from analogio import AnalogIn
from time import sleep
from config import *
import gc

print("Setting up Serial Comms Connections\n")
# from Drivers.SPI_SD import *
print("Setting up I2Cs\n")
from Drivers.TMP117 import *
from Drivers.RTC import *
# from Drivers.Accelerometer import *
from Drivers.ADXL import *
print("Done\n")
# print("Setting up UARTs\n")
# worth putting a try catch block in one instance here
from Drivers.PSU import *
# from Drivers.SWARM import *
from Drivers.DGPS import *
# print("Done\n")
from Drivers.BATV import *
from Drivers.I2C_Devices import *
import gc

# pin_ip = AnalogIn(board.A3)
ADMIN_FLAG = False

def calibrate_offset():
    """Calibrates offset by populating once

    Returns:
        float: atan of calibrated offset to one slope
    """
    ADXL_343.offset = (0,0,0)
    x = ADXL_343.raw_x
    y = ADXL_343.raw_y
    z = ADXL_343.raw_z

    ADXL_343.offset = (
        round(-x / 8),
        round(-y / 8),
        round(-(z - 250) / 8), 
    )
    return ADXL_343.offset

def diskfree():
    info = os.statvfs("/sd")
    return(info[0] * info[3])
    print(f"bytes free: ",diskfree())   # redundant

def print_data_entries():
    """ Check if directory exists """
    PATH = "/sd/data_entries"
    
    try:
        if os.path.exists(PATH):
            print(os.listdir(PATH))
    except BaseException:
        print("Directory doesn't exist, create one.")
        # os.mkdir(PATH) # stuck in read-only mode so won't work
        pass

    """ Nodes could have been damaged due to using the wrong polarity? """
# def voltage_readings(pin):
#     global lc7 
#     # TODO: cannot use this sensor, maybe faulty? Sensor will be replaced with the same
#     # input method used previously with a couple of resistors in the form of a potential divider.
#     # Will be reading the inputs via an ADC input, just need to decide on the actual pin to use.
#     """ DEPRECATED AT THE MOMENT """
#     # try:
#     # print("Battery Voltage: %0.3fV" % (1+lc7.cell_voltage))
#     # print("Battery Percentage: %0.1F %%" %lc7.cell_percent)
#     # except BaseException:
#     #     print("Sensor not connected.")
#     #     pass
#     # return ("Vbat: {.2f}V".format((pin_ip.value * 3.3) / 65536))
#     """ BAT V readings are inconsistent """
#     print((pin.value * 3.3) / 65536)

def read_bat_voltage():
    enable_BATV()
    sleep(3)
    # return round(((BAT_V.value * 5) / 65536 - 0.1), 2)
    return BAT_VOLTS.battery_voltage(BAT_V)

def gps_uart():
    print("Checking UART connection")
    # RTCM3_UART = busio.UART(board.TX, board.RX, baudrate=115200, receiver_buffer_size=2048)
    # ''' GPS RTCM3 UART '''
    count = 5
    try:
        while count > 0: 
            GPS_DEVICE.update()
            if RTCM3_UART is not None:
                print(RTCM3_UART.readline())
                count -= 1
            else:
                print("Nothing in Buffer")
    except BaseException:
        print("GPS not detected")
        pass

def gps_i2c():
    count = 1
    while count > 0:
        GPS_DEVICE.update()
        # print(gps.readline())
        # if gps.has_3d_fix:
        # if "$GNGGA" in gps.nmea_sentence or "$GNZDA" in gps.nmea_sentence:
        # if GPS_DEVICE.nmea_sentence is None:
        #     # print("Nothing yet")
        #     continue
        if GPS_DEVICE.nmea_sentence is not None:
            if "$GNGGA" in GPS_DEVICE.nmea_sentence:
                # GPS_DEVICE.update()
                print("====================")
                print("I2C GPS - GNGGA")
                print(GPS_DEVICE.nmea_sentence)
                # print(GPS_DEVICE.readline())
            #     print("====================")
            if "$GNZDA" in GPS_DEVICE.nmea_sentence:
                    # GPS_DEVICE.update()
                print("====================")
                print("I2C GPS - GNZDA")
                print(GPS_DEVICE.nmea_sentence)
                # print(GPS_DEVICE.readline())
            # print(GPS_DEVICE.readline())
            print("====================")
            count -= 1
            try:
                print(GPS_DEVICE.to_dict())
            except BaseException:
                print("Nothing to show")
                print("exit")
            print("====================\n")
        # RTCM3_UART.update()
        # print(RTCM3_UART.readline())
        # print(gps_uart.readline().decode())
        # if "$GNGGA" in gps_uart.readline().decode():
        #     print("UART GPS")
        #     print(gps_uart.readline().decode())
        #     print("====================")
        # time.sleep(1)
    # if "$G" in data: 
    # # data.decode()
    #     data.split("$")


def radio_rx_test():
    print("Checking XBee Radio Uart connection")
    # from Drivers.Radio import *
    import Drivers.Radio
    try:
        # RADIO_UART = busio.UART(board.D11, board.D10, baudrate=9600, receiver_buffer_size=2048) 
        ''' Radio UART for communications'''
        # counter = 10
        MessageReceived = False
        while not MessageReceived:
            # if Drivers.Radio.UART is not None:
            #     print(Drivers.Radio.UART.readline())
            #     MessageReceived = True
            # else:
            #     print("Nothing in Buffer")
            Drivers.Radio.UART.readline()
            
    except BaseException:
        print("Radio not connected.\n Check pins and SMA antenna connections.")
        pass
    # gc.collect()

def radio_tx_test():
    print("Checking XBee Radio Uart connection")
    # from Drivers.Radio import *
    import Drivers.Radio

    try:
        # RADIO_UART = busio.UART(board.D11, board.D10, baudrate=9600, receiver_buffer_size=2048) 
        ''' Radio UART for communications'''
        counter = 10
        message = "SENDER ID: {}".format(DEVICE_ID)
        while counter > 0:
            Drivers.Radio.UART.write(message.encode() + "\n")
            sleep(1)
            counter -= 1
    except BaseException:
        print("Radio not connected.\n Check pins and SMA antenna connections.")
        pass
    # gc.collect()

# def radio_test():
#     print("Checking XBee Radio Uart connection")
#     # from Drivers.Radio import *
#     import Drivers.Radio

#     try:
#         # RADIO_UART = busio.UART(board.D11, board.D10, baudrate=9600, receiver_buffer_size=2048) 
#         ''' Radio UART for communications'''
#         counter = 10
#         while counter > 0:
#             if Drivers.Radio.UART is not None:
#                 print(Drivers.Radio.UART.readline())
#             else:
#                 print("Nothing in Buffer")
#             counter -= 1
#     except BaseException:
#         print("Radio not connected.\n Check pins and SMA antenna connections.")
#         pass


def temperature_sensor(): # uses board.SCL and board.SDA
    print(TMP_117.get_temperature())

def accelerometer_slope():
    xoff, yoff = ADXL_343.calib_accel()
    print(ADXL_343.accelerometer_to_slope(xoff,yoff))
#TODO: 
# - Check DateTime - RTC
# - Check SPI Mounted and available Storage
# - Check that Data exists in SPI storage
# - Check GPS - I2C and UART
# - Check Radio 
# - Check GSM Fona
# - Check SWARM 
# - Check Temperature Sensor
# - Check Accelerometer
# - Check BatV

def admin_menu():
    print("ADMIN MODE ACCESSED\n")
    print("Choose one of the following:\n")
    print("1\tDate/Time")
    print("2\tSPI SD Flash Chip")
    print("3\tAvailable Storage")
    print("4\t/Files on Chip")
    print("5\tGPS I2C NMEA")
    print("6\tGPS UART RTCM3")
    print("7\tXBee Radio - UART")
    print("8\tTemperature - TMP117")
    print("9\tBatV")
    print("10\tAccelerometer Slope - ADXL343")

    print("Push Button or Enter 0 to exit Admin mode")

def admincmd(c):
    global ADMIN_FLAG
    if c == "1":
        # may need to update this using gps time.
        print("Date/Time from DS3231 RTC Chip")
        print("Date: {}-{}-{}\n".format(RTC_DEVICE.datetime[2],RTC_DEVICE.datetime[1],RTC_DEVICE.datetime[0]))
        print("Time: {}:{}:{}\n".format(RTC_DEVICE.datetime[3],RTC_DEVICE.datetime[4],RTC_DEVICE.datetime[5]))
    elif c == "2":
        print("Checking SPI Flash Chip is Mounted")
        try:
            from Drivers.SPI_SD import storage, mount_SD, SPI_SD, CS
            mount_SD(SPI_SD,CS)
            print(storage.getmount("/sd"))
        except ImportError:
            print("Can't Import Driver")

    elif c == "3":
        print(f"Available Storage: ",diskfree())
    elif c == "4":
        from Drivers.SPI_SD import print_directory
        print(f"Files on SD Chip: ",print_directory("/sd"))
    elif c == "5":
        print("Reading NMEA Messages from I2C Pins on GPS board.")
        gps_i2c()
    elif c =="6":
        print("Reading RTCM3 Messages from UART2 Pins on GPS board.")
        gps_uart()
    elif c == "7":
        print("Testing XBee Radio Module is active.")
        print("Choose whether to test 1:TX or 2:RX:\n")
        # radio_test()
        option = input()
        if option == "1":
            radio_tx_test()
        elif option == "2":
            radio_rx_test()
        else:
            print("command not found")
    elif c == "8":
        print("Temperature Sensor Reading:")
        temperature_sensor()
    elif c == "9":
        print("Battery Voltage: ")
        enable_BATV()
        print(read_bat_voltage())
    elif c == "10":
        print("Accelerometer Slope:")
        accelerometer_slope()
    elif c == "0":
        ADMIN_FLAG = False
    else:   
        print("command not found")


if __name__ == '__main__':
    logger.info("DEVICE IN ADMIN MODE")
    admin_menu()
    ADMIN_FLAG = True
    while ADMIN_FLAG:
        admincmd(input())

    # while True:
    #     if ADMIN_IO.value:
    gc.collect()
    logger.info("DEVICE IN NORMAL MODE")
    exec(open('./main.py').read())

    #     else:
    #         admincmd(input())