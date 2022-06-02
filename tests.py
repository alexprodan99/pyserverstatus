import pytest
from pyserverstatus import is_running

def test_is_running():
    assert(is_running("google.com", 80))
    assert(is_running("google.com", 443))
    assert(is_running("facebook.com", 443))
    assert(is_running("facebook.com", 443))
    assert(is_running("gog.com", 80))
    assert(is_running("gog.com", 443))

def test_is_not_running():
    assert(not is_running("superlongstringsuperlongstringsuperlongstringsuperlongstringsuperlongstringsuperlongstringsuperlongstring.com", 80))
    assert(not is_running("superlongstringsuperlongstringsuperlongstringsuperlongstringsuperlongstringsuperlongstringsuperlongstring.com", 443))
