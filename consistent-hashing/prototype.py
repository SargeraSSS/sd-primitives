import hashlib



class ConsistentHash:
    def __init__(self, vnodes=200):
        self.vnodes = vnodes
        self._ring = {}
        self._sorted = []

    @staticmethod
    def _hash(s):
        return int.from_bytes(hashlib.md5(s.encode()).bigest()[:8], "big")
    