import os
import struct
import zlib

HEADER = struct.Struct("<IIQB")
SET, DELETE = 1, 2


def encode(lsn: int, rtype: int, payload: bytes) -> bytes:
    crc = zlib.crc32(payload)
    header = HEADER.pack(len(payload), crc, lsn, rtype)
    return header + payload
