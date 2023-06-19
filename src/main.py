from config import *
import os
import Drivers.PSU as PSU
from Drivers.I2C_Devices import RTC_DEVICE, shutdown
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

# to be deleted? TIME_INTERVAL = 20
# to be deleted? WAKEUP_INTERVAL = 10
RTC_TIMEOUT = 90

COMMS_TIME = [0, 3, 6, 9, 12,13, 15, 18, 21] 

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
                # hh = RTC_DEVICE.datetime.tm_hour + 1
            nexttime = WAKE_UP_WINDOW_MINS[next_position]
    else:
        for i in WAKE_UP_WINDOW_MINS:
            if( i > mm):
                nexttime = i
                break
        if nexttime == None:
            nexttime = 0
    return nexttime

# def get_next_alarm_min(mm, hh):
#     nexttime = None
#     hour = hh
#     if ( mm in WAKE_UP_WINDOW_MINS):
#             position = WAKE_UP_WINDOW_MINS.index(mm)
#             # next_position = position + 1
#             if (next_position > (len(WAKE_UP_WINDOW_MINS)-1)):
#                 next_position = 0
#             nexttime = WAKE_UP_WINDOW_MINS[next_position]
#             hour = hh + 1
#     else:
#         for i in WAKE_UP_WINDOW_MINS:
#             if( i > mm):
#                 nexttime = i
#                 break
#         if nexttime == None:
#             nexttime = 0
#     return nexttime, hour



if __name__ == "__main__":
    #   start_time = time.monotonic()

    if ADMIN_IO.value:
        supervisor.set_next_code_file("./Utility/adminmode.py")

    logger.info("Current Time")
    print(RTC_DEVICE.datetime)
    (YY, MM, DD, hh, mm, ss, wday, yday, dst) = RTC_DEVICE.datetime
    nextwake_MM = get_next_alarm_min(mm)
    nextwake_HH = get_next_alarm_hour(hh)
    logger.info("NEXT WAKEUP TIME (Hour) {}".format(nextwake_HH))
    # changed daily into monthly - should it be running at hourly??
    # RTC_DEVICE.alarm1 = (struct_time([YY,MM,DD,nextwake_HH,0,0,wday,yday,dst]), "daily")

    # (YY, MM, DD, hh, mm, ss, wday, yday, dst) = RTC_DEVICE.datetime
    # nextwake_MM=  get_next_alarm_min(mm)
    # print(nextwake_MM)
    # #   print(hour)
    # logger.info("NEXT WAKEUP TIME (Minutes) {}".format(nextwake_MM))
    # RTC_DEVICE.alarm1 = (struct_time([YY,MM,DD,hh,nextwake_MM,0,wday,yday,dst]), "hourly")
    print(RTC_DEVICE.alarm1)

      # print("Setting First Alarm")
      # first_alarm_time = localtime(mktime(RTC_DEVICE.datetime)+TIME_INTERVAL)

      # RTC_DEVICE.alarm1 = (first_alarm_time, "monthly")
    print(RTC_DEVICE.alarm1_status)
    if RTC_DEVICE.alarm1_status:
        if RTC_DEVICE.alarm_is_in_future():
            logger.critical("Abnormal reset detected!!! Shutting device down")
            shutdown()
        else:

            (YY, MM, DD, hh, mm, ss, wday, yday, dst) = RTC_DEVICE.datetime
            nextwake_MM = get_next_alarm_min(mm)
            nextwake_HH = get_next_alarm_hour(hh)
            logger.info("NEXT WAKEUP TIME (Hour) {}".format(nextwake_HH))
            # changed daily into monthly - should it be running at hourly??
            RTC_DEVICE.alarm1 = (struct_time([YY,MM,DD,nextwake_HH,0,0,wday,yday,dst]), "daily")


            # (YY, MM, DD, hh, mm, ss, wday, yday, dst) = RTC_DEVICE.datetime
            # nextwake_MM = get_next_alarm_min(mm)
            # logger.info("NEXT WAKEUP TIME (Minutes) {}".format(nextwake_MM))
            # RTC_DEVICE.alarm1 = (struct_time([YY,MM,DD,hh,nextwake_MM,0,wday,yday,dst]), "hourly")
            print(RTC_DEVICE.alarm1)
        RTC_DEVICE.alarm1_interrupt = True

      # RTC_DEVICE.alarm1_interrupt = True
    #   print("I'm here\n")
    #   if RTC_DEVICE.alarm1_status
    #   end_time = time.monotonic()
    #   print(end_time - start_time)

    if not DEBUG["WATCHDOG_DISABLE"]:
        watchdog.timeout = 16
        watchdog.mode = WatchDogMode.RESET
        watchdog.feed()
        #  PSU.shutdown()
    try:
        if "data_entries" not in os.listdir("/sd/"):
            os.mkdir("/sd/data_entries")
        if "sent_data" not in os.listdir("/sd/"):
            os.mkdir("/sd/sent_data")
         #input()
        if RTC_DEVICE.datetime[3] in COMMS_TIME and RTC_DEVICE.datetime[4] < 30:
            logger.info('Comms Time')
            exec(open('./Comms.py').read())
        else:
            logger.info("not COMMS time")
            if DEVICE_ID == 100:
                logger.info("run base")
                exec(open('./Base.py').read())
            else:
                logger.info("run rover")
                exec(open('./Rover.py').read())
    except BaseException as error:
        #  logger.critical(traceback.format_exception(type(error), error, error.__traceback__, None, False))
        with open("/sd/error_log.txt","a") as file:
            traceback.print_exception(type(error),error,error.__traceback__,None,file,False)
        traceback.print_exception(type(error),error,error.__traceback__,None,None,False)
    finally:
        shutdown()
