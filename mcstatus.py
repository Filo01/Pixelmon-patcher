#!/usr/bin/env python
"""Checks the status (availability, logged-in players) on a Minecraft server.
Example:
    $ %(prog)s host [port]
    available, 3 online: mf, dignity, viking
    or
    McServer('my.mcserver.com').Update().player_names_sample
    frozenset(['mf', 'dignity', 'viking'])
Based on:
    https://gist.github.com/barneygale/1209061
Protocol reference:
    http://wiki.vg/Server_List_Ping
"""

import argparse
import json
import logging
import socket
import struct

DEFAULT_PORT = 25565
TIMEOUT_SEC = 5.0

def GetJson(host, port=DEFAULT_PORT):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(TIMEOUT_SEC)
    s.connect((host, port))

    # Send the handshake + status request.
    s.send(_PackData('\x00\x00' + _PackData(host.encode('utf8'))
                     + _PackPort(port) + '\x01'))
    s.send(_PackData('\x00'))

    # Read the response.
    unused_packet_len = _UnpackVarint(s)
    unused_packet_id = _UnpackVarint(s)
    expected_response_len = _UnpackVarint(s)

    data = ''
    while len(data) < expected_response_len:
        data += s.recv(1024)

    s.close()
    return json.loads(data.decode('utf8'))


def _UnpackVarint(s):
    num = 0
    for i in range(5):
        next_byte = ord(s.recv(1))
        num |= (next_byte & 0x7F) << 7 * i
        if not next_byte & 0x80:
            break
    return num


def _PackVarint(num):
    remainder = num
    packed = ''
    while True:
        next_byte = remainder & 0x7F
        remainder >>= 7
        packed += struct.pack('B', next_byte | (0x80 if remainder > 0 else 0))
        if remainder == 0:
            break
    return packed


def _PackData(data_str):
    return _PackVarint(len(data_str)) + data_str


def _PackPort(port_num):
    return struct.pack('>H', port_num)
