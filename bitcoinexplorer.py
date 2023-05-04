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
    val = value[:4]
    if val < b'\xfd':
        return 1, struct.unpack('<B', value[0:1])[0]
    elif val <= b'\xff\xff':
        return 3, struct.unpack('<H', value[1:3])[0]
    elif val <= b'\xff\xff\xff\xff':
        return 5, struct.unpack('<I', value[1:5])[0]
    else:
        return 9, struct.unpack('<Q', value[1:9])[0]

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
    return command, payload_size, magic, checksum

def parse_inv_payload(payload):
    # print(payload)
    length, num_items = var_int(payload)

    block_items = []
    for i in range(num_items):
        item_type = struct.unpack("<I", payload[length+i*36:(length+4)+i*36])[0]
        item_hash = payload[8+i*36:44+i*36]

        if item_type == 2:
            print("WE GOT A BLOCK PEOPLE")
            block_items.append((item_type, item_hash))    
        elif item_type == 1:
            print("we got a transaction!")

    # Print the inventory vectors
    for item in block_items:
        print(f"Item type: {item[0]}, Item hash: {item[1].hex()}")

    return block_items

def main():
    # Constants
    magic_value = 0xd9b4bef9
    node_ip_address = '52.78.49.245'
    port = 8333
    buffer_size = 1024
    
    # Create Request Objects
    version_payload = create_payload_version(node_ip_address)
    version_message = create_message(magic_value, 'version', version_payload)

    verack_message = create_message_verack()

    # Establish TCP Connection
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((node_ip_address, port))

    # Send message "version"
    sock.send(version_message)
    response_data = sock.recv(buffer_size)
    # print_response("version", version_message, response_data)

    # Send message "verack"
    sock.send(verack_message)
    response_data = sock.recv(buffer_size)
    # print_response("verack", verack_message, response_data)

    while True: 
        data = sock.recv(24)
        command, payload_size, magic, checksum = unpack_header(data)
        payload = sock.recv(payload_size)
        if (command=='inv'):
            print('we got an event!\n')
            parse_inv_payload(payload) 
    

    # # Create getdata Payload
    #tx_id = "fc57704eff327aecfadb2cf3774edc919ba69aba624b836461ce2be9c00a0c20"
    # getdata_payload = create_payload_getdata(tx_id)
    # getdata_message = create_message(magic_value, 'getdata', getdata_payload)
    # # Send message "getdata"
    # sock.send(getdata_message)
    # response_data = sock.recv(buffer_size)
    # print_response("getdata", getdata_message, response_data)

    # # Close the TCP connection
    # sock.close()

main()