import board
import busio
# from digitalio import DigitalInOut
import time
import storage
import adafruit_sdcard
import os
import adafruit_tmp117
from config import *
# from adminmode import diskfree


def mount_SD(SPI_SD,CS):
    try:
        print("Mounting to SD Card")
        
        fs = adafruit_sdcard.SDCard(SPI_SD, CS)

        vfs = storage.VfsFat(fs)
        storage.mount(vfs,"/sd")
        print("\nSuccessfully Mounted")
    except OSError:
        print("SD Card not active, please try again.")


def read_file(path):
    data_entry_path = os.listdir("/sd/data_entry/" + path)
    with open(data_entry_path, "r") as f:
        print("Printing lines in file:")
        line = f.readline()
        while line != '':
            print(line)
            line = f.readline()


def write_to_file(path,data):
    with open(path, "w") as f:
        f.write(data)


def print_directory(path, tabs=0):
    for file in os.listdir(path):
        stats = os.stat(path + "/" + file)
        filesize = stats[6]
        isdir = stats[0] & 0x4000

        if filesize < 1000:
            sizestr = str(filesize) + " by"
        elif filesize < 1000000:
            sizestr = "%0.1f KB" % (filesize / 1000)
        else:
            sizestr = "%0.1f MB" % (filesize / 1000000)

        prettyprintname = ""
        for _ in range(tabs):
            prettyprintname += "   "
        prettyprintname += file
        if isdir:
            prettyprintname += "/"
        print('{0:<40} Size: {1:>10}'.format(prettyprintname, sizestr))

        # recursively print directory contents
        if isdir:
            print_directory(path + "/" + file, tabs + 1)


SPI_SD = SPI(board.SCK, board.MOSI, board.MISO)
'''SPI SMT SD CARD PINS'''

CS = DigitalInOut(board.A4)
'''SPI CS PIN'''
mount_SD(SPI_SD, CS)
