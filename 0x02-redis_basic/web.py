#!/usr/bin/env python3
"""
Module that implements an expiring web cache and access counter using Redis.
"""

import redis
import requests
from functools import wraps
from typing import Callable

# Redis client
r = redis.Redis()


def count_url_access(method: Callable) -> Callable:
    """
    Decorator that tracks how many times a URL is accessed.
    Uses Redis key 'count:{url}'.
    """
    @wraps(method)
    def wrapper(url: str) -> str:
        r.incr(f"count:{url}")
        return method(url)
    return wrapper


@count_url_access
def get_page(url: str) -> str:
    """
    Fetches the content of a URL or returns cached version if available.
    Caches the response content in Redis with a 10-second expiration.

    Args:
        url (str): URL to fetch.

    Returns:
        str: HTML content of the page.
    """
    cache_key = f"cache:{url}"
    cached = r.get(cache_key)

    if cached:
        return cached.decode('utf-8')

    response = requests.get(url)
    content = response.text

    r.setex(cache_key, 10, content)
    return content
