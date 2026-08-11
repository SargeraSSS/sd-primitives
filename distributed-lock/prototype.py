import threading
import time


class Store:
    def __init__(self):
        self._data = {}
        self._mu = threading.Lock()

    def _live(self, key):
        if key in self._data:
            value, expires_at = self._data[key]
            if expires_at > time.monotonic():
                return value
            else:
                del self._data[key]
        return None

    def set_nx_px(self, key, value, ttl):
        with self._mu:
            if self._live(key) is not None:
                return False

            expires_at = time.monotonic() + ttl

            self._data[key] = (value, expires_at)
            return True


if __name__ == "__main__":
    s = Store()
    print(s.set_nx_px("k", "a", 0.1))  # True - free
    print(s.set_nx_px("k", "b", 0.1))  # False - occupied
    time.sleep(0.15)
    print(s.set_nx_px("k", "b", 0.1))  # first call is dead - True then
