"""
    Pynba
    ~~~~~

    :copyright: (c) 2015 by Xavier Barbosa.
    :license: MIT, see LICENSE for more details.
"""

from __future__ import absolute_import, unicode_literals

__all__ = ['monitor', 'pynba', 'PynbaMiddleware', 'RequestContext']

from .ctx import RequestContext
from .middleware import PynbaMiddleware
from pynba.stacked import LocalProxy

pynba = LocalProxy(enabled=False)


def monitor(address, **config):
    """Simple decorator for WSGI app.
    Parameters will be directly passed to the :class:`PynbaMiddleware`
    """
    def wrapper(func):
        return PynbaMiddleware(func, address, **config)
    return wrapper
