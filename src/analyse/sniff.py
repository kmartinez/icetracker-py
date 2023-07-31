import serial
import binascii
import time
import datetime
ser = serial.Serial('COM16', 115200)
while True:
    ser.read_until(b'\x80\x80') #find packet

    size_raw = ser.read(4)
    size = int.from_bytes(size_raw, "little")
    if size < 0 or size > 1000:
        print("WARN: invalid size")
        #print(f"DEBUG: {size}")
        continue
    
    link_layer_payload = ser.read(size) #payload + checksum
    if link_layer_payload is None or len(link_layer_payload) != size:
        print("WARN: data size does not match received size")
        continue
    network_layer_payload = link_layer_payload[:-4]
    checksum_raw = link_layer_payload[-4:]
    checksum = int.from_bytes(checksum_raw, "little")
    calculated_checksum = binascii.crc32(network_layer_payload)
    if checksum != calculated_checksum:
        print("WARN: checksum fail")
        #print(f"DEBUG: CALCULATED: {calculated_checksum}, RECV: {checksum}")
        continue
    
    transport_header = network_layer_payload[:2]
    payload = network_layer_payload[2:]
    type = transport_header[0]
    sender = transport_header[1]

    match type:
        case 3:
            type_str = "ACK"
        case 4:
            type_str = "NMEA"
        case 5:
            type_str = "RTCM3"
        case 8:
            type_str = "FIN"
        case _:
            type_str = f"UNKNOWN OR DEPRECATED ({type})"

    timestamp = time.localtime(time.time())
    time_str = "%02d:%02d:%02d" % (timestamp[3], timestamp[4], timestamp[5])
    print(f"{time_str} - SUCCESS: packet of type {type_str} received from {sender}")
