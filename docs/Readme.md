# Icetracker firmware for rover and base station 2022/3

see glacsweb.org for more details
This mainly circuitpython code is designed to run the icetrackers we produced to monitor glaciers using Ublox M9P GNSS units.
It does the following:
 * wakes up the units at regular intervals (RTC enables the PSU)
 * during GPS fixes the base feeds RTCM messages from the GPS to the radio
 * when rovers get a fix they send the data back to the base
 * at 12:00 and 24:00 the base sends all unsent data to the server in Southampton


## Circuitpython
designed to run on circuitpython - tested on version 8
needs modified GPS library, temperature and DS2131 RTC libraries

## Hardware
Uses Thing Plus SAMD51, Sparkfun M9P GPS, Adafruit FONA and XTSD flash/SD, DIGI SX868 radio.
Sparkfun SWARM untested

## Docs
To make html docs run `./make.bat html`.
Other formats can be made in a very similar way (run `make.bat` for options)
