import os
import board
import adafruit_tmp117
from adafruit_datetime import datetime

def diskfree():
    info = os.statvfs("/")
    return(info[0] * info[3])
    print(f"bytes free: ",diskfree())

def printdataentries():
    print(os.listdir("/data_entries"))

def temp():
    i2c = board.I2C()  # uses board.SCL and board.SDA
    tmp117 = adafruit_tmp117.TMP117(i2c)
    print("%.2f C" % tmp117.temperature)

def adminmenu():
    print("1\tdatetime")
    print("2\tGPS test")
    print("3\tDisk free")
    print("4\tprint data-entries")
    print("5\tTemperature")

def admincmd(c):
    if c == "1":
        print(f"the datetime is ", datetime.now())

    elif c == "2":
        print("printing GPS")
    elif c == "3":
        print(f"disk free: ",diskfree())
    elif c == "4":
        print(f"data entries: ",printdataentries())
    elif c == "5":
        print(temp())
    else:
        print("command not found")


while True:
    adminmenu()
    admincmd(input())
