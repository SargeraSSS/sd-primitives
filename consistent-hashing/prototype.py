import hashlib
import bisect


class ConsistentHash:
    def __init__(self, vnodes=200):
        self.vnodes = vnodes
        self._ring = {}
        self._sorted = []

    @staticmethod
    def _hash(s):
        return int.from_bytes(hashlib.md5(s.encode()).digest()[:8], "big")

    def add_node(self, name):
        for i in range(self.vnodes):
            pos = self._hash(f"{name}#{i}")
            self._ring[pos] = name
            bisect.insort(self._sorted, pos)

    def get_node(self, key):
        if not self._sorted:
            return None
        i = bisect.bisect_right(self._sorted, self._hash(key))
        if i == len(self._sorted):
            i = 0
        return self._ring[self._sorted[i]]


# buckets = [0] * 100
# step = 2 ** 64 // 100
# for i in range(100000):
#     buckets[min(ConsistentHash._hash(f"x-{i}") // step, 99)] += 1
# print(min(buckets), max(buckets)) # 934 1066


keys = [f"key-{i}" for i in range(100000)]

ch = ConsistentHash(vnodes=1)
for n in ["a", "b", "c"]:
    ch.add_node(n)

before = {k: ch.get_node(k) for k in keys}
ch.add_node("d")
moved = sum(1 for k in keys if ch.get_node(k) != before[k])
print(moved / len(keys))