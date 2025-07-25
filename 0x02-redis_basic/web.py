#!/usr/bin/env python3
"""
Module that implements an expiring web cache and request counter using Redis.
"""

import redis
import requests
from functools import wraps
from typing import Callable

# Redis client (assumes Redis is running locally)
r = redis.Redis()


def count_url_access(method: Callable) -> Callable:
    """
    Decorator that counts how many times a URL is accessed.
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
    Retrieves HTML content of a URL using requests.
    Caches result in Redis with key 'cache:{url}' and TTL 10 seconds.

    Args:
        url (str): The web page URL.

    Returns:
        str: HTML content of the page.
    """
    cache_key = f"cache:{url}"
    cached = r.get(cache_key)
    if cached:
        return cached.decode('utf-8')

    # Not cached; fetch, store and return
    response = requests.get(url)
    content = response.text
    r.setex(cache_key, 10, content)
    return content
