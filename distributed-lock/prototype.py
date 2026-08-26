import threading
import time
import uuid


class Store:
    def __init__(self):
        self._data = {}
        self._mu = threading.Lock()

    def _live(self, key):
        if key in self._data:
            value, expires_at = self._data[key]
            if expires_at > time.monotonic():
                return value
        return None

    def set_nx_px(self, key, value, ttl):
        with self._mu:
            if self._live(key) is not None:
                return False

            expires_at = time.monotonic() + ttl

            self._data[key] = (value, expires_at)
            return True

    def delete_if(self, key, value):
        with self._mu:
            current = self._live(key)
            if current == value:
                del self._data[key]
                return True
            else:
                return False

    def expire_if(self, key, value, ttl):
        with self._mu:
            current = self._live(key)
            if current == value:
                self._data[key] = (value, time.monotonic() + ttl)

                return True
            return False


class Lock:
    def __init__(self, store, key, ttl=10.0):
        self._store = store
        self._key = key
        self._ttl = ttl
        self._token = None

    def release(self):
        if self._token is None:
            return False
        ok = self._store.delete_if(self._key, self._token)
        self._token = None
        return ok

    def renew(self):
        if self._token is None:
            return False
        return self._store.expire_if(self._key, self._token, self._ttl)

    def acquire(self, blocking=True, timeout=None):
        token = uuid.uuid4().hex
        deadline = None if timeout is None else time.monotonic() + timeout
        while True:
            if self._store.set_nx_px(self._key, token, self._ttl):
                self._token = token
                return True
            if not blocking:
                return False
            if deadline is not None and time.monotonic() >= deadline:
                return False
            time.sleep(0.05)


if __name__ == "__main__":
    s = Store()
    print(s.set_nx_px("k", "a", 0.1))  # True - free
    print(s.set_nx_px("k", "b", 0.1))  # False - occupied
    time.sleep(0.15)
    print(s.set_nx_px("k", "b", 0.1))  # first call is dead - True then

    s = Store()
    s.set_nx_px("job", "a", 1.0)
    print(s.delete_if("job", "b"))  # False
    print(s.delete_if("job", "a"))  # True
    print(s.delete_if("job", "a"))  # False

    s = Store()
    s.set_nx_px("j", "a", 0.2)
    time.sleep(0.15)
    print(s.expire_if("j", "a", 5.0))  # true
    time.sleep(0.15)
    print(s.set_nx_px("j", "b", 1.0))  # false

    s = Store()
    s.set_nx_px("j", "a", 0.1)
    print(s.expire_if("j", "a", 0.1))  # True
    print(s.expire_if("j", "b", 0.1))  # False

    s = Store()
    s.set_nx_px("j", "a", 0.1)
    time.sleep(0.15)
    print(s.expire_if("j", "a", 5.0))  # False
    print(s.set_nx_px("j", "b", 1.0))  # True

    s = Store()
    a = Lock(s, "job", ttl=1.0)
    b = Lock(s, "job", ttl=1.0)
    print(a.acquire())  # True
    print(b.acquire())  # False a is holding lock
    print(a.release())  # True
    print(b.acquire())  # True lock can be takken now

    s = Store()
    a = Lock(s, "job", ttl=0.3)
    b = Lock(s, "job", ttl=0.3)

    print(a.acquire())  # True
    print(b.acquire(blocking=False))  # False

    t = time.monotonic()
    print(b.acquire())  # True
    print(round(time.monotonic() - t, 2))  # ~0.3s
    s = Store()
    a = Lock(s, "job", ttl=5.0)
    b = Lock(s, "job", ttl=5.0)

    print(a.acquire())  # True
    t = time.monotonic()
    print(b.acquire(timeout=0.2))  # False
    print(round(time.monotonic() - t, 2))  # ~0.2s

    s = Store()
    lock = Lock(s, "job", ttl=5.0)

    print(lock.acquire())  # True
    print(lock.release())  # True
    print(lock.release())  # False
    print(lock.acquire())  # True

    s = Store()
    lock = Lock(s, "job", ttl=0.3)

    print(lock.renew())  # False — we hold nothing yet
    print(lock.acquire())  # True
    time.sleep(0.2)
    print(
        lock.renew()
    )  # True — made it before the TTL expired, the lease has been extended
    time.sleep(0.2)
    print(lock.renew())  # True
    time.sleep(0.4)
    print(lock.renew())  # False — missed the deadline, the lease has expired
    print(lock.release())  # False - nothing left to give
