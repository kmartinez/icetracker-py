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
#from Drivers.ADXL import *
print("Done\n")
# print("Setting up UARTs\n")
from Drivers.PSU import *
# from Drivers.SWARM import *
from Drivers.DGPS import *
# print("Done\n")
from Drivers.BATV import *
from Drivers.I2C_Devices import *

# pin_ip = AnalogIn(board.A3)
ADMIN_FLAG = False

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

def radio_test():
    print("Checking XBee Radio Uart connection")
    # from Drivers.Radio import *
    import Drivers.Radio

    try:
        # RADIO_UART = busio.UART(board.D11, board.D10, baudrate=9600, receiver_buffer_size=2048) 
        ''' Radio UART for communications'''
        counter = 10
        while counter > 0:
            if Drivers.Radio.UART is not None:
                print(Drivers.Radio.UART.readline())
            else:
                print("Nothing in Buffer")
            counter -= 1
    except BaseException:
        print("Radio not connected.\n Check pins and SMA antenna connections.")
        pass


def temperature_sensor(): # uses board.SCL and board.SDA
    print(TMP_117.get_temperature())

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
    print("10\tDelete all SD data")
    
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
        radio_test()
    elif c == "8":
        print("Temperature Sensor Reading:")
        temperature_sensor()
    elif c == "9":
        print("Battery Voltage: ")
        enable_BATV()
        print(read_bat_voltage())
    # elif c == "10":
    #     print("Accelerometer Slope:")
    #     accelerometer_slope()
    elif c == "10":
        print("REMOVING ALL DATA")
        from Drivers.SPI_SD import mount_SD, SPI_SD, CS
        try:
            mount_SD(SPI_SD,CS)
        except ImportError:
            print("Can't Import Driver")
        if "data_entries" in os.listdir("/sd/"):
            for file in os.listdir("/sd/data_entries/"):
                os.remove("/sd/data_entries/" + file)
            #os.rmdir("/sd/data_entries")
        if "sent_data" in os.listdir("/sd/"):
            for file in os.listdir("/sd/sent_data/"):
                os.remove("/sd/sent_data/" + file)
            #os.rmdir("/sd/sent_data")
        if "error_log.txt" in os.listdir("/sd/"):
            os.remove("/sd/error_log.txt")
        print("DONE")
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
