# Import dependencies
import socket
import time
import random
import struct
import hashlib
import binascii
import datetime

# var_int format 
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

def create_var_int(value):
    val = value.to_bytes(2, 'little')
    if val < b'\xfd':
        return struct.pack('<B', value)
    elif val <= b'\xff\xff':
        return struct.pack('<H', value)
    elif val <= b'\xff\xff\xff\xff':
        return struct.pack('<I', value)
    else:
        struct.pack('<Q', value)
    
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

def create_payload_getdata(count, block_hash):
    type = 2
    payload = create_var_int(count)
    if len(block_hash) > 1:
        for i in range(0, count-1):
            payload += struct.pack('<I32s', type, block_hash[i])
    else:
        payload += struct.pack('<I32s', type, block_hash[0])
        
    return(payload)

# Print request/response data
# delete ???
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
    print(com)
    if com[0] == b'\x00':
        command = 'Command Unknown'
    else: 
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
    length, num_items = transform_var_int(payload)

    block_items = []
    for i in range(num_items):
        item_type = struct.unpack("<I", payload[length+i*36:(length+4)+i*36])[0]
        item_hash = payload[(length+4)+i*36:(length+36)+i*36]

        if item_type == 2:
            print(f"Item type: {item_type}, Item hash: {item_hash.hex()}")
            block_items.append(item_hash)    

    return block_items

# retrieve timestamp, list of transactions (incl value), nonce, difficulty level, hash from received block message
def parse_block_payload(payload):
    block_ftm = '<i32s32sIII'
    print(payload[:80]) # delete ????
    version, prev_block, merkle, unix_timestamp, difficulty, nonce = struct.unpack(block_ftm, payload[:80])

    # human readable timestamp 
    timestamp = datetime.datetime.fromtimestamp(unix_timestamp).strftime('%a %d %b %Y, %I:%M%p')

    b, n_transactions = transform_var_int(payload[80:])
    return timestamp, nonce, difficulty, merkle #, n_transactions, transactions (incl value), hash == merkle?

def display_block(timestamp, nonce, difficulty, send_hash, rec_hash): #n_transactions, transactions

    print(f'Timestamp: {timestamp}\n')
    #list of transactions and their value 
    print('uhhhhh transactions right')
    print(f'Nonce: {nonce}, Difficulty level: {difficulty}')
    #verify hash 
    print(f'Send Hash: {send_hash}')
    print(f'Received Hash: {rec_hash}')
    if hash_block[0] == rec_hash:
        print('Verified Hash!')
    else:
        print('Unverified Hash')


if __name__ == '__main__':
    # Constants
    magic_value = 0xd9b4bef9
    node_ip_address = '63.227.116.162'
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

    # Send message "verack"
    sock.send(verack_message)
    response_data = sock.recv(buffer_size)

    while True: 
        data = sock.recv(24)
        if len(data) == 24:
            command, payload_size, magic, checksum = unpack_header(data)
            payload = sock.recv(payload_size)
            if (command=='inv'):
                # Get block transactions
                hash_block = parse_inv_payload(payload)

                if (len(hash_block) > 0):
                    #  Create getdata message
                    getdata_payload = create_payload_getdata(len(hash_block), hash_block)
                    getdata_message = create_message(magic_value, 'getdata', getdata_payload)

                    # Send message "getdata"
                    sock.send(getdata_message)
                    response_data = sock.recv(2000000) #???
                    print_response(response_data)  # delete ???

                    command, payload_size, magic, checksum = unpack_header(response_data)
                    timestamp, nonce, difficulty, rec_hash = parse_block_payload(response_data[24:])

                    # display block 
                    display_block(timestamp, nonce, difficulty, hash_block[0], rec_hash)
                    break