import socket
import time
import struct 
import hashlib
import random

# def var_int():

def encode_varint(value):
    if value < 0xfd:
        return bytes([value])
    elif value <= 0xffff:
        return b'\xfd' + value.to_bytes(2, 'little')
    elif value <= 0xffffffff:
        return b'\xfe' + value.to_bytes(4, 'little')
    else:
        return b'\xff' + value.to_bytes(8, 'little')


my_list = [1, 2, 3, 4, 5]
length = len(my_list)
varint = encode_varint(length)
print(varint)
