import busio
from os import statvfs, listdir, stat, remove, rmdir, mkdir
import board
import storage
import digitalio
import time
import adafruit_sdcard
import adminmode

from Drivers.TMP117 import TMP_117

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
cs = digitalio.DigitalInOut(board.D4)


def diskfree(path):
    """Checks available storage in either filesystem or SD card

    Args:
        path (String): path on the OS to read availble storage, throws an error if invalid.
    """
    try:
        info = statvfs(path)
        return(info[0] * info[3])
    except OSError:
        print("Invalid path, please try again.")



def mount_SD():
    """Attempts to mount SPI SMT SD Card as a virtual Filesystem to be read and written to.
        Uses SPI to communicate with the Thing+.
        Throws an error if SD card is not detected. 
    """
    try:
        print("Mounting to SD Card")
        spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
        fs = adafruit_sdcard.SDCard(spi, cs)
        vfs = storage.VfsFat(fs)
        storage.mount(vfs,"/sd")
        print("\nSuccessfully Mounted")

    except OSError:
        print("SD Card not active, please try again.")


def print_directory(path, tabs=0):
    """Checks available directories and files on the SD card if mounted successfully. 

    Args:
        path (String): path on the OS to read existing files/directories, throws an error if invalid.
        tabs (int, optional): _description_. Defaults to 0.
    """
    print("Files on filesystem:")
    print("====================")

    for file in listdir(path):
        stats = stat(path + "/" + file)
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


def make_dir(path):
    """Helper function to create a directory on the SD card.

    Args:
        path (String): path on the OS to read existing files/directories, throws an error if invalid.
    """
    try:
        mkdir(path)
        print("Directory created.")
    except OSError:
        print("Directory already exists!")


def remove_dir(path):
    """Helper function to remove an already existing directory on the SD card.

    Args:
        path (String): path on the OS to read existing files/directories, throws an error if invalid.
    """
    try:
        rmdir(path)
        print("Directory deleted.")
    except OSError:
        print("Directory doesn't exist.")


def remove_file(path):
    """Helper function to remove an already existing file on the SD card.

    Args:
        path (String): path on the OS to read existing files/directories, throws an error if invalid.
    """
    try:
        remove(path)
        print("File removed.")
    except OSError:
        print("File doesn't exist.")


def read_file(path):
    """Helper function to read the contents of an already existing file on the SD card.

    Args:
        path (String): path on the OS to read existing files/directories, throws an error if invalid.
    """
    with open(path, "r") as f:
        print("Printing lines in file:")
        line = f.readline()
        while line != '':
            print(line)
            line = f.readline()


def write_to_file(path, data):
    """Helper function to write data to the contents of an already existing file on the SD card.

    Args:
        path (String): path on the OS to read existing files/directories, throws an error if invalid.
        data (tbc): data recorded from the various drivers to be written on SD card instead of filesystem due to lack of storage
    """
    with open(path, "w") as f:
        f.write("Greetings on the SD Card.!\r\n")


def logger(path):
    """ Test function to log data onto the 'virtual' filesystem without the need to use boot.py.

    Args:
        path (String): path on the OS to read existing files/directories, throws an error if invalid.
    """
    print("Logging Temperature via TMP117")
    count = 10
    while count > 0:
        with open(path, "a") as file:
            led.value = True

            # print("Temperature = %0.1fC" % TMP_117.temperature)
            file.write("%0.1fC\n" % TMP_117.temperature)
            led.value = False

        time.sleep(1)
        count -= 1

def main():
    mount_SD()
    print(f"Flash size bytes free: ",diskfree("/"))
    print(f"SPI SMT SD Card bytes free: ",diskfree("/sd"))
    # remove_file("/sd/test.txt")
    # make_dir("/sd/sent_data")
    print_directory("/sd")
    # logger("/sd/data_entries/Temperature.txt")
    read_file("/sd/data_entries/Temperature.txt")

if __name__ == '__main__':
    main()
    