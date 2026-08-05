import hashlib

class BloomFilter:
    def __init__(self, size : int, num_hash : int):
        self.size = size
        self.num_hash = num_hash
        self.bit_array = bytearray(size)

    def _get_indexes(self, item):
        h1 = int.from_bytes(hashlib.md5(item.encode()).digest(), "big")
        h2 = int.from_bytes(hashlib.sha1(item.encode()).digest(), "big")
        for i in range(self.num_hash):
            yield (h1 + i*h2) % self.size

    def add(self, item):
        for i in self._get_indexes(item):
            self.bit_array[i] = 1

    def might_contain(self, item):
        for i in self._get_indexes(item):
            if self.bit_array[i] == 0:
                return False
        return True


