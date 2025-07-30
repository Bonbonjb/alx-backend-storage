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
        count_key = f"count:{url}"
        try:
            r.incr(count_key)
        except Exception as e:
            print(f"Failed to increment counter for {url}: {e}")
        return method(url)
    return wrapper


@count_url_access
def get_page(url: str) -> str:
    """
    Retrieves HTML content of a URL using requests.
    Caches result in Redis with key 'cache:{url}' and TTL 10 seconds.
    """
    cache_key = f"cache:{url}"
    cached_content = r.get(cache_key)

    if cached_content:
        return cached_content.decode("utf-8")

    # Not cached; fetch and store
    response = requests.get(url)
    content = response.text

    # Store with expiration (10 seconds)
    try:
        r.setex(cache_key, 10, content)
    except Exception as e:
        print(f"Failed to cache page for {url}: {e}")

    return content
    
>>> from web import get_page, r
>>> get_page("http://slowwly.robertomurray.co.uk/delay/3000/url/http://www.google.com")
>>> r.get("cache:http://slowwly.robertomurray.co.uk/delay/3000/url/http://www.google.com") is not None
# Wait 10 seconds
>>> r.get("cache:http://slowwly.robertomurray.co.uk/delay/3000/url/http://www.google.com") is None
>>> r.get("count:http://slowwly.robertomurray.co.uk/delay/3000/url/http://www.google.com")
