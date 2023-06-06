"""run by circuitpython upon startup on every node.
It first checks if the module was reset abnormally, and shuts down gracefully if it did.
Otherwise, it determines if it is configured as a base or a rover, where it will then execute the respective code
"""

from config import *
import os
import Drivers.PSU as PSU
# from Drivers.RTC import RTC_DEVICE
from Drivers.I2C_Devices import RTC_DEVICE
from Drivers.SPI_SD import *
import traceback
from microcontroller import watchdog
from watchdog import WatchDogMode
import adafruit_logging as logging
from time import localtime, mktime, struct_time
import rtc
import supervisor
import gc

logger = logging.getLogger("MAIN_FILE")
rtc.set_time_source(RTC_DEVICE)

TIME_INTERVAL = 20
WAKEUP_INTERVAL = 10

WAKE_UP_WINDOW_HRS  = [0, 3, 6, 9, 12, 15, 18, 21] 
# WAKE_UP_WINDOW_MINS = [0,5,10,15,20,25,30,35,40,45,50,55]
WAKE_UP_WINDOW_MINS = [0,3,6,9,12,15,18,21,24,27,30,33,36,39,42,45,48,51,54,57]

def get_next_alarm_hour(hh):
    nexttime = None

    if ( hh in WAKE_UP_WINDOW_HRS):
            position = WAKE_UP_WINDOW_HRS.index(hh)
            next_position = position + 1
            if (next_position > (len(WAKE_UP_WINDOW_HRS)-1)):
                next_position = 0
            nexttime = WAKE_UP_WINDOW_HRS[next_position]
    else:
        for i in WAKE_UP_WINDOW_HRS:
            if( i > hh):
                nexttime = i
                break
        if nexttime == None:
            nexttime = 0
    return nexttime

def get_next_alarm_min(mm):
    nexttime = None

    if ( mm in WAKE_UP_WINDOW_MINS):
            position = WAKE_UP_WINDOW_MINS.index(mm)
            next_position = position + 1
            if (next_position > (len(WAKE_UP_WINDOW_MINS)-1)):
                next_position = 0
            nexttime = WAKE_UP_WINDOW_MINS[next_position]
    else:
        for i in WAKE_UP_WINDOW_MINS:
            if( i > mm):
                nexttime = i
                break
        if nexttime == None:
            nexttime = 0
    return nexttime

if __name__ == "__main__":
      if ADMIN_IO.value:
            supervisor.set_next_code_file("./Utility/adminmode.py")

      logger.info("Current Time")
      print(RTC_DEVICE.datetime)
      (YY, MM, DD, hh, mm, ss, wday, yday, dst) = RTC_DEVICE.datetime
      nextwake_MM = get_next_alarm_min(mm)
      logger.info("NEXT WAKEUP TIME (Minutes) {}".format(nextwake_MM))
      RTC_DEVICE.alarm1 = (struct_time([YY,MM,DD,hh,nextwake_MM,0,wday,yday,dst]), "monthly")
      print(RTC_DEVICE.alarm1)


      # print("Current Time")
      # print(RTC_DEVICE.datetime)

      # print("Setting First Alarm")
      # first_alarm_time = localtime(mktime(RTC_DEVICE.datetime)+TIME_INTERVAL)

      # RTC_DEVICE.alarm1 = (first_alarm_time, "monthly")

      if RTC_DEVICE.alarm1_status:
         if not RTC_DEVICE.alarm_is_in_future():
            logger.critical("Abnormal reset detected!!! Shutting device down")
            PSU.shutdown()
         else:
            # RTC_DEVICE.alarm1 = (localtime(mktime(RTC_DEVICE.alarm1[0])+WAKEUP_INTERVAL), "monthly")
            (YY, MM, DD, hh, mm, ss, wday, yday, dst) = RTC_DEVICE.datetime
            nextwake_MM = get_next_alarm_min(mm)
            RTC_DEVICE.alarm1 = (struct_time([YY,MM,DD,hh,nextwake_MM,0,wday,yday,dst]), "monthly")
            print(RTC_DEVICE.alarm1)
      # RTC_DEVICE.alarm1_interrupt = True

      gc.collect()

      if not DEBUG["WATCHDOG_DISABLE"]:
         watchdog.timeout = 16
         watchdog.mode = WatchDogMode.RESET
         watchdog.feed()
      try:
         # make dirs if they don't exist 
         if "data_entries" not in os.listdir("/sd/"):
            os.mkdir("/sd/data_entries")
         if "sent_data" not in os.listdir("/sd/"):
            os.mkdir("/sd/sent_data")
         # run base or rover code
         if DEVICE_ID == 0:
            logger.info("running as base")
            exec(open('./Base.py').read())
         else:
            logger.info("running as rover")
            exec(open('./Rover.py').read())
      except BaseException as error:
         logger.critical(traceback.format_exception(type(error), error, error.__traceback__, None, False))
      finally:
         PSU.shutdown()
