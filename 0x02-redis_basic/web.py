#!/usr/bin/env python3
"""
Module for caching and tracking web page access using Redis.
"""

import redis
import requests
from typing import Callable
from functools import wraps

# Initialize Redis connection
r = redis.Redis()


def count_url_access(method: Callable) -> Callable:
    """
    Decorator to count how many times a URL is accessed.
    Stores the count in Redis under key 'count:{url}'.
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
    Retrieves the content of a web page. If the content is cached in Redis,
    it returns the cached version. Otherwise, it fetches the page and caches it
    with a 10-second expiration.
    
    Args:
        url (str): The URL of the web page to fetch.
    
    Returns:
        str: HTML content of the page.
    """
    cache_key = f"cache:{url}"
    cached = r.get(cache_key)

    if cached:
        return cached.decode('utf-8')

    # Fetch from the web and cache it
    response = requests.get(url)
    content = response.text

    r.setex(cache_key, 10, content)  # Cache for 10 seconds
    return content
