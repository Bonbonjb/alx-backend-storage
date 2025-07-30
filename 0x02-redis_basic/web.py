#!/usr/bin/env python3
"""
Module that implements an expiring web cache and request counter using Redis.
"""

import redis
import requests
from functools import wraps
from typing import Callable

# Redis client
r = redis.Redis()


def count_url_access(method: Callable) -> Callable:
    """
    Decorator to count how many times a URL is accessed.
    Uses Redis key 'count:{url}'.
    """
    @wraps(method)
    def wrapper(url: str) -> str:
        count_key = f"count:{url}"
        r.incr(count_key)
        return method(url)
    return wrapper


@count_url_access
def get_page(url: str) -> str:
    """
    Gets HTML content of a URL. Caches it for 10 seconds.
    Returns:
        - Cached content if available.
        - "OK" if fetched and cached.
    """
    cache_key = f"cache:{url}"
    cached = r.get(cache_key)

    if cached:
        return cached.decode('utf-8')

    # Cache miss, fetch page
    response = requests.get(url)
    r.setex(cache_key, 10, response.text)
    return "OK"
