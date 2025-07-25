#!/usr/bin/env python3
"""Implement an expiring web cache and tracker"""

import redis
import requests
from functools import wraps

r = redis.Redis()


def count_access(method):
    """Decorator to count how many times a URL is accessed"""
    @wraps(method)
    def wrapper(url):
        key = f"count:{url}"
        r.incr(key)
        return method(url)
    return wrapper


@count_access
def get_page(url: str) -> str:
    """Get a page and cache its response for 10 seconds"""
    cached = r.get(url)
    if cached:
        return cached.decode('utf-8')

    # If not cached, make a request
    response = requests.get(url)
    r.setex(url, 10, response.text)  # Cache for 10 seconds
    return response.text
