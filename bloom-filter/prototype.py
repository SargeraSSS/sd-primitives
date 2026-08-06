import hashlib
import math
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
    @staticmethod
    def _is_prime(x):
        if x < 2:
            return False
        for d in range(2, x):
            if x % d == 0:
                return False
        return True
    
    # 
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
    



if __name__ == "__main__":
    bf = BloomFilter(10007, 7)
    for i in range(1000):
        bf.add(f"item-{i}")

    fn = sum(1 for i in range(1000) if not bf.might_contain(f"item-{i}"))
    fp = sum(1 for i in range(20000) if bf.might_contain(f"nope-{i}"))
    print(fn, fp / 200)  # must be 0 and ~0.8

    print(BloomFilter.optimal_params(1000, 0.01)) # (9586, 7)
    print(BloomFilter.optimal_params(1000, 0.001)) # (14378, 10)
    print(BloomFilter._is_prime(2))        # True
    print(BloomFilter._is_prime(3))        # True
    print(BloomFilter._is_prime(10007))    # True
    print(BloomFilter._is_prime(1))        # False
    print(BloomFilter._is_prime(4))        # False
    print(BloomFilter._is_prime(9))        # False