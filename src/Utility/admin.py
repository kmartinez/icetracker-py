import os
import board
import busio
from analogio import AnalogIn
import time
import adafruit_mcp9808 # replaced with tmp117
import adafruit_lc709203f
from adafruit_datetime import datetime

# TX, RX
i2c = board.STEMMA_I2C()
pin_ip = AnalogIn(board.A3)
lc7 = adafruit_lc709203f.LC709203F(i2c)

def diskfree():
    info = os.statvfs("/")
    return(info[0] * info[3])
    print(f"bytes free: ",diskfree())   # redundant

def print_data_entries():
    """ Check if directory exists """
    PATH = "/data_entries"
    
    try:
        if os.path.exists(PATH):
            print(os.listdir("/data_entries"))
    except BaseException:
        print("Directory doesn't exist, create one.")
        # os.mkdir(PATH) # stuck in read-only mode so won't work
        pass

    """ Nodes could have been damaged due to using the wrong polarity? """
def voltage_readings(pin):
    global lc7 
    # TODO: cannot use this sensor, maybe faulty? Sensor will be replaced with the same
    # input method used previously with a couple of resistors in the form of a potential divider.
    # Will be reading the inputs via an ADC input, just need to decide on the actual pin to use.
    """ DEPRECATED AT THE MOMENT """
    # try:
    # print("Battery Voltage: %0.3fV" % (1+lc7.cell_voltage))
    # print("Battery Percentage: %0.1F %%" %lc7.cell_percent)
    # except BaseException:
    #     print("Sensor not connected.")
    #     pass
    # return ("Vbat: {.2f}V".format((pin_ip.value * 3.3) / 65536))
    """ BAT V readings are inconsistent """
    print((pin.value * 3.3) / 65536)

def gps_test():
    print("Checking uart connection")
    GPS_UART = busio.UART(board.A1, board.A2, baudrate=115200, receiver_buffer_size=2048)
    ''' GPS NMEA UART for communications '''
    RTCM3_UART = busio.UART(board.TX, board.RX, baudrate=115200, receiver_buffer_size=2048)
    ''' GPS RTCM3 UART '''

    try:
        if GPS_UART is not None:
            print(GPS_UART.readline())
        else:
                print("Nothing in Buffer")
    except BaseException:
        print("GPS not detected")
        pass

def radio_test():
    print("Checking uart connection")
    try:
        RADIO_UART = busio.UART(board.D11, board.D10, baudrate=9600, receiver_buffer_size=2048) 
        ''' Radio UART for communications'''
        counter = 10
        while counter > 0:
            if RADIO_UART is not None:
                print(RADIO_UART.readline())
            else:
                print("Nothing in Buffer")
            counter -= 1
    except BaseException:
        print("Radio not connected.\n Check pins and SMA antenna connections.")
        pass

def temp():
    i2c = board.I2C()  # uses board.SCL and board.SDA
    mcp = adafruit_mcp9808.MCP9808(i2c)
    print("%.2f C" % mcp.temperature)

def admin_menu():
    print("1\tdatetime")
    print("2\tGPS test")
    print("3\tDisk free")
    print("4\tprint data-entries")
    print("5\tTemperature")
    print("6\tVoltage")
    print("7\tRadio test")

def admincmd(c):
    if c == "1":
        # may need to update this using gps time.
        print(f"the datetime is ", datetime.now())
    elif c == "2":
        print("printing GPS")
        gps_test()
    elif c == "3":
        print(f"disk free: ",diskfree())
    elif c == "4":
        print(f"data entries: ",print_data_entries())
    elif c == "5":
        print(temp())
    elif c == "6":
        while True:
            # print(voltage_readings())
            voltage_readings(pin_ip)
            time.sleep(1)
    elif c == "7":
        # print(radio_test())
        radio_test()
    else:   
        print("command not found")


# while True:
#     adminmenu()
#     admincmd(input())