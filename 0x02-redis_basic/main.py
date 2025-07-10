#!/usr/bin/env python3
"""
Main file to test Cache class.
"""
import redis

Cache = __import__('exercise').Cache

cache = Cache()

cache.store(b"first")
print(cache.get(cache.store.__qualname__))

cache.store(b"second")
cache.store(b"third")
print(cache.get(cache.store.__qualname__))

data = b"hello"
key = cache.store(data)
print(key)

local_redis = redis.Redis()
print(local_redis.get(key))

TEST_CASES = {
    b"foo": None,
    123: int,
    "bar": lambda d: d.decode("utf-8")
}

for value, fn in TEST_CASES.items():
    key = cache.store(value)
    assert cache.get(key, fn=fn) == value
