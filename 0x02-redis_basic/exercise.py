#!/usr/bin/env python3
"""
A module that defines a Cache class for storing data in Redis.
"""
import redis
import uuid
from typing import Union


class Cache:
    """
    Cache class for interacting with Redis to store and retrieve data.
    """

    def __init__(self):
        """Initialize Redis client and flush the database."""
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store the given data in Redis with a random key.

        Args:
            data (Union[str, bytes, int, float]): Data to store in Redis.

        Returns:
            str: The key under which the data is stored.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key
