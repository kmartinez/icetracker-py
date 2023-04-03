import board
import busio
import supervisor
import time

import adafruit_ds3231 as DS3231

from Drivers.Swarm import *

GLOBAL_TIME_OUT = 10
COMMS_TIME = [12]
COMMS_TIME_MINUTES = [0, 15, 30, 45]

i2c = board.STEMMA_I2C()

rtc = DS3231.DS3231(i2c)

def send_message_no_waiting(message: str):
    """Sends a message and immediately returns regardless of if the message was actually
    sent to a satellite

    :param message: Message to send
    :type message: str
    """
    serialized_msg_no_checksum = "$TD " + message

    checksum_bytes = serialized_msg_no_checksum.encode('ascii')
    checksum = 0
    for b in checksum_bytes:
        checksum ^= b
    # checksum_str = format(checksum, "02x")

    # serialized_msg = serialized_msg_no_checksum + "*" + checksum_str
    serialized_msg = checksum_bytes + b'*%02X\n'%checksum
    SWARM_UART.write(serialized_msg)
    print(SWARM_UART.readline())




# TODO: 
# - Wait for bootloader 
# - Wait for Init (- check we can read:
#   $M138 DATETIME and M138 POSITION
# - Run Notify Enable such that the modem is ready to recieve messages



def wait_for_bootloader():
    global ready_to_receive
    while not ready_to_receive:
        line = SWARM_UART.readline()
        if line is not None:
            if 'M138 BOOT,RUNNING' in line:
                print('Boot complete')
                ready_to_receive = True
        else:
            continue

def wait_for_init_datetime():
    global ready_to_send
    while not ready_to_send:

        wait_for_bootloader()
        date_line = SWARM_UART.readline()
        if date_line is not None:
            if 'M138 DATETIME' in date_line:
                print("Got a fix")
                ready_to_send = True

def main():

    ''' TIMEOUT code to test if board is unable to boot and init correctly - may need to use watchdog to trigger it reset?'''

    # start_time = time.monotonic()
    
    # wait_for_init_datetime()

    # end_time = time.monotonic()


    # # Doesn't work, need something to override function - watchdog?
    # try:
    #     if (end_time - start_time) > GLOBAL_TIME_OUT:
    #         supervisor.reload() # can try microcontroller.RunMode.NORMAL & microcontroller.reset()
    # except BaseException:
    #     print("GLOBAL TIMEOUT EXCEEDED - RESTARTING")
    
    # Separating and Checking Times
    (YY, MM, DD, hh, mm, ss, wday, yday, dst) = rtc.datetime

    print("Checking RTC Calibrated")
    if YY == 2000:
        raise Exception("External RTC needs calibrating")

    print("CHECKING COMMS TIME")
    # replace hh with mm to test every 15 mins
    if mm in COMMS_TIME_MINUTES:
        print("INSIDE COMMS TIME WINDOW")

        send_message_no_waiting("THINGPLUS")
        print("Sent")
        while True:
            response = SWARM_UART.readline()
            if response is not None:
                response_relevant = response[0:]
                print(response_relevant)
                if response_relevant != b'$TD OK':
                    raise Exception("COMMS_ERROR, MSG=" + bytes.decode(response, 'utf-8'))
    else:
        print("OUTSIDE OF COMMS TIME WINDOW - MCU POWER OFF")
        supervisor.reload()
    
if __name__ == '__main__':
    main()


