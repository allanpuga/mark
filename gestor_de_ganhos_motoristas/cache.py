import time
import threading


class TTLCache:
    """A simple thread-safe in-memory TTL cache."""

    def __init__(self):
        self._cache: dict[
            str, tuple[str | int | float | bool | list | dict, float]
        ] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> str | int | float | bool | list | dict | None:
        with self._lock:
            if key not in self._cache:
                return None
            value, expiry = self._cache[key]
            if time.time() > expiry:
                del self._cache[key]
                return None
            return value

    def set(
        self,
        key: str,
        value: str | int | float | bool | list | dict,
        ttl_seconds: int,
    ):
        with self._lock:
            expiry = time.time() + ttl_seconds
            self._cache[key] = (value, expiry)

    def has(self, key: str) -> bool:
        return self.get(key) is not None


fipe_cache = TTLCache()