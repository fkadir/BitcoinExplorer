import socket
import time
import struct 
import hashlib

# Send version message
version = 70015  # Replace with your own version number
services = 0  # Replace with the services you want to offer
timestamp = int(time.time())  # Replace with the current Unix timestamp
addr_recv = "0.0.0.0"  # Replace with the address of the receiving node
addr_recv = addr_recv.encode()
addr_from = "0.0.0.0" # Replace with your own address
addr_from = addr_from.encode()
nonce = 1234567890  # Replace with a random nonce value
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"  # Replace with your own user agent string
user_agent = user_agent.encode()
start_height = 0  # Replace with the block height of the latest block you have

# Create the payload message
payload = struct.pack("<iQq26sQsQ", version, services, timestamp, addr_recv, nonce, user_agent, start_height) #,  addr_from 26s

# Define the magic value and command name
magic = b"\xf9\xbe\xb4\xd9"
command = b"version\x00\x00\x00\x00\x00\x00\x00\x00"

# Calculate the payload checksum
payload_checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]

# Create the complete version message
message = magic + command + struct.pack("<I", len(payload)) + payload + payload_checksum

# Establish connection
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('142.114.241.39', 8333))

# Send the complete message to the node
sock.sendall(message)

# Receive and process any response from the node
response = sock.recv(1024)
print(response)