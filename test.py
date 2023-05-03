# Import dependencies
import socket
import time
import random
import struct
import hashlib
import binascii

# var_int format 
# ! almost works except byte by byte comparison is used test case 5
def var_int(value):
    if value < b'\xfd':
        return struct.unpack('<B', value)[0]
    elif value <= b'\xff\xff':
        return struct.unpack('<H', value[1:])[0]
    elif value <= b'\xff\xff\xff\xff':
        print('3', value[1:])
        return struct.unpack('<I', value[1:])[0]
    else:
        print('4', value[1:])
        return struct.unpack('<Q', value[1:])[0]

# Binary encode the sub-version
def create_sub_version():
    sub_version = "/Satoshi:0.7.2/"
    return b'\x0F' + sub_version.encode()

# Binary encode the network addresses
def create_network_address(ip_address, port):
    network_address = struct.pack('>8s16sH', b'\x01', 
        bytearray.fromhex("00000000000000000000ffff") + socket.inet_aton(ip_address), port)
    return(network_address)

# Create the TCP request object
def create_message(magic, command, payload):
    checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[0:4]
    return(struct.pack('L12sL4s', magic, command.encode(), len(payload), checksum) + payload)

# Create the "version" request payload
def create_payload_version(node_ip_address):
    version = 60002
    services = 1
    timestamp = int(time.time())
    addr_local = create_network_address("0.0.0.0", 8333)
    addr_peer = create_network_address(node_ip_address, 8333)
    nonce = random.getrandbits(64)
    start_height = 0
    payload = struct.pack('<LQQ26s26sQ16sL', version, services, timestamp, addr_peer,
                          addr_local, nonce, create_sub_version(), start_height)
    return(payload)

# Create the "verack" request message
def create_message_verack():
    return bytearray.fromhex("f9beb4d976657261636b000000000000000000005df6e0e2")

def create_payload_getdata(tx_id):
    count = 1
    type = 1
    hash = bytearray.fromhex(tx_id)
    payload = struct.pack('<bb32s', count, type, hash)
    return(payload)

# Print request/response data
def print_response(command, request_data, response_data):
    print("")
    print("Command: " + command)
    print("Request:")
    print(binascii.hexlify(request_data))
    print("Response:")
    print(binascii.hexlify(response_data))

def unpack_header(response):
    # Define the header format
    header_fmt = "<4s12sI4s"

    # Unpack the header fields from the message
    magic, com, payload_size, checksum = struct.unpack(header_fmt, response[:24])

    # Format command 
    command = com.decode('ascii').strip('\0')

    # Print the header fields
    print(f"Magic: {magic.hex()}")
    print(f"Command: {command}")
    print(f"Payload size: {payload_size}")
    print(f"Checksum: {checksum.hex()}")
    print("\n")
    return command

def parse_inv_payload(payload):
    num_items = struct.unpack("<I", payload[:4])[0]
    print(num_items)

    items = []
    for i in range(num_items):
        print(f"Unpacked Type: {payload[4+i*36:8+i*36]} \n hash {payload[8+i*36:44+i*36].hex()}")
        item_type = struct.unpack("<I", payload[4+i*36:8+i*36])[0]
        item_hash = payload[8+i*36:44+i*36]
        print(f"Type: {item_type} \n Hash: {item_hash.hex()} \n")

        if item_type == 2:
            items.append((item_type, item_hash))    

    # Print the inventory vectors
    for item in items:
        print(f"Item type: {item[0]}, Item hash: {item[1].hex()}")

  

def main():


main()