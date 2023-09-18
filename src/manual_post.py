# Manual AT HTTP post

from adafruit_fona.adafruit_fona import FONA
from Drivers.SPI_SD import *
import time
from Drivers.PSU import * #EVERYTHING FROM THIS IS READONLY (you can use write functions, but cannot actually modify a variable)
from config import *
import json
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
    if not fona._send_check_reply(b"AT+HTTPPARA=\"URL\",\"http://marc.ecs.soton.ac.uk/postin\"",reply=REPLY_OK):
        return False       # set HTTP parameters value
    time.sleep(0.1)

    logger.info("PROVIDING CONTENT TYPE")
    # if not fona._send_check_reply(b"AT+HTTPPARA=\"CONTENT\",\"x-www-form-urlencoded\"",reply=REPLY_OK):
    # if not fona._send_check_reply(b"AT+HTTPPARA=\"CONTENT\",\"text/plain\"",reply=REPLY_OK):

    if not fona._send_check_reply(b"AT+HTTPPARA=\"CONTENT\",\"application/json\"",reply=REPLY_OK):
        return False        # set HTTP parameters value
    time.sleep(0.1)


    logger.info("PROVIDING PAYLOAD")
    if not fona._send_check_reply(b"AT+HTTPDATA="+str(len(payload))+",10000",reply=REPLY_DN): # - Fails here unsupported types
        return False      # input HTTP data
    else:
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

    
if __name__ == '__main__':
    
    logger.info("ENABLING GSM COMMS")

    fona = FONA(GSM_UART, GSM_RST_PIN, debug=False)
    
    logger.info("FONA initialized")


    fona._send_check_reply(CMD_AT,reply=REPLY_OK) # True # sends data to fona - validates if true - send AT - expecting response OK - received True 

    (fona._send_check_reply(b"ATE0",reply=REPLY_OK)) # using send_check_reply alone responds with OK which means echoing is now turned off.

    # enable gprs - using apn
    while not fona.gprs:
        fona.set_gprs((SECRETS["apn"], SECRETS["apn_username"], SECRETS["apn_password"]),enable=True)
    print(fona.gprs) # retruns false - need to enable using set_gprs() which needs apn, username and pw
    logger.info("GPRS ENABLED")

    # AT+HTTPCPOST - https://docs.espressif.com/projects/esp-at/en/latest/esp32/AT_Commands_Set/HTTP_AT_Commands.html#cmd-httpcpost

    (fona._send_check_reply(b"AT+HTTPINIT",reply=REPLY_OK)) # Initialise HTTP service return True
    time.sleep(0.1)
    (fona._send_check_reply(b"AT+HTTPPARA=\"CID\",1",reply=REPLY_OK)) # HTTPPARA paramter - sets the bearer profile ID of the connection - returns true
    logger.info("HTTP SERVICES ENABLED")

    (http_post(http_payload))
