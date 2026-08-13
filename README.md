# sd-primitives

This repository exists to showcase system design primitives — the basic building blocks of distributed systems, implemented from scratch for learning purposes.

## Projects

### [bloom-filter](./bloom-filter)
A probabilistic set-membership structure. It can return false positives but never false negatives, saving memory and unnecessary trips to storage.

### [consistent-hashing](./consistent-hashing)
Key distribution across nodes using a hash ring with virtual nodes. Adding or removing a node remaps only a small fraction of the keys.


### [distributed-lock](./distributed-lock)
Mutual exclusion across processes on different machines: lock acquisition with a TTL, lease renewal, and safe owner-only release.


## TODO
### [wal](./wal)
Write-Ahead Log — an append-only journal written to disk before changes are applied. The foundation of durability and crash recovery.

## License

[MIT](./LICENSE)
