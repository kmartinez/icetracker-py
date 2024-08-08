# Manual AT HTTP post

from adafruit_fona.adafruit_fona import FONA
from adafruit_fona.fona_3g import FONA3G
import sys
# from Drivers.SPI_SD import *
import time
from Drivers.PSU import * #EVERYTHING FROM THIS IS READONLY (you can use write functions, but cannot actually modify a variable)
from config import *
import json
import adafruit_logging as logging

logger = logging.getLogger("BASE")

CMD_AT = b"AT"
REPLY_OK = b"OK"
REPLY_DN = b"DOWNLOAD"
REPLY_ERROR = b"ERROR"
REPLY_CME_ERROR = b"+CME ERROR"
REPLY_CGACT = b"+CGACT: 1,1"

MAX_SENT_DATA_FILES = 30

SERVER_URL = "http://iotgate.ecs.soton.ac.uk/postin"

# http_payload = '{"sats": 12, "temp": 2.35, "altitude": 105.637, "timestamp": "2023-09-01T15:01:02", "batv": 3.92, "latitude": "64.1024530713333333", "rover_id": 19, "longitude": "-16.3378673346666667"}'
# json_payload = bytearray(http_payload)
test_payload = [{"batv": "3.92", "latitude": "64.1024530713333333", "rover_id": "19", "longitude": "-16.3378673346666667"}]
# http_payload = ["abcdef-glacsweb"]
# http_payload = []

def uhttp_post(payload) -> bool:
    logger.info("BASIC HTTP POST SETUP")
    logger.info("SET VERBOSE ERROR CODES")
    if not fona._send_check_reply(b"AT+CMEE=2",reply=REPLY_OK): # Set verbose error result codes
        return False
    time.sleep(0.1)

    logger.info("RESET HTTP PROFILE #0")
    if not fona._send_check_reply(b"AT+UHTTP=0",reply=REPLY_OK): # Reset HTTP profile #0
        return False
    time.sleep(0.1)

    logger.info("SET URL")
    if not fona._send_check_reply(b"AT+UHTTP=0,1,\"http://marc.ecs.soton.ac.uk/postin\"",reply=REPLY_OK): # Set URL
        print(fona._send_check_reply(b"AT+UHTTP=0,1,\"http://marc.ecs.soton.ac.uk/postin\"",reply=REPLY_OK))
        return False
    time.sleep(0.1)

    # logger.info("SET PORT OF HTTP REQUEST TO 80")
    # if not fona._send_check_reply(b"AT+UHTTP=0,2,443",reply=REPLY_OK): # Set port of HTTP request to 80
    #     print(fona._send_check_reply(b"AT+UHTTP=0,2,443",reply=REPLY_OK))
    #     return False
    # time.sleep(0.1)

    # logger.info("SET HTTP METHOD")
    # if not fona._send_check_reply(b"AT+UHTTP=2,1",reply=REPLY_OK): # Set HTTP method to POST
    #     return False
    # time.sleep(0.1)

    # logger.info("SET HTTP DATA")
    # if not fona._send_check_reply(b"AT+UHTTP=3,0,0",reply=REPLY_OK): # Set HTTP data to 0 bytes
    #     return False
    # time.sleep(0.1)

    # logger.info("SET HTTP HEADER")
    # if not fona._send_check_reply(b"AT+UHTTP=4,0",reply=REPLY_OK): # Set HTTP header to 0 bytes
    #     return False
    # time.sleep(0.1)

    # post data to server
    logger.info("POST DATA IN DIRECT LINK")
    if not fona._send_check_reply(b"0,7,\"http://marc.ecs.soton.ac.uk/postin\",4,"+str(len(payload)),reply=REPLY_OK): # Post data to server")
        return False
    else:
        fona._uart_write(bytearray(payload))
    time.sleep(0.1)
    # logger.info("SET HTTP DATA")
    # if not fona._send_check_reply(b"AT+UHTTP=5,"+str(len(payload)),reply=REPLY_OK): # Set HTTP data to <len> bytes
    #     return False
    # else:
    #     fona._uart_write(bytearray(payload))
    # time.sleep(0.1)

    logger.info("SEND HTTP POST")
    if not fona._send_check_reply(b"AT+UHTTP=6",reply=REPLY_OK): # Send HTTP POST
        return False
    time.sleep(0.1)

    logger.info("READ HTTP RESPONSE")
    if not fona._send_check_reply(b"AT+UHTTP=7",reply=REPLY_OK): # Read HTTP response
        return False
    time.sleep(0.1)

    logger.info("TERMINATE HTTP PROFILE")
    if not fona._send_check_reply(b"AT+UHTTP=8",reply=REPLY_OK): # Terminate HTTP profile
        return False
    time.sleep(0.1)

    return True


def uhttp_setup(payload):
    print(fona._send_check_reply(b"AT+CMEE=2",reply=REPLY_OK)) # Set verbose error result codes

    print(fona._send_check_reply(b"AT+UHTTP=0",reply=REPLY_OK)) # Reset HTTP profile #0

    print(fona._send_check_reply(b"AT+UHTTP=0,1,\"http://marc.ecs.soton.ac.uk/postin\"",reply=REPLY_OK)) # Set URL

    print(fona._send_check_reply(b"AT+UHTTP=0,5,80",reply=REPLY_OK)) # Set port of HTTP request to 80

    print(fona._send_check_reply(b"AT+UHTTP=0,20,2,1",reply=REPLY_OK)) # Mapping the embedded HTTP client to the HTTP POST method
    # print(fona._send_check_reply(b"AT+UDNSRN=0,\"http://marc.ecs.soton.ac.uk/postin\"",reply=REPLY_OK)) # DNS Resolution of URL   - Doesn't work
    
    # print(fona._send_check_reply(b"AT+UHTTPC=0,5,"/post","post.ffs","name_post=MyName&age_post=30",0",reply=REPLY_OK)) # Set HTTP data to 0 bytes




def http_post(payload) -> bool:

    logger.info("ENABLING HTTP SERVICES")
    if not fona._send_check_reply(b"AT+HTTPINIT",reply=REPLY_OK): # Initialise HTTP service return True
        return False
    time.sleep(0.1)

    if not fona._send_check_reply(b"AT+HTTPPARA=\"CID\",1",reply=REPLY_OK): # HTTPPARA paramter - sets the bearer profile ID of the connection - returns true
        return False
    time.sleep(0.1)
    logger.info("HTTP SERVICES ENABLED")

    logger.info("SETTING UP URL")
    if not fona._send_check_reply(b"AT+HTTPPARA=\"URL\",\"http://iotgate.ecs.soton.ac.uk/postin\"",reply=REPLY_OK):
        return False       # set HTTP parameters value
    time.sleep(0.1)

    logger.info("PROVIDING CONTENT TYPE")
    # if not fona._send_check_reply(b"AT+HTTPPARA=\"CONTENT\",\"x-www-form-urlencoded\"",reply=REPLY_OK):
    # if not fona._send_check_reply(b"AT+HTTPPARA=\"CONTENT\",\"text/plain\"",reply=REPLY_OK):

    if not fona._send_check_reply(b"AT+HTTPPARA=\"CONTENT\",\"application/json\"",reply=REPLY_OK):
        return False        # set HTTP parameters value
    time.sleep(0.1)

    logger.info("PROVIDING PAYLOAD")
    if not fona._send_check_reply(b"AT+HTTPDATA="+str(len(payload))+",10000",reply=REPLY_DN): # Send data to HTTP server - <len> is the length of data to be sent - 10000 is the timeout
        return False      # input HTTP data
    else:
        # fona._uart_write(str(json.loads(payload)))
        # fona._uart_write(str(json.loads(payload)).encode())
        fona._uart_write(bytearray(payload))
    time.sleep(0.1)

    logger.info("POSTING DATA")
    if not fona._send_check_reply(b"AT+HTTPACTION=1",reply=REPLY_OK):
        return False   # HTTP method action
    time.sleep(0.1)

    logger.info("READING SERVER RESPONSE")

    if not fona._send_check_reply(b"AT+HTTPREAD",reply=REPLY_OK):
        return False       # Read HTTP Server Response
    else:
        logger.info("HTTP request successful - Removing sent data")
        # for path in payload_paths:
        #     os.rename("/sd/data_entries/" + path, "/sd/sent_data/" + path)

        # # if contents in sd/sent_data is too large, remove files until it is less than MAX_SENT_DATA_FILES (30)
        # sent_data = os.listdir("/sd/sent_data/")
        # if len(sent_data) > MAX_SENT_DATA_FILES:
        #     for file in sent_data[:-MAX_SENT_DATA_FILES]: 
        #         os.remove("/sd/sent_data/" + file)
        
        # if there are contents inside of sent_data, remove them all - available in case the first if statement is not needed
        # if len(os.listdir("/sd/sent_data/")) > 0:
        #     for file in os.listdir("/sd/sent_data/"):
        #         os.remove("/sd/sent_data/" + file)
    time.sleep(0.1)

    logger.info("TERMINATING HTTP SERVICES")
    if not fona._send_check_reply(b"AT+HTTPTERM",reply=REPLY_OK):
        return False       # Terminate HTTP service
    time.sleep(0.1) 

    return True


def chttp_post(payload):

    logger.info("ENABLING HTTP SERVICES")
    if not fona._send_check_reply(b"AT+CHTTPSSTART",reply=REPLY_OK): # Initialise HTTP service for 3G - returns True
        print("FAILED TO START HTTPS")
        print(fona._send_check_reply(b"AT+CHTTPSSTART",reply=REPLY_OK))
        return False
    time.sleep(0.1)

    logger.info("OPEN HTTPS Session")
    if not fona._send_check_reply(b"AT+CHTTPSOPSE=\"http://iotgate.ecs.soton.ac.uk/postin\",80",reply=REPLY_OK): # Opens a new HTTPS session
        print("FAILED TO OPEN HTTPS SESSION")
        print(fona._send_check_reply(b"AT+CHTTPSOPSE=\"http://iotgate.ecs.soton.ac.uk/postin\",80",reply=REPLY_OK))
        return False
    time.sleep(0.1)

    logger.info("SENDING HTTPS REQUEST")
    if not fona._send_check_reply(b"AT+CHTTPSSEND="+str(len(payload)),reply=REPLY_OK): # Send an HTTPS request - specifying <len> used to download data to be sent
        return False
    time.sleep(0.1)

    logger.info("RECEIVING HTTPS RESPONSE")
    if not fona._send_check_reply(b"AT+CHTTPSRECV?",reply=REPLY_OK): # Receive HTTPS response after sending HTTPS request
        return False
    time.sleep(0.1)

    logger.info("CLOSING HTTPS SESSION")
    if not fona._send_check_reply(b"AT+CHTTPSCLSE",reply=REPLY_OK): # Close opened HTTPS Session
        return False
    time.sleep(0.1)

    logger.info("TERMINATING HTTPS SERVICES")
    if not fona._send_check_reply(b"AT+CHTTPSSTOP",reply=REPLY_OK): # Stops HTTPS protocol stack
        return False
    time.sleep(0.1)



    return True
    

if __name__ == '__main__':
    
    # data_paths = os.listdir("/sd/data_entries/")
    http_payload = []
    payload_paths = []

    logger.info("ENABLING GSM COMMS")

    fona = FONA(GSM_UART, GSM_RST_PIN, debug=True)

    # fona = FONA3G(GSM_UART, GSM_RST_PIN, debug=False)
    
    logger.info("FONA initialized")


    fona._send_check_reply(CMD_AT,reply=REPLY_OK)      # sends data to fona - validates if true - send AT - expecting response OK - received True 

    fona._send_check_reply(b"ATE0",reply=REPLY_OK)     # turn off echoing

    fona._send_check_reply(b"AT+CMEE?",reply=REPLY_OK) # returns 2

    # enable gprs - using apn
    logger.info("ENABLING GPRS")
    while not fona.gprs:
        fona.set_gprs((SECRETS["apn"], SECRETS["apn_username"], SECRETS["apn_password"]),enable=True)
    print(fona.gprs)       # returns false - need to enable using set_gprs() which needs apn, username and pw
    logger.info("GPRS ENABLED")

    # check PDP context
    logger.info("CHECKING PDP CONTEXT")

    print(fona._send_check_reply(b"AT+CFUN=1",reply=REPLY_OK))  # returns 1 - full functionality
    print(fona._send_check_reply(b"AT+COPS?",reply=b"+COPS:"))  # verifies network registration - returns 0,0,"EE Things Mobile",7
    print(fona._send_check_reply(b"AT+CGACT=1,1",reply=REPLY_OK))  # Activate PDP context 1 - returns OK
    print(fona._send_check_reply(b"AT+CGDCONT?",reply=b"CGDCONT:"))  # return IPV4 Address

    uhttp_setup(test_payload)


    # print(fona._send_check_reply(b"AT+CGDCONT=1,\"IP\",\"TM\"",reply=REPLY_OK))  # Set PDP context 1 - returns OK
    # print(fona._send_check_reply(b"AT+CGACT?",reply=REPLY_CGACT))  # returns 1 - attached to GPRS service



    # print(fona._send_check_reply(b"AT+UDCONF=19,2,0",reply=REPLY_OK))   # not supported
    # print(fona._send_check_reply(b"AT+CFUN=16",reply=REPLY_OK)) 

    # print(fona._send_check_reply(b"AT+CGDCONT?",reply=REPLY_OK)) # returns +CGDCONT: 1,"IP","TM","
    # print(fona._send_check_reply(b"AT+CGACT?",reply=REPLY_OK))   # returns 1 - attached to GPRS service
    
    # if not fona._send_check_reply(b"AT+CGACT?",reply=REPLY_CGACT):
    #     logger.error("Failed to activate PDP service")
    #     sys.exit(1)
    #     # return False
        
    # # else:
    # #     fona.
    # #     fona.write(b"AT+CGACT=1,1\r\n")
    # logger.info("PDP CONTEXT CHECKED")

    # if not fona._send_check_reply(b"AT+UDCONF=19,2,0",reply=REPLY_OK):
    #     print(fona._send_check_reply(b"AT+UDCONF=19,2,0",reply=REPLY_OK))
    #     logger.error("Failed to disable URC")
    #     # return False
    # else:
    #     logger.info("URC DISABLED")
    
    

    # version for unused mode
    # AT+HTTPCPOST - https://docs.espressif.com/projects/esp-at/en/latest/esp32/AT_Commands_Set/HTTP_AT_Commands.html#cmd-httpcpost
    # (fona._send_check_reply(b"AT+HTTPINIT",reply=REPLY_OK)) # Initialise HTTP service return True
    # time.sleep(0.1)
    # (fona._send_check_reply(b"AT+HTTPPARA=\"CID\",1",reply=REPLY_OK)) # HTTPPARA paramter - sets the bearer profile ID of the connection - returns true
    # logger.info("HTTP SERVICES ENABLED")
    # chttp_post(http_payload)

    # data_paths = os.listdir("/sd/data_entries/")
    # http_payload = []
    # payload_paths = []

    # if len(data_paths) < 1:
    #     logger.warning("No unsent data on SD") # ??? why keep for loop next???
    # for path in data_paths:
    #     with open("/sd/data_entries/" + path, "r") as file:
    #         try:
    #             http_payload.append(json.load(file))
    #             payload_paths.append(path)
    #         except json.JSONDecodeError:
    #             logger.warning("Invalid JSON file: %s", path)
    #             os.rename("/sd/data_entries/" + path, "/sd/invalid_data/" + path)
    #     if len(http_payload) >= MAX_READINGS_IN_SINGLE_HTTP:
    #         print("MAX READINGS REACHED")
    #         chttp_post(json.dumps(http_payload))
    #         http_payload = []
    #         payload_paths = []    

    # chttp_post(json.dumps(http_payload))
    # http_post(json.dumps(test_payload))
    # uhttp_post(json.dumps(test_payload))

    # shutdown()


