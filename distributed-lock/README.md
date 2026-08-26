# distributed-lock

My take on a distributed lock. It answers one question: "am I the only one doing this right now?"

A normal mutex works because everyone shares memory. Across machines there is no shared memory, so the lock has to live somewhere both sides can see - here a key in a store. Taking the lock means writing your name into that key, but only if nobody wrote there first. That is one atomic operation, `SET key value NX PX ttl`, and the whole thing is built on it.

The hard part is not taking the lock, it is what happens when the holder dies. Nobody will come and release it for you, so the key must expire by itself. That is the TTL. It turns ownership into a **lease**: the lock is yours for N seconds, not until you say otherwise. Die, and it comes back on its own.

But now the lease can run out while you are still working - a long GC pause is enough. Someone else takes the key, you wake up and call `release()`, and you delete *their* lock. That is why the value is a random token and not `1`. Release is not "delete the key", it is "delete the key **if it still holds my token**". Same for renewal.

The token belongs to the lease, not to the `Lock` object. It is born in `acquire()` and dies in `release()`. I had it in `__init__` at first and that quietly broke everything: one object reused for two acquisitions has one token, so a stale second `release()` matches the key of a completely different holder and kills it. No error, no warning, two workers inside the critical section.

`Store` here is a fake Redis - a dict with expiry and a mutex. `set_nx_px` is `SET NX PX`. `delete_if` and `expire_if` are compare-and-swap; in real Redis they are not commands at all, you send them as a small Lua script so the read and the write stay atomic.

## Usage

```python
from prototype import Store, Lock

store = Store()
lock = Lock(store, "job:42", ttl=10.0)

if lock.acquire(timeout=5.0):     # wait up to 5s, then give up
    try:
        ...                       # only one worker gets here
        lock.renew()              # work is slow? push the lease
    finally:
        lock.release()
```

`acquire()` has three modes. `blocking=False` tries once and answers immediately. `timeout=N` spins until the deadline. Default is spin forever, which is the one I would not put in production.

All three methods return a bool and never raise. `release()` returning `False` is not a failure to release - it means the lease was already gone.

## Notes for myself

- All timing is `time.monotonic()`. Wall clock can jump backwards on an NTP sync and then a TTL means nothing.
- The deadline is counted once before the loop instead of checking elapsed time inside. Same result, but a deadline is a point in time, so I can pass it further down later.
- `timeout` is "at least". The loop sleeps 50ms, so I usually overshoot by up to that much. `sleep(min(0.05, deadline - now))` fixes it, but `deadline` can be `None` so I left it.
- Fixed sleep also means all waiters wake up at the same moment and hit the store together. Random jitter would be better.
- Lost time on a bug where I passed `self._token` (still `None`) instead of the local `token`. The store uses `None` for "no key", so a taken key looked free. Do not use a real value as a sentinel.
- `renew()` does not drop the token when it fails. Over a network a failed renew might have actually worked and only the reply got lost - dropping the token would leave me with a lock I own and cannot release.
- No fencing here. The token stops me from deleting someone else's key, but two workers can still both think they hold the lock if one freezes at a bad moment. The real fix is a number that grows on every acquire and gets checked by the storage you are protecting.
