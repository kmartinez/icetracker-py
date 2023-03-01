import board
import busio
# from digitalio import DigitalInOut
import time
import digitalio
import storage
import sdcardio
import adafruit_sdcard
import os
import adafruit_tmp117
from adminmode import diskfree

# SPI_CS = digitalio.DigitalInOut(board.D4)
# SPI_CS = board.D4
i2c = board.STEMMA_I2C()
tmp = adafruit_tmp117.TMP117(i2c)
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT


cs = digitalio.DigitalInOut(board.D4)
print(storage.getmount("/"))
print("Bytes Available: ", diskfree())


# try:
def mount_SD():
    try:
        print("Mounting to SD Card")
        spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
        # fs = sdcardio.SDCard(spi, SPI_CS)
        fs = adafruit_sdcard.SDCard(spi, cs)

        # vfs = "/measurements"
        vfs = storage.VfsFat(fs)
        storage.mount(vfs,"/sd")
        print("\nSuccessfully Mounted")
    except OSError:
        print("SD Card not active, please try again.")
    # SPI_CS: False

def read_file():
    with open("/sd/temperature.txt", "r") as f:
        print("Printing lines in file:")
        line = f.readline()
        while line != '':
            print(line)
            line = f.readline()


def write_to_file():
    with open("/sd/log.txt", "w") as f:
        f.write("Greetings on the SD Card.!\r\n")

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


def logger():
    print("Logging Temperature via TMP117")
    while True:
        with open("/sd/temperature.txt", "a") as file:
            led.value = True

            print("Temperature = %0.1fC" % tmp.temperature)
            file.write("%0.1fC\n" % tmp.temperature)
            led.value = False

        time.sleep(1)


def main():

    mount_SD()
    
    print(storage.getmount("/sd"))
    print("Bytes Available: ", diskfree())

    print("Files on filesystem:")
    print("====================")
    print_directory("/sd")

    # try:
    #     logger()
    # except BaseException:
    #     print("Can't detect sensor.")
    # logger()

    # write_to_file()

    read_file()

    # pass

    # except OSError:
    #     print("\n------- Not Accessible --------\n")
    #     pass
if __name__ == '__main__':
    # from adminmode import *
    main()

