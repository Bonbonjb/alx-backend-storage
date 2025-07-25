#!/usr/bin/env python3
"""Module for a simple Redis-backed Cache class using redis-py."""

import redis
import uuid
from typing import Union, Optional, Callable
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """
    Decorator that counts how many times a method is called.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """
    Decorator to store the history of inputs
    and outputs for a function in Redis.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        input_key = f"{method.__qualname__}:inputs"
        output_key = f"{method.__qualname__}:outputs"

        # Store input arguments as a string
        self._redis.rpush(input_key, str(args))

        # Call the actual method and store output
        result = method(self, *args, **kwargs)
        self._redis.rpush(output_key, str(result))

        return result

    return wrapper


class Cache:
    """
    Cache class for storing and retrieving data
    from Redis, with history tracking..
    """

    def __init__(self) -> None:
        """Initialize the Cache instance with a clean Redis database."""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Store data in Redis and return the generated key"""
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(
        self,
        key: str,
        fn: Optional[Callable[[bytes],
                              Union[str, int, float, bytes]]] = None
    ) -> Union[str, int, float, bytes, None]:
        """
        Retrieve data from Redis by key, with optional conversion function.
        """
        data = self._redis.get(key)
        if data is None:
            return None
        if fn:
            return fn(data)
        return data

    def get_str(self, key: str) -> Union[str, None]:
        """
        Retrieve a UTF-8 decoded string from Redis.
        """
        return self.get(key, fn=lambda d: d.decode("utf-8") if d else None)

    def get_int(self, key: str) -> Union[int, None]:
        """
        Retrieve an integer from Redis.
        """
        return self.get(key, fn=lambda d: int(d) if d else None)


def replay(method: Callable) -> None:
    """
    Display the history of calls of a particular
    function for tracking purposes.
    """
    redis_instance = method.__self__._redis
    method_name = method.__qualname__

    inputs_key = f"{method_name}:inputs"
    outputs_key = f"{method_name}:outputs"

    inputs = redis_instance.lrange(inputs_key, 0, -1)
    outputs = redis_instance.lrange(outputs_key, 0, -1)

    print(f"{method_name} was called {len(inputs)} times:")

    for input_data, output_data in zip(inputs, outputs):
        input_args = input_data.decode("utf-8")
        output_value = output_data.decode("utf-8")
        print(f"{method_name}(*{input_args}) -> {output_value}")
