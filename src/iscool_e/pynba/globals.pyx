# -*- coding: utf-8 -*-
"""
    IsCool-e Pynba
    ~~~~~~~~~~~~~~

    :copyright: (c) 2012 by IsCool Entertainment.
    :license: MIT, see LICENSE for more details.
"""

from functools import wraps
from .local import LOCAL_STACK

__all__ = ['pynba']

cdef class LocalProxy(object):
    def timer(self, **tags):
        pynba = LOCAL_STACK.pynba
        if pynba:
            return pynba.timer(**tags)

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    timer = LOCAL_STACK.pynba.timer(**tags)
                except (TypeError, AttributeError):
                    raise RuntimeError('working outside of request context')

                with timer:
                    response = func(*args, **kwargs)
                return response
            return wrapper
        return decorator

    def __getattr__(self, name):
        try:
            return getattr(LOCAL_STACK.pynba, name)
        except TypeError:
            raise RuntimeError('working outside of request context')

    def __setattr__(self, name, value):
        try:
            setattr(LOCAL_STACK.pynba, name, value)
        except TypeError:
            raise RuntimeError('working outside of request context')

    def __delattr__(self, name):
        try:
            delattr(LOCAL_STACK.pynba, name)
        except TypeError:
            raise RuntimeError('working outside of request context')

pynba = LocalProxy()
