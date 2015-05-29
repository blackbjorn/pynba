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


cdef class LocalStack(object):
    cdef dict stacked
    cdef object indent_func

    def __cinit__(self):
        self.stacked = {}
        self.indent_func = get_ident

    property indent:
        def __get__(self):
            return self.indent_func()

    property pynba:
        def __get__(self):
            return self.stacked.get(self.indent, None)

        def __set__(self, pynba):
            self.stacked[self.indent] = pynba

        def __del__(self):
            try:
                del self.stacked[self.indent]
            except KeyError:
                pass

LOCAL_STACK = LocalStack()
