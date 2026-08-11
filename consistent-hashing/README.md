# consistent-hashing

My take on a hash ring. It answers one question: "which node owns this key?"

The obvious way is `hash(key) % N`. Fine until N changes - add one node and almost every key lands somewhere else, so the whole cache goes cold at once.

The ring fixes that. Hash keys and nodes into the same 64-bit space, bend it into a circle, and a key belongs to the first node clockwise from it. Now dropping a node only orphans the keys that pointed at it. Everybody else doesn't even notice, because their walk around the ring is unchanged.

Each node is placed 200 times, not once. These are virtual nodes. With one point per node the arcs come out wildly uneven, and when a node dies its entire load falls on one neighbour. With 200 the arcs interleave, so the load is even and the orphans spread out.

## Usage

```python
from prototype import ConsistentHash

ch = ConsistentHash(vnodes=200)
for n in ["a", "b", "c"]:
    ch.add_node(n)

ch.get_node("key-42")   # "c"
ch.remove_node("c")
ch.get_node("key-42")   # "a" - moved, because its owner is gone
```

## Notes for myself

- md5 cut to 8 bytes gives the ring position. Not for security, it just has to spread evenly.
- `_sorted` holds the positions in order, lookup is `bisect_right` and wrap to 0 at the end. O(log n).
- From my own runs on 100k keys: adding a 4th node moved 3.7% of them. Removing a node moved exactly its own 27448 keys and not a single other one.
- `vnodes=1` gave `{a: 72723, c: 17156, b: 6379, d: 3742}`. `vnodes=200` gave 21-27k each. That is the whole argument for virtual nodes.
- Removing a node that was never added raises `KeyError`. Fine for now.
- Redis Cluster does not use a ring, it has 16384 fixed hash slots. The ring is more of a memcached/ketama thing.
