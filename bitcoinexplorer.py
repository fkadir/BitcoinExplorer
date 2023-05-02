import socket
import time
import struct 
import hashlib
import random

# encoding formats 
# def var_int():

# def var_str():

def net_addr(services: int, ip: str, port: int, version: bool):
    time = int(time.time())
    services = services

    hex_ip = socket.inet_aton(ip).hex().encode()
    ip_address = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF' + hex_ip

    if version:
        net_adr = struct.pack('<Q', services) + ip_address + struct.pack('<Q', port)
    else:
        net_adr = struct.pack('<IQ', time, services) + ip_address + struct.pack('<Q', port)
    
    return net_addr

# def inv_vect():

# create different message payloads 
def create_version(version: int, services: int, port: int, ip: str, ):
    timestamp = int(time.time())
    addr_from = "0.0.0.0"
    nonce = random.randint(0, 99999)
    user_agent = 0 #b'\x00' 
    start_height = 0

    addr_from = net_addr(services, addr_from, port, version)
    addr_recv = net_addr(services, ip, port, version)

    # Create the payload message
    payload = struct.pack("<iQq", version, services, timestamp) + addr_recv + addr_from + struct.pack('<Qii', nonce, user_agent, start_height)

    # Define the magic value and command name
    magic = b"\xf9\xbe\xb4\xd9"
    command = b"version\x00\x00\x00\x00\x00\x00\x00\x00"

    # Calculate the payload checksum
    payload_checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]

    # Create the complete version message
    message = magic + command + struct.pack("<I", len(payload)) + payload + payload_checksum

    return message

# def create_verack():

# def create_getdata():

# parse incoming payloads
# def parse_block():

# def parse_inv():


# Send version message
version = 70015  # Replace with your own version number
services = 0  # Replace with the services you want to offer
timestamp = int(time.time())  # Replace with the current Unix timestamp
addr_recv = "201.191.6.103"  # Replace with the address of the receiving node
addr_from = "0.0.0.0" # Replace with your own address

nonce = random.randint(0, 99999)
user_agent = b'\x00' 
start_height = 0  # Replace with the block height of the latest block you have



# def main():
#     # Establish connection
#     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     sock.connect(('201.191.6.103', 8333))

#     # Create & send the complete message to the node
#     version_message = create_version()
#     sock.sendall(version_message)

#     # Receive and process any response from the node
#     response = sock.recv(1024)
#     print(response)

#     while True:

# main()
