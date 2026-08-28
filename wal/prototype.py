import os
import struct
import zlib

HEADER = struct.Struct("<IIQB")
SET, DELETE = 1, 2


def encode(lsn: int, rtype: int, payload: bytes) -> bytes:
    crc = zlib.crc32(payload)
    header = HEADER.pack(len(payload), crc, lsn, rtype)
    return header + payload


def decode_from(f) -> tuple[int, int, bytes] | None:
    raw = f.read(HEADER.size)
    if len(raw) < HEADER.size:
        return None
    length, crc, lsn, rtype = HEADER.unpack(raw)
    payload = f.read(length)
    if len(payload) < length:
        return None
    if zlib.crc32(payload) != crc:
        return None
    return lsn, rtype, payload
