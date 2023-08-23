import os
import board
import busio
from analogio import AnalogIn
from time import sleep
from config import *
import gc

print("importing drivers for tmp and RTC\n")
# from Drivers.SPI_SD import *
from Drivers.TMP117 import *
from Drivers.RTC import *
print("importing PSU BatV and DGPS\n")
from Drivers.PSU import *
from Drivers.DGPS import *
from Drivers.BATV import *
from Drivers.I2C_Devices import *
import sys
# pin_ip = AnalogIn(board.A3)
ADMIN_FLAG = False

def diskfree():
    info = os.statvfs("/sd")
    return(info[0] * info[3])
    
def print_data_entries():
    """ Check data dir exists """
    PATH = "/sd/data_entries"
    
    try:
        if os.path.exists(PATH):
            print(os.listdir(PATH))
    except BaseException:
        print("Directory doesn't exist, create one.")
        # os.mkdir(PATH) # stuck in read-only mode so won't work???
        pass

def read_bat_voltage():
    enable_BATV()
    # allow cap charge up
    sleep(0.5)
    # return round(((BAT_V.value * 5) / 65536 - 0.1), 2)
    v = BAT_VOLTS.battery_voltage(BAT_V)
    # should disable batv here???
    return v

def gps_uart():
    print("Checking RTCM connection")
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
                print("Nothing in Buffer") # should say no rtcm messgread ???
    except BaseException:
        print("GPS not detected")
        pass

def gps_i2c():
    count = 1
    while count > 0:
        GPS_DEVICE.update()

        if GPS_DEVICE.nmea_sentence is not None:
            if "$GNGGA" in GPS_DEVICE.nmea_sentence:
                # GPS_DEVICE.update()
                print("I2C GPS - GNGGA received")
                print(GPS_DEVICE.nmea_sentence)
                # print(GPS_DEVICE.readline())
            # WE DONT USE ZDA SO THIS CAN BE DELETED???
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
    print("Read (10x) XBee Radio Uart\n")
    # from Drivers.Radio import *
    import Drivers.Radio

    try:
        ''' read Radio UART'''
        counter = 10
        while counter > 0:
            if Drivers.Radio.UART is not None:
                print(Drivers.Radio.UART.readline())
            else:
                print("Nothing in Buffer")
            counter -= 1
    except BaseException:
        print("Radio not connected?\n")
        pass


def temperature_sensor(): # uses board.SCL and board.SDA
    print(TMP_117.get_temperature())

def get_next_alarm_time(curr_hr, curr_min):
    next_hr = None
    next_min = None

    for i in WAKE_UP_WINDOW_MINS:
        if (i > curr_min):
            next_min = i
            break
    if next_min is None:
        next_min = WAKE_UP_WINDOW_MINS[0]
        # Current time is above last minute time, so we need to set for the next hr
        for i in WAKE_UP_WINDOW_HRS:
            if (i > curr_hr):
                next_hr = i
                break
        if next_hr is None:
            next_hr = WAKE_UP_WINDOW_HRS[0]
    else:
        next_hr = curr_hr
    
    return (next_hr, next_min)

def admin_menu():

    print("Admin mode:\n")
    print("1\tDate/Time")
    print("2\tmount SD Flash")
    print("3\tAvailable Storage")
    print("4\tlist Files on SD")
    print("5\tGPS I2C NMEA")
    print("6\tGPS UART RTCM3")
    print("7\tXBee Radio - UART")
    print("8\tTemperature")
    print("9\tBatV")
    print("11\tDelete all SD data")
    print("12\tPrint Unsent Files")
    print("13\tSystem Shutdown")
    
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
    elif c == "6":
        print("Reading NMEA Messages from GPS (I2c)")
        gps_i2c()
    elif c =="6":
        print("Reading RTCM3 Messages from GPS (UART2)")
        gps_uart()
    elif c == "7":
        print("Testing XBee Radio Module is active.")
        radio_test()
    elif c == "8":
        print("Temperature Sensor Reading:")
        temperature_sensor()
    elif c == "9":
        print("Battery Voltage: ")
        print(read_bat_voltage())
    elif c == "10":
        print("Accelerometer Slope:")
        accelerometer_slope()
    elif c == "11":
        yesno = input("Delete all data? (y/n) ")
        if yesno == "y" :
            print("REMOVING ALL DATA")
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
        elif yesno == "n":
            pass
        else:
            logger.warning("Please enter a valid command.")
            return
            
    elif c == "12":
        # print every unsent datafile
        import Drivers.SPI_SD
        logger.info("printing unsent data")
        try:
            files = os.listdir("/sd/data_entries/")
            for file in files :
                with open("/sd/data_entries/" + file, "r") as fd:
                    print(fd.readline() )
            print("DONE")
        except OSError:
            logger.warning("SD Chip not mounted.\n Files not available.")
            return
        
    # Ensure Future Alarm is Set BEFORE completely shutting down.
    elif c == "13":
        print("Setting Next Alarm...")
        
        (YY,MM, DD, hh, mm, ss, wday, yday, dst) = RTC_DEVICE.datetime
        logger.info("Current Time: %d:%d", hh, mm)
        nextwake = get_next_alarm_time(hh, mm)

        RTC_DEVICE.alarm1 = (struct_time([YY,MM,DD,nextwake[0],nextwake[1],0,wday,yday,dst]), "daily")
        logger.info("Next wake time = %d:%d", RTC_DEVICE.alarm1[0][3], RTC_DEVICE.alarm1[0][4])
        RTC_DEVICE.alarm1_interrupt = True

        print("SHUTTING DOWN...\nSafe to Unplug")
        sys.exit(0)
        
        
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

    gc.collect()
    logger.info("DEVICE IN NORMAL MODE")
    exec(open('./main.py').read())

