# Import dependencies
import socket
import time
import struct 
import hashlib
import random
import binascii

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

def parse_inv_payload(payload):
    print(payload)
    
    # Ensure payload has at least 4 bytes
    if len(payload) < 4:
        print("Payload too short")
        exit()

    num_items = struct.unpack("<I", payload[:4])[0]
    items = []
    for i in range(num_items):
        item_type = struct.unpack("<I", payload[4+i*36:8+i*36])[0]
        item_hash = payload[8+i*36:44+i*36]
        items.append((item_type, item_hash))

    # Print the inventory vectors
    for item in items:
        print(f"Item type: {item[0]}, Item hash: {item[1].hex()}")

def main():
    # Constants
    magic_value = 0xd9b4bef9
    tx_id = "fc57704eff327aecfadb2cf3774edc919ba69aba624b836461ce2be9c00a0c20"
    node_ip_address = '167.71.73.244'
    port = 8333
    buffer_size = 1024
    
    # Create Request Objects
    version_payload = create_payload_version(node_ip_address)
    version_message = create_message(magic_value, 'version', version_payload)
    verack_message = create_message_verack()
    getdata_payload = create_payload_getdata(tx_id)
    getdata_message = create_message(magic_value, 'getdata', getdata_payload)

        # Establish TCP Connection
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((node_ip_address, port))

    # Send message "version"
    s.send(version_message)
    response_data = s.recv(buffer_size)
    print_response("version", version_message, response_data)

    # Send message "verack"
    s.send(verack_message)
    response_data = s.recv(buffer_size)
    print_response("verack", verack_message, response_data)

    data = s.recv(1024)
    parse_inv_payload(data)

    # while True:
    #     data = s.recv(1024)
    #     print(data)

    # # Send message "getdata"
    # s.send(getdata_message)
    # response_data = s.recv(buffer_size)
    # print_response("getdata", getdata_message, response_data)

    # Close the TCP connection
    # s.close()


main()
