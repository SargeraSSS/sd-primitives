import hashlib
import math
class BloomFilter:
    def __init__(self, size : int, num_hash : int):
        self.size = size
        self.num_hash = num_hash
        self.bit_array = bytearray((size + 7 ) // 8)
        self.count = 0  


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
        self.count += 1

    def might_contain(self, item):
        for i in self._get_indexes(item):
            byte_i = i // 8
            mask = 1 << (i % 8)
            if not self.bit_array[byte_i] & mask:
                return False
        return True

    def fill_ratio(self):
        ones = sum(b.bit_count() for b in self.bit_array)
        return ones / self.size          # знаменник логічний, не len(bit_array)*8

    def current_fp_rate(self):
        return self.fill_ratio() ** self.num_hash

    @staticmethod
    def _is_prime(x):
        if x < 2:
            return False
        for d in range(2, math.isqrt(x) + 1):
            if x % d == 0:
                return False
        return True

    @staticmethod
    def _next_prime(x):
        while not BloomFilter._is_prime(x):
            x+= 1 
        return x
    
    @staticmethod    
    def optimal_params(n, p): # n - amount of elements,  p - desired error
        if not (0 < p < 1 ):
            raise ValueError(f"p must be in (0,1), got {p}")
        if n < 1:
            raise ValueError(f"n must >= 1 got {n}")
        ln2 = math.log(2)
        m = -n * math.log(p) / ln2 **2
        k = (m / n) * ln2
        return math.ceil(m), max(1, round(k))
    
    @classmethod
    def from_capacity(cls, expected_items, false_positive_rate):
        size, num_hash = cls.optimal_params(expected_items, false_positive_rate)
        size = cls._next_prime(size)
        return cls(size, num_hash)


if __name__ == "__main__":
    bf = BloomFilter.from_capacity(1000, 0.01)
    for i in range(1000):
        bf.add(f"item-{i}")

    fn = sum(1 for i in range(1000) if not bf.might_contain(f"item-{i}"))
    fp = sum(1 for i in range(20000) if bf.might_contain(f"nope-{i}"))
    print(bf.size, bf.num_hash, fn, fp / 200)   # ~9587 7 0 ~0.9