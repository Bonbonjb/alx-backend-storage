#!/usr/bin/env python3
"""
A module that defines a Cache class for storing and retrieving data using Redis.
"""
import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """
    Decorator that counts how many times a method is called.
    Stores the count in Redis using the method's qualified name.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        key = method.__qualname__  # ✅ must be from the method
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper

class Cache:
    """
    Cache class for interacting with Redis to store and retrieve data.
    """

    def __init__(self):
        """Initialize Redis client and flush the database."""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store the given data in Redis with a random key.

        Args:
            data: The data to store. Can be str, bytes, int, or float.

        Returns:
            A unique key as a string.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key


    def get(self, key: str, fn: Optional[Callable] = None) -> Union[str, bytes, int, float, None]:
        """
        Retrieve data from Redis and optionally convert it using a callable.

        Args:
            key: The key under which the data is stored.
            fn: Optional callable used to convert the data back to original format.

        Returns:
            The data, possibly converted using fn, or None if key doesn't exist.
        """
        data = self._redis.get(key)
        if data is None:
            return None
        return fn(data) if fn else data

    def get_str(self, key: str) -> Optional[str]:
        """
        Retrieve a UTF-8 string from Redis.

        Args:
            key: The key to retrieve.

        Returns:
            The decoded string, or None if key does not exist.
        """
        return self.get(key, fn=lambda d: d.decode("utf-8"))

    def get_int(self, key: str) -> Optional[int]:
        """
        Retrieve an integer from Redis.

        Args:
            key: The key to retrieve.

        Returns:
            The integer value, or None if key does not exist.
        """
        return self.get(key, fn=int)
