#!/usr/bin/env python3
"""
Main file to test replay only
"""

from exercise import Cache, replay

cache = Cache()
cache._redis.flushdb() 

cache.store("foo")
cache.store("bar")
cache.store(42)

replay(cache.store)

