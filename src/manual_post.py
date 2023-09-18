# Manual AT HTTP post

from adafruit_fona.adafruit_fona import FONA
import adafruit_fona.adafruit_fona_network as network
import adafruit_fona.adafruit_fona_socket as cellular_socket
from Drivers.SPI_SD import *
import time
from Drivers.PSU import * #EVERYTHING FROM THIS IS READONLY (you can use write functions, but cannot actually modify a variable)
from config import *
import json
import adafruit_requests as requests
import asyncio
import struct
import os
from microcontroller import watchdog
from watchdog import WatchDogMode
import adafruit_logging as logging

logger = logging.getLogger("BASE")

CMD_AT = b"AT"
REPLY_OK = b"OK"
REPLY_DN = b"DOWNLOAD"

SERVER_URL = "http://marc.ecs.soton.ac.uk/postin"

http_payload = '{"sats": 12, "temp": 2.35, "altitude": 105.637, "timestamp": "2023-09-01T15:01:02", "batv": 3.92, "latitude": "64.1024530713333333", "rover_id": 19, "longitude": "-16.3378673346666667"}'
# json_payload = bytearray(http_payload)
# http_payload = [{"batv": "3.92", "latitude": "64.1024530713333333", "rover_id": "19", "longitude": "-16.3378673346666667"}]
# http_payload = ["abcdef-glacsweb"]
# http_payload = []

def http_post(payload) -> bool:

    logger.info("SETTING UP URL")
    # print(fona._send_check_reply(b"AT+HTTPPARA=\"URL\",\"http://marc.ecs.soton.ac.uk/postin\"",reply=REPLY_OK))
    if not fona._send_check_reply(b"AT+HTTPPARA=\"URL\",\"http://marc.ecs.soton.ac.uk/postin\"",reply=REPLY_OK):
        return False       # set HTTP parameters value
    time.sleep(0.1)

    logger.info("PROVIDING CONTENT TYPE")
    # print(fona._send_check_reply(b"AT+HTTPPARA=\"CONTENT\",\"text/plain\"",reply=REPLY_OK))
    # if not fona._send_check_reply(b"AT+HTTPPARA=\"CONTENT\",\"text/plain\"",reply=REPLY_OK):
    if not fona._send_check_reply(b"AT+HTTPPARA=\"CONTENT\",\"application/json\"",reply=REPLY_OK):
    # if not fona._send_check_reply(b"AT+HTTPPARA=\"CONTENT\",\"x-www-form-urlencoded\"",reply=REPLY_OK):
        return False        # set HTTP parameters value
    time.sleep(0.1)


    logger.info("PROVIDING PAYLOAD")

    # # print(str(payload))
    # print(str(len(payload)))
    # print(fona._uart_write(b"AT+HTTPDATA=str(len(payload)),5000"))
    # print( fona._send_check_reply(b"AT+HTTPDATA=str(len(payload)),5000",reply=REPLY_OK))
    if not fona._send_check_reply(b"AT+HTTPDATA="+str(len(payload))+",10000",reply=REPLY_DN): # - Fails here unsupported types
    # while True:
    #     # print(fona._send_check_reply(b"AT+HTTPDATA=str(len(payload)),100000",reply=REPLY_OK))
    #     print(fona._send_check_reply(b"AT+HTTPDATA=192,5000",reply=REPLY_OK))
    #     time.sleep(0.1)
        return False      # input HTTP data
    else:
        # fona._uart_write(bytearray(payload[0]))
        fona._uart_write(str(json.loads(payload)).encode())

    time.sleep(0.1)

    

    logger.info("POSTING DATA")
    if not fona._send_check_reply(b"AT+HTTPACTION=1",reply=REPLY_OK):
        return False   # HTTP method action
    time.sleep(0.1)

    logger.info("READING SERVER RESPONSE")

    if not fona._send_check_reply(b"AT+HTTPREAD",reply=REPLY_OK):
        return False       # Read HTTP Server Response
    time.sleep(0.1)

    logger.info("TERMINATING HTTP SERVICES")
    if not fona._send_check_reply(b"AT+HTTPTERM",reply=REPLY_OK):
        return False       # Terminate HTTP service
    time.sleep(0.1) 

    return True


# def main():
    # print(len(http_payload))
    # print(str(json.loads(http_payload)).encode())
    # print((json.loads(http_payload)))

# if __name__ == '__main__':
#     main()
    
if __name__ == '__main__':
    
    logger.info("ENABLING GSM COMMS")

    fona = FONA(GSM_UART, GSM_RST_PIN, debug=False)
    
    logger.info("FONA initialized")

    # fona._send_ckeck_reply(b"ATE0",reply=fona.REPLY_OK)
    # print(fona.network_status)
    # print(fona._uart_write(CMD_AT))
    fona._send_check_reply(CMD_AT,reply=REPLY_OK) # True # sends data to fona - validates if true - send AT - expecting response OK - received True 
    # time.sleep(0.1)
    # print(fona._read_line()) #(0, b'')
    # print(fona._uart_write(b"ATE0"))
    # print(fona._read_line())
    (fona._send_check_reply(b"ATE0",reply=REPLY_OK)) # using send_check_reply alone responds with OK which means echoing is now turned off.
    # time.sleep(0.1)
    # print(fona._read_line()) # reads multiple lines into the buffer - optionally prints the buffer after reading

    # enable gprs - using apn
    while not fona.gprs:
        fona.set_gprs((SECRETS["apn"], SECRETS["apn_username"], SECRETS["apn_password"]),enable=True)
    print(fona.gprs) # retruns false - need to enable using set_gprs() which needs apn, username and pw
    logger.info("GPRS ENABLED")

    # AT+HTTPCPOST
    # print(fona.local_ip)

    (fona._send_check_reply(b"AT+HTTPINIT",reply=REPLY_OK)) # Initialise HTTP service return True
    time.sleep(0.1)
    (fona._send_check_reply(b"AT+HTTPPARA=\"CID\",1",reply=REPLY_OK)) # HTTPPARA paramter - sets the bearer profile ID of the connection - returns true
    logger.info("HTTP SERVICES ENABLED")


    # print(fona._send_check_reply(b"AT+HTTPPARA=\"URL\",\"http://marc.ecs.soton.ac.uk/postin\"",reply=REPLY_OK)) # we want to provide a URL instead of CID
    (http_post(http_payload))
