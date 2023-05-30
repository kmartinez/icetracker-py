from Drivers.PSU import *
from Drivers.RTC import *
from Drivers.I2C_Devices import *
from time import mktime, struct_time, localtime, sleep
WAKE_UP_WINDOW_HRS  = [0, 3, 6, 9, 12, 15, 18, 21] 
# WAKE_UP_WINDOW_MINS = [0,5,10,15,20,25,30,35,40,45,50,55]
WAKE_UP_WINDOW_MINS = 
[0,3,6,9,12,15,18,21,24,27,30,33,36,39,42,45,48,51,54,57]
WAKE_UP_WINDOW_SECS = [0,15,30,45]

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

def get_next_alarm_sec(ss):
    nexttime = None

    if ( ss in WAKE_UP_WINDOW_SECS):
            position = WAKE_UP_WINDOW_SECS.index(ss)
            next_position = position + 1
            if (next_position > (len(WAKE_UP_WINDOW_SECS)-1)):
                next_position = 0
            nexttime = WAKE_UP_WINDOW_SECS[next_position]
    else:
        for i in WAKE_UP_WINDOW_SECS:
            if( i > ss):
                nexttime = i
                break
        if nexttime == None:
            nexttime = 0
    return nexttime

def set_next_alarm(hour):
    RTC_DEVICE.alarm1[0][3] = hour
    RTC_DEVICE.alarm1[0][4] = 0
    RTC_DEVICE.alarm1[0][5] = 0



if __name__ == '__main__':
    (YY, MM, DD, hh, mm, ss, wday, yday, dst) = RTC_DEVICE.datetime
    # nextwake_HH = get_next_alarm_hour(hh)
    nextwake_MM = get_next_alarm_min(mm)
    # nextwake_SS = get_next_alarm_sec(ss)
    # print(nextwake_HH)
    print(nextwake_MM)
    # print(nextwake_SS)
    # RTC_DEVICE.alarm1 = 
(struct_time([YY,MM,DD,nextwake_HH,0,0,wday,yday,dst]), "monthly")
    RTC_DEVICE.alarm1 = 
(struct_time([YY,MM,DD,hh,nextwake_MM,0,wday,yday,dst]), "monthly")
    # RTC_DEVICE.alarm1 = 
(struct_time([YY,MM,DD,hh,mm,nextwake_SS,wday,yday,dst]), "monthly")
    # RTC_DEVICE.alarm1 = (localtime(mktime(RTC_DEVICE.datetime)+60), 
"monthly")
    # set_next_alarm(nextwake)
    print(RTC_DEVICE.alarm1)
    # print(RTC_DEVICE.alarm2)
    # if RTC_DEVICE.alarm1_status:
    #     print("Resetting Alarm")
    #     RTC_DEVICE.alarm1_status = False
    # print("RTC DATETIME")
    # print(RTC_DEVICE.datetime)
    # print("Setting first alarm")
    # RTC_DEVICE.alarm1 = (localtime(mktime(RTC_DEVICE.datetime)+60), 
"monthly")
    # print(RTC_DEVICE.alarm1)
    # print("ALARM STATUS: {}".format(RTC_DEVICE.alarm1_status))
    # while True:


    while True:
        if RTC_DEVICE.alarm1_status:
            if RTC_DEVICE.alarm_is_in_future():
                logger.critical("Abnormal reset detected!!! Shutting 
device down")
                shutdown()
            else:
                print("ALARM STATUS: {}".format(RTC_DEVICE.alarm1_status))
                print("Device is awake")
                print(RTC_DEVICE.datetime)
                # sleep(60)
                for i in range(30):
                    print(i)
                    sleep(1)
                print("Updating Future Alarm")
                (YY, MM, DD, hh, mm, ss, wday, yday, dst) = 
RTC_DEVICE.datetime
                nextwake_MM = get_next_alarm_min(mm)
                RTC_DEVICE.alarm1 = 
(struct_time([YY,MM,DD,hh,nextwake_MM,0,wday,yday,dst]), "monthly")
                print(RTC_DEVICE.alarm1)
                shutdown()


    # RTC_DEVICE.alarm1_interrupt = True
    
