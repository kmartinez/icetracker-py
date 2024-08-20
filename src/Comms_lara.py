# Manual AT HTTP post
# for ublox LARA R600
# Reference links for firmware update 
#https://content.u-blox.com/sites/default/files/documents/LARA-R6-L6-01B-IP_IN_UBXDOC-686885345-1861.pdf
#https://content.u-blox.com/sites/default/files/documents/LEXI-R520-SARA-R5-FW-Update_AppNote_UBX-20033314.pdf
#https://www.u-blox.com/en/product/lara-r6-series?legacy=Current#Documentation-&-resources
# Evaluation Software - Evaluation software for LARA-R6 series
#https://www.u-blox.com/en/product/lara-r6-series?legacy=Current#Documentation-&-resources
# Reference links for HTTP POST
# https://content.u-blox.com/sites/default/files/documents/LARA-R6-L6_ATCommands_UBX-21046719.pdf
# https://files.seeedstudio.com/wiki/LTE_Cat_1_Pi_HAT/res/AT-CommandsExamples_AppNote_(UBX-13001820).pdf
# http_command - allowed values for LARA-L6/:LARA-R6 - 0,1,2,3,4,5 - DO NOT USE 6 and 7!!
# possible APN not set correctly
from adafruit_fona.adafruit_fona import FONA
from adafruit_fona.fona_3g import FONA3G
import sys
import os
# from Drivers.SPI_SD import *
import time
from Drivers.PSU import * #EVERYTHING FROM THIS IS READONLY
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
#not used for now - hard coded later
SERVER_URL = "http://marc.ecs.soton.ac.uk/postin"

# http_payload = '{"sats": 12, "temp": -2.35, "altitude": 105.637, "timestamp": "2023-09-01T15:01:02", "batv": 3.92, "latitude": "64.1024530713333333", "rover_id": 19, "longitude": "-16.3378673346666667"}'
# json_payload = bytearray(http_payload)
test_payload = [{"batv": "3.92", "latitude": "64.9999999", "rover_id": "19", "longitude": "-16.999999789"}]
message_payload = "post data from 4g LARA module - Sherif"



# # source: https://content.u-blox.com/sites/default/files/documents/LARA-R6-Internet-applications-development-guide_AppNote_UBX-22001854.pdf
# # page 64
def uhttp_post(payload) -> bool:
    # Set verbose error result codes
    logger.info("SET VERBOSE ERROR CODES")
    if not fona._send_check_reply(b"AT+CMEE=2",reply=REPLY_OK):
        return False
    time.sleep(0.1)

    # Write payload to temporary Post file called "postFile.txt" with payload length specified
    logger.info("WRITE PAYLOAD TO FILE")
    if not fona._send_check_reply(b"AT+UDWNFILE=\"postFile.txt\","+str(len(payload)),reply=b">"):
        return False
    else:
        fona._uart_write(bytearray(payload))
    time.sleep(0.1)

    #URDFILE - Ensure that data string is present in file
    logger.info("CHECKING DATA IS PRESENT IN FILE")
    fona._send_check_reply(b"AT+URDFILE=\"postFile.txt\"",reply=REPLY_OK)
    time.sleep(0.1)


    logger.info("RESET HTTP PROFILE #0")
    if not fona._send_check_reply(b"AT+UHTTP=0",reply=REPLY_OK):
        return False
    time.sleep(0.1)

    # Set URL path to marc.ecs.soton.ac.uk
    logger.info("SET URL")
    if not fona._send_check_reply(b"AT+UHTTP=0,1,\"marc.ecs.soton.ac.uk\"",reply=REPLY_OK):
        return False
    time.sleep(0.1)

    # Set HTTP URL Port to to Port 80
    logger.info("SET PORT OF HTTP REQUEST TO 80")
    if not fona._send_check_reply(b"AT+UHTTP=0,5,80",reply=REPLY_OK):
        return False
    time.sleep(0.1)

    # Post Data to marc.ecs.soton.ac.uk/postin through postFile.txt, and store the server response inside resultResponseFile.txt
    logger.info("SUBMIT POST COMMAND IN JSON FORMAT - 4 STORE ANSWER IN RESULT.TXT")
    if not fona._send_check_reply(b"AT+UHTTPC=0,4,\"/postin\",\"resultResponseFile.txt\",\"postFile.txt\",4",reply=REPLY_OK):
        return False
    time.sleep(0.1)

    # ERROR CODES - review with UHTTPER
    # 0, 4, 0 - Failed to send - review 
    # not working UHTTPER: 0, 3, 11
    # error class = HTTP Protocol Error Class = 3
    # Error Result Code = 11 = Server Connection Error

    # Reading Server Response from resultResponseFile.txt
    logger.info("READING HTTP RESPONSE")
    fona._send_check_reply(b"AT+URDFILE=\"resultResponseFile.txt\"",reply=REPLY_OK) # check the server's reply
    time.sleep(0.1)

    # Remove postFile.txt after data has been sent to avoid duplicates
    logger.info("DELETING FILENAME")
    if not fona._send_check_reply(b"AT+UDELFILE=\"postFile.txt\"",reply=REPLY_OK):
        return False
    time.sleep(0.1)
    

if __name__ == '__main__':

    logger.info("ENABLING 4G GSM COMMS")
    
    fona = FONA(GSM_UART, GSM_RST_PIN, debug=False)

    logger.info("FONA initialized")
    
    
    fona._send_check_reply(b"AT+CMEE?",reply=REPLY_OK) # we want zero - not lots of reports

    # enable gprs - using apn
    logger.info("ENABLING GPRS")
    # try a few times and exit politely if no signal - NEEDS TO EXIT AND SHUTDOWN IF FAILS!!
    count = 5
    while not fona.gprs:
        count = count - 1
        fona.set_gprs((SECRETS["apn"], SECRETS["apn_username"], SECRETS["apn_password"]),enable=True)
        if count == 0 :
            print("can't connect - shutting down")
            sys.exit()
            # shutdown()
            # break
            
    print(fona.gprs)       # returns false - need to enable using set_gprs() which needs apn, username and pw
    logger.info("GPRS ENABLED")
    # try finding rssi
    logger.info("RSSI READING:")
    print(fona.rssi)

    # check PDP context
    logger.info("CHECKING PDP CONTEXT")
    # each needs a False check and exit

    # print(fona._send_check_reply(b"AT+CFUN=1",reply=REPLY_OK))  # returns 1 - full functionality
    if not fona._send_check_reply(b"AT+CFUN=1",reply=REPLY_OK):
        sys.exit()
    time.sleep(0.1)
    if not fona._send_check_reply(b"AT+COPS?", reply=b"+COPS: 0,0,\"EE Things Mobile\",7"):
        sys.exit()
    time.sleep(0.1)

    if not fona._send_check_reply(b"AT+CGACT=1,1",reply=REPLY_OK):
        sys.exit()
    time.sleep(0.1)
    fona._send_check_reply(b"AT+CGDCONT?",reply=b"CGDCONT:")  # return IPV4 Address

    if not fona._send_check_reply(b"AT+CGDCONT=1,\"IP\",\"TM\"",reply=REPLY_OK):
        sys.exit()
    time.sleep(0.1)

    if not fona._send_check_reply(b"AT+CGACT?",reply=REPLY_CGACT):
        sys.exit()
    time.sleep(0.1)
    
    # =============UNCOMMENT WHEN DEPLOYED=============
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
    #         uhttp_post(json.dumps(http_payload))
    #         http_payload = []
    #         payload_paths = []    


    try:
        uhttp_post(json.dumps(test_payload)) # final version
    except BaseException as e:
        print(e)
        sys.exit()
    finally:
        sys.exit()

    # shutdown()



 
