import hashlib



class ConsistentHash:
    def __init__(self, vnodes=200):
        self.vnodes = vnodes
        self._ring = {}
        self._sorted = []

    @staticmethod
    def _hash(s):
        return int.from_bytes(hashlib.md5(s.encode()).digest()[:8], "big")

buckets = [0] * 100
step = 2 ** 64 // 100
for i in range(100000):
    buckets[min(ConsistentHash._hash(f"x-{i}") // step, 99)] += 1
print(min(buckets), max(buckets)) # 934 1066