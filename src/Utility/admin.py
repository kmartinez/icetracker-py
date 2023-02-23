import os
import board
import busio
import adafruit_mcp9808 # replaced with tmp117
import adafruit_lc709203f
from adafruit_datetime import datetime

# TX, RX
RADIO_UART = busio.UART(board.D11, board.D10, baudrate=9600, receiver_buffer_size=2048) 
''' Radio UART for communications'''
GPS_UART = busio.UART(board.A1, board.A2, baudrate=115200, receiver_buffer_size=2048)
''' GPS NMEA UART for communications '''
RTCM3_UART = busio.UART(board.TX, board.RX, baudrate=115200, receiver_buffer_size=2048)
''' GPS RTCM3 UART '''

def diskfree():
    info = os.statvfs("/")
    return(info[0] * info[3])
    print(f"bytes free: ",diskfree())   # redundant

def printdataentries():
    """ Check if directory exists """
    PATH = "/data_entries"
    
    try:
        if os.path.exists(PATH):
            print(os.listdir("/data_entries"))
    except BaseException:
        print("Directory doesn't exist, create one.")
        # os.mkdir(PATH) # stuck in read-only mode so won't work
        pass
def voltagereadings():
    i2c = board.STEMMA_I2C()
    lc7 = adafruit_lc709203f.LC709203F(i2c)
    try:
        print("Battery Voltage: %0.2fV" % lc7.cell_voltage)
    except BaseException:
        print("Sensor not connected.")
        pass

def gps_test():
    print("Checking uart connection")
    pass

def radio_test():
    print("Checking uart connection")
    
    pass

def temp():
    i2c = board.I2C()  # uses board.SCL and board.SDA
    mcp = adafruit_mcp9808.MCP9808(i2c)
    print("%.2f C" % mcp.temperature)

def adminmenu():
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
        print(f"data entries: ",printdataentries())
    elif c == "5":
        print(temp())
    elif c == "6":
        print(voltagereadings())
    elif c == "7":
        # print(radio_test())
        radio_test()
    else:   
        print("command not found")


# while True:
#     adminmenu()
#     admincmd(input())