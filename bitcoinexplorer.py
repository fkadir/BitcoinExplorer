# Import dependencies
import socket
import time
import random
import struct
import hashlib
import binascii
import datetime

# var_int format 
# ! almost works except byte by byte comparison is used test case 5
def transform_var_int(value):
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

def create_payload_getdata(count, ids):
    type = 2
    payload = struct.pack('<b', count)
    for i in range(0, count-1):
        payload += struct.pack('<b32s', type, ids[i])
    print(payload)
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
    print("\n")
    print(f"Magic: {magic.hex()}")
    print(f"Command: {command}")
    print(f"Payload size: {payload_size}")
    print(f"Checksum: {checksum.hex()}")
    print("\n")
    return command, payload_size, magic, checksum

def parse_inv_payload(payload):
    # print(payload)
    length, num_items = transform_var_int(payload)

    block_items = []
    for i in range(num_items):
        item_type = struct.unpack("<I", payload[length+i*36:(length+4)+i*36])[0]
        item_hash = payload[8+i*36:44+i*36]

        if item_type == 2:
            print("WE GOT A BLOCK PEOPLE")
            print(f"Item type: {item_type}, Item hash: {item_hash.hex()}")
            block_items.append(item_hash)    

    return block_items

# Print timestamp, list of transactions (incl value), nonce, difficulty level, verify hash
def parse_block_payload(payload):
    block_ftm = '<i32s32sIII'
    version, prev_block, merkle, unix_timestamp, bits, nonce = struct.unpack(block_ftm, payload[:80])
    # human readable timestamp 
    dt_object = datetime.fromtimestamp(unix_timestamp).strftime('%a %d %b %Y, %I:%M%p')
    timestamp = dt_object.strftime("%Y-%m-%d %H:%M:%S")

    b, n_transactions = transform_var_int(payload[80:])
    return timestamp, nonce # difficulty, n_transactions, transactions


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
        if len(data) == 24:
            command, payload_size, magic, checksum = unpack_header(data)
            payload = sock.recv(payload_size)
            if (command=='inv'):
                # Get block transactions
                ids = parse_inv_payload(payload)

                if (len(ids) > 0):
                    #  Create getdata message
                    getdata_payload = create_payload_getdata(len(ids), ids)
                    getdata_message = create_message(magic_value, 'getdata', getdata_payload)

                    # Send message "getdata"
                    sock.send(getdata_message)
                    response_data = sock.recv(2000000) #???
                    print_response('getdata', getdata_message, response_data)

                    command, payload_size, magic, checksum = unpack_header(response_data)
                    timestamp, nonce = parse_block_payload(response_data[24:])
                    # print_response("getdata", getdata_message, response_data)
                    print(f"Timestamp: {timestamp}, Nonce: {nonce} \n THE END")
                    break

main()