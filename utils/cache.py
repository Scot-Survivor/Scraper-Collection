"""
 Simple modular Cache system, each module can store values in a Key->Value cache with a specified TTL,
 schedule runs every 5 seconds to check for expired keys and remove them.
 Keys are stored such that module-key is the key in the cache, this allows for multiple modules to store
    keys with the same name without conflict.
"""
import logging
import threading
import time
import os
import json

from typing import Any, Dict
from utils.misc import get_calling_filename


if not os.path.exists("./.cache"):
    os.makedirs("./.cache")


class TTL:
    """
    Multipliers for TTL values
    """
    SECONDS = 1
    MINUTES = 60
    HOURS = 60 * 60
    DAYS = 60 * 60 * 24


class Cache:
    """Singleton Cache class"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Cache, cls).__new__(cls)
            cls._instance.cache = {}
            cls._instance.cache_lock = threading.Lock()
            cls._instance.cache_thread = threading.Thread(target=cls._instance._cache_thread)
            cls._instance.cache_thread.daemon = True
            cls._instance.cache_thread.start()
            cls._instance.read_cache()
        return cls._instance

    def write_cache(self):
        with open("./.cache/cache.json", "w") as f:
            json.dump(self.cache, f)
        f.close()
        logging.debug("Cache written to disk")

    def read_cache(self):
        try:
            with open("./.cache/cache.json", "r") as f:
                self.cache = json.load(f)
            f.close()
            logging.debug("Cache read from disk")
        except FileNotFoundError:
            logging.debug("No cache file found")

    def _cache_thread(self):
        while True:
            time.sleep(5)
            with self.cache_lock:
                for key in list(self.cache.keys()):
                    if self.cache[key]['ttl'] < time.time():
                        logging.debug(f"Removing expired key: {key}")
                        del self.cache[key]

    def set(self, key: str, value: Any, ttl: int = 60):
        """Set a value in the cache

        Args:
            key (str): Key to store the value under
            value (Any): Value to store
            ttl (int, optional): Time in seconds before the key expires. Defaults to 60.
        """
        calling_filename = get_calling_filename()
        key = f"{calling_filename}-{key}"
        with self.cache_lock:
            self.cache[key] = {'value': value, 'ttl': time.time() + ttl}

    def get(self, key: str) -> Any:
        """Get a value from the cache

        Args:
            key (str): Key to get the value for

        Returns:
            Any: Value stored in the cache
        """
        logging.debug(f"Getting key: {key}")
        calling_filename = get_calling_filename()
        key = f"{calling_filename}-{key}"
        with self.cache_lock:
            if key in self.cache:
                return self.cache[key]['value']
        return None

    def remove(self, key: str):
        """Remove a key from the cache

        Args:
            key (str): Key to remove
        """
        logging.debug(f"Removing key: {key}")
        calling_filename = get_calling_filename()
        key = f"{calling_filename}-{key}"
        with self.cache_lock:
            if key in self.cache:
                del self.cache[key]

    def clear(self):
        """Clear the cache for give module"""
        logging.debug("Clearing cache")
        with self.cache_lock:
            calling_filename = get_calling_filename()
            keys = [key for key in self.cache.keys() if key.startswith(calling_filename)]
            for key in keys:
                del self.cache[key]

    def get_all(self) -> Dict[str, Any]:
        """Get all keys and values from the cache for module

        Returns:
            Dict[str, Any]: All keys and values in the cache
        """
        logging.debug("Getting all keys")
        with self.cache_lock:
            calling_filename = get_calling_filename()
            keys = {key: self.cache[key]['value'] for key in self.cache.keys() if key.startswith(calling_filename)}
        return {key.split("-")[1]: value for key, value in keys.items()}

    def exists(self, key: str) -> bool:
        """Check if a key exists in the cache

        Args:
            key (str): Key to check

        Returns:
            bool: True if key exists, False otherwise
        """
        calling_filename = get_calling_filename()
        key = f"{calling_filename}-{key}"
        with self.cache_lock:
            return key in self.cache
