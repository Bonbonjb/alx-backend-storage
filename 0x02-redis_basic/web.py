#!/usr/bin/env python3
"""
Module that implements an expiring web cache and access counter using Redis.
"""

import redis
import requests
from functools import wraps
from typing import Callable

# Connect to Redis
r = redis.Redis()


def count_url_access(method: Callable) -> Callable:
    """
    Decorator to track how many times a URL is accessed.
    Increments Redis key 'count:{url}'.
    """
    @wraps(method)
    def wrapper(url: str) -> str:
        r.incr(f"count:{url}")
        return method(url)
    return wrapper


@count_url_access
def get_page(url: str) -> str:
    """
    Returns HTML content of a URL.
    Caches result in Redis for 10 seconds.

    Args:
        url: Web URL to retrieve.

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
