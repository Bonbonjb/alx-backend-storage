#!/usr/bin/env python3
"""
Implements an expiring web cache and request counter using Redis.
"""

import redis
import requests
from typing import Callable
from functools import wraps

# Redis client
r = redis.Redis()


def count_url_access(method: Callable) -> Callable:
    """
    Decorator that tracks how many times a URL was accessed.
    Stores the count in Redis with key 'count:{url}'.
    """
    @wraps(method)
    def wrapper(url: str) -> str:
        r.incr(f"count:{url}")
        return method(url)
    return wrapper


@count_url_access
def get_page(url: str) -> str:
    """
    Fetches the HTML content of a URL.
    Caches it in Redis for 10 seconds with key 'cache:{url}'.

    Args:
        url (str): URL to fetch.

    Returns:
        str: HTML content.
    """
    cache_key = f"cache:{url}"
    cached = r.get(cache_key)

    if cached:
        return cached.decode("utf-8")

    response = requests.get(url)
    content = response.text

    r.setex(cache_key, 10, content)
    return content
