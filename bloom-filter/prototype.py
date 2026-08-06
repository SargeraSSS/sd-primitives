import hashlib

class BloomFilter:
    def __init__(self, size : int, num_hash : int):
        self.size = size
        self.num_hash = num_hash
        self.bit_array = bytearray((size + 7 ) // 8)


    def _get_indexes(self, item):
        h1 = int.from_bytes(hashlib.md5(item.encode()).digest(), "big")
        h2 = int.from_bytes(hashlib.sha1(item.encode()).digest(), "big")
        for i in range(self.num_hash):
            yield (h1 + i*h2) % self.size

    def add(self, item):
        for i in self._get_indexes(item):
            byte_i = i // 8
            mask = 1 <<(i % 8)
            self.bit_array[byte_i] |= mask 

    def might_contain(self, item):
        for i in self._get_indexes(item):
            byte_i = i // 8
            mask = 1 << (i % 8)
            if not self.bit_array[byte_i] & mask:
                return False
        return True
        


bf = BloomFilter(10007, 7)
for i in range(1000):
    bf.add(f"item-{i}")

fn = sum(1 for i in range(1000) if not bf.might_contain(f"item-{i}"))
fp = sum(1 for i in range(20000) if bf.might_contain(f"nope-{i}"))
print(fn, fp / 200)  # must be 0 and ~0.8