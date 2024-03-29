from config import *
import config
import os
import Drivers.PSU as PSU
from Drivers.I2C_Devices import RTC_DEVICE
from Drivers.SPI_SD import *
import traceback
from microcontroller import watchdog
from watchdog import WatchDogMode
import adafruit_logging as logging
from time import localtime, mktime, struct_time
import rtc
import supervisor

logger = logging.getLogger("MAIN_FILE")
rtc.set_time_source(RTC_DEVICE)

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

if __name__ == "__main__":
    if ADMIN_IO.value:
        #Debug mode set
        logger.info("Alarm Time: %d:%02d", RTC_DEVICE.alarm1[0][3], RTC_DEVICE.alarm1[0][4])
        config.DEBUG["WATCHDOG_DISABLE"] = True
        config.GLOBAL_FAILSAFE_TIMEOUT = 99999
        print("""BOOT_MENU:
        1 - normal boot (no timeouts)
        2 - admin mode
        3 - GSM test
        4 - Manual GSM Test""")
        input = input()
        if input == "2":
            supervisor.set_next_code_file("./Utility/adminmode.py")
            supervisor.reload()
        if input == "3":
            print("GSM SELECTED")
            exec(open('./Utility/GSM.py').read())
        if input == "4":
            print("Manual GSM Test Selected")
            exec(open('Comms_AT.py').read())
    else:
        #Perform failsafe procedures (timeouts, watchdog, etc.)
        if RTC_DEVICE.alarm1_status and RTC_DEVICE.alarm_is_in_future():
            logger.warning("Alarm is alarming but set to future, presumed abnormal reset")
            PSU.shutdown()

        (YY,MM, DD, hh, mm, ss, wday, yday, dst) = RTC_DEVICE.datetime
        logger.info("Current Time: %d:%d", hh, mm)
        nextwake = get_next_alarm_time(hh, mm)

        RTC_DEVICE.alarm1 = (struct_time([YY,MM,DD,nextwake[0],nextwake[1],0,wday,yday,dst]), "daily")
        logger.info("Next wake time = %d:%d", RTC_DEVICE.alarm1[0][3], RTC_DEVICE.alarm1[0][4])
        RTC_DEVICE.alarm1_interrupt = True

        if not DEBUG["WATCHDOG_DISABLE"]:
            watchdog.timeout = 16
            watchdog.mode = WatchDogMode.RESET
            watchdog.feed()
            logger.info("WATCHDOG_ENABLED")
    
    try:
        #Normal boot
        dirs = os.listdir("/sd/")

        if "data_entries" not in dirs:
            os.mkdir("/sd/data_entries")
        if "sent_data" not in dirs:
            os.mkdir("/sd/sent_data")
        if "invalid_data" not in dirs:
            os.mkdir("/sd/invalid_data")
        
        if DEVICE_ID >= 100:
            if RTC_DEVICE.datetime[3] in COMMS_TIME:
                logger.info('Comms Time')
                exec(open('Comms_AT.py').read())
                # exec(open('./Comms.py').read())
            else:
                logger.info("run base")
                exec(open('./Base.py').read())
        else:
            logger.info("run rover")
            exec(open('./Rover.py').read())
    except BaseException as error:
        if type(error) is KeyboardInterrupt:
            logger.warning(traceback.format_exception(type(error), error, error.__traceback__, None, False))
        else:
            logger.critical(traceback.format_exception(type(error), error, error.__traceback__, None, False))
            with open("/sd/error_log.txt","a") as file:
                traceback.print_exception(type(error),error,error.__traceback__,None,file,False)
            #traceback.print_exception(type(error),error,error.__traceback__,None,None,False)
    finally:
        PSU.shutdown()