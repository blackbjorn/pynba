"""
    Pynba
    ~~~~~

    :copyright: (c) 2015 by Xavier Barbosa.
    :license: MIT, see LICENSE for more details.
"""

from __future__ import absolute_import, unicode_literals

try:
    from greenlet import getcurrent as get_ident
except ImportError:
    try:
        from six.moves._thread import get_ident
    except ImportError:
        def get_ident():
            """Dummy implementation of thread.get_ident().

            Since this module should only be used when threadmodule is not
            available, it is safe to assume that the current process is the
            only thread.  Thus a constant can be safely returned.
            """
            return -1

__all__ = ['LocalStack', 'LOCAL_STACK']


class LocalStack(object):

    def __init__(self):
        self.stacked = {}
        self.indent_func = get_ident

    @property
    def indent(self):
        return self.indent_func()

    @property
    def pynba(self):
        return self.stacked.get(self.indent, None)

    @pynba.setter
    def pynba(self, pynba):
        self.stacked[self.indent] = pynba

    @pynba.deleter
    def pynba(self):
        try:
            del self.stacked[self.indent]
        except KeyError:
            pass

LOCAL_STACK = LocalStack()
