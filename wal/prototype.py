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


class WAL:
    def __init__(self, path):
        self._path = path
        self._f = open(path, "a+b")
        self._next_lsn = 1
        self._recover()

    def append(self, rtype: bytes, payload: bytes) -> int:
        lsn = self._next_lsn
        self._next_lsn += 1

        frame = encode(lsn, rtype, payload)
        self._f.write(frame)
        self._f.flush()
        os.fsync(self._f.fileno())
        return lsn

    def replay(self):
        self._f.seek(0)
        while True:
            rec = decode_from(self._f)
            if rec is None:
                break
            yield rec
