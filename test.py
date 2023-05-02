import socket
import time
import struct 
import hashlib
import random

def net_addr(services: int, ip: str, port: int, version: bool):
    timestamp = int(time.time())
    services = services

    hex_ip = socket.inet_aton(ip).hex().encode()
    ip_address = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF' + hex_ip

    if version:
        net_addr = struct.pack('<Q', services) + ip_address + struct.pack('<Q', port)
    else:
        net_addr = struct.pack('<IQ', timestamp, services) + ip_address + struct.pack('<Q', port)
    
    return net_addr


# input 
version = 70015  # Replace with your own version number
services = 0
ip = "10.0.0.1"
port = 8333

## create version function
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
